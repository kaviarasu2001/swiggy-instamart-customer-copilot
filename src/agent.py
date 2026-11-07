
import json
import mock_llm
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.policy_rag import retrieve

PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_DIR / "data" / "instamart.db"
OUTPUT_DIR = PROJECT_DIR / "outputs"
LEDGER_PATH = OUTPUT_DIR / "refund_ledger.jsonl"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_order(order_id):
    """Read an order from the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        row = conn.execute(
            """
            SELECT order_id, status, order_amount, delivery_minutes
            FROM orders
            WHERE order_id = ?
            """,
            (order_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return {"error": "order not found"}

    return {
        "order_id": row["order_id"],
        "status": row["status"],
        "order_amount": float(row["order_amount"]),
        "delivery_minutes": (
            None if row["delivery_minutes"] is None
            else float(row["delivery_minutes"])
        )
    }


def search_policy(query):
    """Retrieve relevant policy chunks."""
    return {"results": retrieve(query, k=3)}


def calculate_refund(order_amount, delivery_minutes):
    """Calculate the refund under the delivery refund rules."""
    if delivery_minutes is None or float(delivery_minutes) <= 45:
        amount = 0.0
    else:
        amount = float(order_amount)

    return {"refund_inr": round(amount, 2)}


def _record_ledger(tool_name, order_id, refund_inr):
    """Append an issued or escalated action to the JSONL ledger."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "order_id": order_id,
        "refund_inr": round(float(refund_inr), 2)
    }

    with open(LEDGER_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")

    return {"refund_inr": round(float(refund_inr), 2)}


def issue_refund(order_id, refund_inr):
    """Record an automatically issued refund."""
    return _record_ledger("issue_refund", order_id, refund_inr)


def escalate_to_human(order_id, refund_inr):
    """Record a refund escalated to a human support lead."""
    return _record_ledger("escalate_to_human", order_id, refund_inr)


TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Look up an order by its order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Search the company policy documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_refund",
            "description": "Calculate an eligible refund amount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_amount": {"type": "number"},
                    "delivery_minutes": {
                        "type": ["number", "null"]
                    }
                },
                "required": ["order_amount", "delivery_minutes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Record an automatically issued refund.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "refund_inr": {"type": "number"}
                },
                "required": ["order_id", "refund_inr"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate a refund to a human support lead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "refund_inr": {"type": "number"}
                },
                "required": ["order_id", "refund_inr"]
            }
        }
    }
]


TOOL_MAP = {
    "get_order": get_order,
    "search_policy": search_policy,
    "calculate_refund": calculate_refund,
    "issue_refund": issue_refund,
    "escalate_to_human": escalate_to_human
}


import time

STATE_DIR = PROJECT_DIR / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)


def _checkpoint_path(run_id):
    return STATE_DIR / f"{run_id}.json"


def _save_checkpoint(state):
    with open(_checkpoint_path(state["run_id"]), "w",
              encoding="utf-8") as file:
        json.dump(state, file, indent=2)


def _fallback(status, state, reason):
    summary = ", ".join(state["tools_executed"]) or "No tools executed"
    return {
        "status": status,
        "final_answer": (
            f"{status}: {reason} "
            f"Human handoff summary: {summary}."
        ),
        "steps": state["steps"],
        "llm_calls": state["llm_calls"],
        "tokens_used": state["tokens_used"]
    }


def _continue_agent(state, max_iterations, token_limit,
                    time_limit_seconds, crash_after_tools=None):
    start_time = time.monotonic()

    while state["llm_calls"] < max_iterations:

        if time.monotonic() - start_time >= time_limit_seconds:
            return _fallback(
                "FALLBACK_TIMEOUT", state,
                "The time limit was reached."
            )

        response = mock_llm.chat(state["messages"], tools=TOOLS_SPEC)

        state["llm_calls"] += 1
        state["tokens_used"] += response.usage.total_tokens

        if state["tokens_used"] > token_limit:
            return _fallback(
                "FALLBACK_TOKEN_LIMIT", state,
                "The token limit was exceeded before executing the requested tool."
            )

        message = response.choices[0].message
        tool_calls = message.tool_calls

        if not tool_calls:
            answer = message.content or "No final answer returned."
            status = answer.split(":", 1)[0].strip().upper()

            return {
                "status": status,
                "final_answer": answer,
                "steps": state["steps"],
                "llm_calls": state["llm_calls"],
                "tokens_used": state["tokens_used"]
            }

        assistant_calls = [
            {
                "id": call.id,
                "name": call.name,
                "arguments": call.arguments
            }
            for call in tool_calls
        ]

        state["messages"].append({
            "role": "assistant",
            "content": None,
            "tool_calls": assistant_calls
        })

        for call in tool_calls:
            tool_name = call.name
            arguments = call.arguments

            if tool_name not in TOOL_MAP:
                observation = {"error": "unknown tool"}
            else:
                try:
                    observation = TOOL_MAP[tool_name](**arguments)
                except Exception as error:
                    observation = {"error": str(error)}

            state["tools_executed"].append(tool_name)

            state["steps"].append({
                "tool": tool_name,
                "arguments": arguments,
                "observation": observation
            })

            state["messages"].append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": tool_name,
                "content": json.dumps(observation)
            })

            state["step_number"] += 1

            # Persist immediately after each tool observation.
            _save_checkpoint(state)

            if (
                crash_after_tools is not None
                and state["step_number"] >= crash_after_tools
            ):
                return {
                    "status": "CRASH_SIMULATED",
                    "final_answer": "Simulated crash after checkpoint.",
                    "steps": state["steps"],
                    "llm_calls": state["llm_calls"],
                    "tokens_used": state["tokens_used"]
                }

    return _fallback(
        "FALLBACK_MAX_ITERATIONS",
        state,
        "The maximum number of model iterations was reached."
    )


def run_agent(user_message, scenario_id, max_iterations=6,
              token_limit=6000, time_limit_seconds=10,
              crash_after_tools=None):

    state = {
        "run_id": str(scenario_id),
        "scenario_id": scenario_id,
        "messages": [
            {
                "role": "system",
                "content": (
                    "AGENT\n"
                    "You are an Instamart refund assistant. "
                    "Use the available tools and follow company refund policy."
                )
            },
            {"role": "user", "content": user_message}
        ],
        "tokens_used": 0,
        "llm_calls": 0,
        "step_number": 0,
        "tools_executed": [],
        "steps": []
    }

    return _continue_agent(
        state, max_iterations, token_limit,
        time_limit_seconds, crash_after_tools
    )


def resume_agent(run_id, max_iterations=6,
                 token_limit=6000, time_limit_seconds=10):

    path = _checkpoint_path(str(run_id))

    if not path.exists():
        raise FileNotFoundError(f"No checkpoint found: {run_id}")

    with open(path, "r", encoding="utf-8") as file:
        state = json.load(file)

    return _continue_agent(
        state, max_iterations, token_limit, time_limit_seconds
    )
