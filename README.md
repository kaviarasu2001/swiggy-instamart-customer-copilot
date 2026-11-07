# Overview

## Swiggy Instamart Customer Intelligence Support Co-Pilot

An academic customer intelligence and support automation project built using Python, Pandas, NumPy, Scikit-learn, SQLite, TF-IDF retrieval, and an offline mock LLM.

The project contains four parts:
- Part A: Data cleaning, SQLite storage, and SQL analysis.
- Part B: RFM segmentation, PCA, and lapse prediction.
- Part C: Support ticket classification, PII redaction, and routing.
- Part D: Policy retrieval, refund decisions, and a resumable agent.

All records are synthetic. The supplied mock_llm.py simulates LLM responses. No paid API or external LLM service is used.

## Technologies

Python, Pandas, NumPy, Scikit-learn, SQLite, TF-IDF, cosine similarity, K-Means, PCA, Logistic Regression, Random Forest, and Joblib.

# Reproduce

## Requirements

Python 3.10 or later is recommended.

Install dependencies:

    python -m pip install -r requirements.txt

Verify the submitted project:

    python verify_project.py

The verification script checks required files, cleaned dataset dimensions, SQLite row counts and revenue, output row counts, policy evaluation inputs, and agent-run records.

The successful verification result was 36/36 checks passed.

Important: verification checks saved project artifacts. It does not regenerate every Part A-D result. generate_data.py creates raw synthetic datasets and policy documents; it is not a complete end-to-end pipeline runner.

# Part A

## Data Foundation: Clean, Store, Query

### Data preparation

| Dataset | Raw rows | Clean rows | Columns |
|---|---:|---:|---:|
| Customers | 1,200 | 1,200 | 5 |
| Products | 40 | 40 | 4 |
| Orders | 13,084 | 12,309 | 9 |

The raw ticket dataset contains 164 records.

Customer cleaning standardized city and gender values, converted ages to numeric values, handled invalid ages, and imputed missing ages.

Order cleaning handled duplicates, non-final records, invalid amounts, and invalid delivery times.

Final order checks:
- Completed orders: 11,110
- Cancelled orders: 1,199
- Missing order amounts: 0
- Negative order amounts: 0
- Completed orders with missing delivery times: 0

### SQLite database

Database: data/instamart.db

| Table | Rows |
|---|---:|
| customers | 1,200 |
| products | 40 |
| orders | 12,309 |

Completed-order revenue: **INR 2,998,668.80**

### SQL analysis

sql/queries.sql includes queries for order status, completed revenue, category revenue, top customers, delivery time by category, monthly revenue, and customer order frequency.

Revenue by category:

| Category | Revenue (INR) |
|---|---:|
| Electronics | 1,219,248.10 |
| Grocery | 614,293.30 |
| Dairy | 531,938.95 |
| Snacks | 464,754.50 |
| Personal Care | 168,433.95 |

Database validation passed all eight checkpoints.

# Part B

## Customer Segmentation and Lapse Prediction

### RFM analysis

RFM analysis used completed orders and a reference date of 2025-10-01.

- Customers analyzed: 1,175
- Median recency: 19 days
- Average frequency: 9.46 orders
- Average monetary value: INR 2,552.06

### K-Means clustering

RFM features were standardized before applying K-Means. Values of K from 2 to 8 were evaluated using inertia and silhouette score.

- Selected clusters: K = 4
- Silhouette score: 0.5255

| Customer segment | Customers |
|---|---:|
| Occasional Customers | 436 |
| Premium Customers | 138 |
| Loyal Frequent Customers | 419 |
| At-Risk Customers | 182 |

PCA explained variance: component 1 = 0.634, component 2 = 0.218, total = 0.852.

### Lapse prediction

The lapse cohort contains customers with at least one completed order before 2025-09-01. A customer is labelled lapsed if they made no completed order during September 2025.

- Cohort size: 1,156
- Active customers: 713
- Lapsed customers: 443
- Lapse rate: 38.32%

A stratified 80/20 train-test split was used with random_state=42. Preprocessing was fitted on the training data.

| Model | CV F1 | Test accuracy | Test precision | Test recall | Test F1 |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.6506 | 0.7284 | 0.6444 | 0.6517 | 0.6480 |
| Random Forest | 0.6811 | 0.7371 | 0.6591 | 0.6517 | 0.6554 |

The Random Forest model was selected based on the official grid-search cross-validation F1 score.

Top Random Forest feature importances:

| Feature | Importance |
|---|---:|
| Frequency | 0.2796 |
| Monetary | 0.2712 |
| Recency | 0.1151 |
| Average delivery minutes | 0.0613 |
| Cancellation rate | 0.0523 |

### Class imbalance experiment

Random oversampling was applied only to the Logistic Regression training data. The test set remained unchanged.

| Metric | Original training data | Oversampled training data |
|---|---:|---:|
| Accuracy | 0.7284 | 0.7155 |
| Precision | 0.6444 | 0.5891 |
| Recall | 0.6517 | 0.8539 |
| F1 | 0.6480 | 0.6972 |

Oversampling improved recall and F1 but reduced precision. It identified more lapsed customers at the cost of additional false positives.

The selected Random Forest model is saved as outputs/lapse_model.joblib. Reloaded-model predictions matched the original predictions.

The retention shortlist contains ten premium customers ranked by predicted lapse probability. Premium membership was calculated using the full-window RFM data, so this shortlist is illustrative and is not fully leakage-free.


# Part C

## Support Ticket Triage with Guardrails

The ticket dataset contains 164 records. Before classification, the pipeline estimates token usage, redacts personal information, and checks input length.

### Input validation and privacy

- Total tickets: 164
- Eligible tickets: 156
- Empty tickets skipped: 4
- Over-400-token tickets flagged: 4

PII redaction counts:

| PII type | Replacements |
|---|---:|
| Email addresses | 55 |
| Phone numbers | 91 |
| Order IDs | 132 |
| Total replacements | 278 |

The redaction placeholders are [EMAIL], [PHONE], and [ORDER_ID].

### Zero-shot and few-shot comparison

| Metric | Zero-shot | Few-shot |
|---|---:|---:|
| Classification accuracy | 85.71% | 100.00% |
| Tokens used | 11,428 | 22,348 |
| Tokens per classified ticket | 77.74 | 152.03 |
| Classified tickets | 147 | 147 |
| Recovered transient failures | 19 | 19 |

Both runs processed the same 156 eligible tickets. Few-shot examples improved accuracy by 14.29 percentage points, with approximately 96% more token usage.

### Final classification and routing

| Result status | Tickets |
|---|---:|
| Classified JSON | 135 |
| Classified using keyword fallback | 12 |
| Invalid output | 9 |
| Flagged as too long | 4 |
| Skipped as empty | 4 |

Routing results:

| Route | Tickets |
|---|---:|
| support_queue | 102 |
| security_team | 34 |
| human_review | 17 |
| premium_desk | 11 |

Priority results: NORMAL = 119 and HIGH = 45.

The final few-shot output is saved in outputs/triage_results.csv.

### Token budget demonstration

The zero-shot budget demonstration used a token budget of 6,000. Actual usage reached 6,021 because the budget is checked before a model call, and the final call can exceed the remaining budget.

- Budget-exhausted tickets: 74
- JSON classifications: 72
- Keyword classifications: 6
- Invalid outputs: 4
- Empty tickets skipped: 4
- Long tickets flagged: 4

The budget demonstration is saved in outputs/triage_budget_demo.csv.


# Part D

## Policy RAG Assistant and Refund Agent

### Policy retrieval and evaluation

The policy assistant uses five policy documents covering delivery, escalation, payment, privacy, and refunds.

- Chunk size: 40 words
- Chunk overlap: 10 words
- Retrieval method: TF-IDF with cosine similarity
- Top retrieved chunks: 3

Evaluation results:

| Evaluation | Result |
|---|---:|
| Expected document retrieval | 12/12 |
| Expected fact retrieval | 12/12 |
| Unsupported-question fallback | 2/2 |

A zero-overlap experiment retrieved 12/12 expected documents but retrieved the expected facts in only 9/12 cases. This indicates that overlap improved the completeness of relevant policy context.

The evaluation results are saved in outputs/policy_rag_evaluation.csv.

### Refund agent and tools

The agent uses a ReAct-style tool loop and five tools:

1. get_order
2. search_policy
3. calculate_refund
4. issue_refund
5. escalate_to_human

Refund rules are based on the simulated policy: only completed orders qualify; orders delivered more than 45 minutes late qualify for a full refund; refunds above INR 1,000 require human approval.

### Seven scenario results

| Scenario | Result | Refund (INR) | Model calls | Tokens |
|---|---|---:|---:|---:|
| S1 | REFUND | 128.25 | 5 | 907 |
| S2 | REFUND | 135.00 | 5 | 907 |
| S3 | ESCALATE | 1,999.00 | 5 | 914 |
| S4 | DENIED | 0.00 | 4 | 625 |
| S5 | DENIED | 0.00 | 3 | 358 |
| S6 | NOT_FOUND | 0.00 | 2 | 94 |
| S7 | FALLBACK_MAX_ITERATIONS | 0.00 | 6 | 3,048 |

The seven scenario execution records are saved in outputs/agent_runs.jsonl. Refund and escalation tool actions are recorded in outputs/refund_ledger.jsonl.

### Crash and resume demonstration

Scenario S1 was interrupted after the second tool observation. The checkpoint was saved before the simulated crash.

After resuming, the agent completed the refund of INR 128.25. The combined execution used exactly these tools in order:

get_order -> search_policy -> calculate_refund -> issue_refund

No previously completed tool was repeated during resume. The checkpoint is stored in state/CRASH_S1.json.

### Safe-stop demonstrations

| Demonstration | Status | Model calls | Tokens | Executed tools |
|---|---|---:|---:|---:|
| Token limit | FALLBACK_TOKEN_LIMIT | 3 | 360 | 2 |
| Timeout | FALLBACK_TIMEOUT | 0 | 0 | 0 |
| Maximum iterations | FALLBACK_MAX_ITERATIONS | 6 | 3,048 | 6 |

Each fallback provides a human-handoff summary and preserves completed tool observations where applicable.

### ReAct versus plan-and-execute

ReAct was selected because it alternates model reasoning and tool execution, allowing the next action to depend on actual observations. The measured scenarios required between two and six model calls. For example, the missing-order scenario stopped after two calls, while the refund scenarios required five calls. A fixed plan could be efficient for predictable workflows, but it may need additional handling when an order is missing, cancelled, or requires escalation. ReAct is more suitable for this policy-driven support workflow because it can react to tool results and stop safely when limits are reached.

The agent uses the offline mock LLM and does not issue real payments or contact external services.


# Limitations and Next Steps

## Limitations

- The datasets are synthetic and do not represent actual Swiggy customer transactions.
- The LLM is an offline mock implementation; its behavior does not represent a production language model.
- Model evaluation uses a single stratified train-test split, so performance may vary across different splits.
- The premium retention shortlist uses full-window RFM segmentation and is illustrative rather than fully leakage-free.
- Refund and escalation actions are simulated through a local JSONL ledger. No real money is transferred.
- The verification script checks committed artifacts; it does not independently regenerate every Part A-D output from a clean checkout.

## Next steps

- Build a single reproducible pipeline that generates, cleans, evaluates, and saves all outputs from a clean checkout.
- Use time-based validation and leakage-free customer segmentation for retention targeting.
- Monitor classification quality, token usage, and routing performance on new data.
- Add stronger audit logging and human approval controls before any production refund workflow.
- Evaluate the system with real, appropriately anonymized data and approved production services.

