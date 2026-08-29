# FinGuard

FinGuard is an end-to-end machine learning system for financial
transaction fraud detection and risk scoring.

The project focuses on detecting fraudulent financial transactions
while accounting for the severe class imbalance common in fraud
datasets.

Rather than optimising for accuracy alone, FinGuard will examine the
trade-off between detecting fraudulent transactions and incorrectly
flagging legitimate customers.

## Project Goals

- Build a reproducible data preprocessing pipeline
- Analyse highly imbalanced financial transaction data
- Engineer transaction-level fraud features
- Compare baseline and tree-based machine learning models
- Evaluate models using precision, recall, F1 and PR-AUC
- Optimise classification thresholds based on fraud-risk trade-offs
- Serve predictions through an API
- Log predictions for monitoring and analysis
- Package the system in a production-oriented structure