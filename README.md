
# Swiggy Instamart Customer Intelligence Support Co-Pilot

## Project Overview

The Swiggy Instamart Customer Intelligence Support Co-Pilot is an academic AI and Machine Learning project developed using Python, SQL, Machine Learning, Natural Language Processing (NLP), and Retrieval-Augmented Generation (RAG) techniques.

The project combines customer analytics, churn prediction, automated support ticket classification, and policy-based customer support into one integrated application.

## Project Objectives

- Analyze customer purchasing behavior.
- Segment customers using RFM analysis and K-Means clustering.
- Predict potential customer churn.
- Automatically classify customer support tickets.
- Route tickets to the appropriate support teams.
- Retrieve relevant policy information to assist customer support.

## Main Features

### 1. Customer Data Analysis
- Customer, order, and ticket data processing.
- Data cleaning and preprocessing.
- SQLite database integration.
- Exploratory Data Analysis (EDA).

### 2. Customer Segmentation
- Recency, Frequency, and Monetary (RFM) analysis.
- K-Means clustering.
- PCA dimensionality reduction.
- Silhouette score evaluation.

### 3. Customer Churn Prediction
- Logistic Regression classification.
- Churn-risk prediction using customer frequency and spending.
- Churn probability estimation.

### 4. Support Ticket Triage
- TF-IDF text feature extraction.
- Logistic Regression ticket classification.
- Automatic support-team assignment.

### 5. Policy-Based Customer Support
- Mock policy knowledge base.
- Policy document chunking.
- TF-IDF similarity-based retrieval.
- Template-based mock response generation.
- Human-support escalation guidance.

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- SQLite
- SQLAlchemy
- Joblib
- TF-IDF
- Logistic Regression
- K-Means Clustering
- PCA

## Project Structure

```text
swiggy-instamart-customer-copilot/
|
|-- data/
|   |-- raw/
|   |-- cleaned/
|   |-- customers.csv
|   |-- orders.csv
|   |-- tickets.csv
|
|-- models/
|   |-- churn_model_improved.pkl
|   |-- ticket_classifier.pkl
|
|-- policies/
|   |-- delivery_delay.txt
|   |-- refund_request.txt
|   |-- missing_item.txt
|   |-- payment_issue.txt
|   |-- product_quality.txt
|
|-- src/
|   |-- data_cleaning.py
|   |-- eda_analysis.py
|   |-- churn_prediction.py
|   |-- triage.py
|   |-- policy_rag.py
|   |-- copilot.py
|
|-- outputs/
|-- notebooks/
|-- generate_data.py
|-- mock_llm.py
|-- run_project.py
|-- Requirements.txt
|-- README.md
