# Fraud Detection and Prevention Project

## Overview

This repository documents my approach to building a fraud detection model and implementing preventive measures to enhance fraud detection capabilities.

## Task Details

### 1. Data Cleaning

#### Steps Taken:
- **Missing Values:**
  - I identified missing values using `data.isnull().sum()`.
  - Removed rows with missing values using `data.dropna(inplace=True)`.

- **Outliers:**
  - I created features like `amount_balance_ratio` to indirectly capture outlier behavior. I assumed outliers’ impact would be negligible.

- **Multi-collinearity:**
  - I used feature engineering to combine highly correlated variables, improving the analysis.

### 2. Fraud Detection Model

#### Model:
I utilized a Random Forest Classifier for fraud detection.

- **Algorithm:**
  - Random Forest is robust, handles non-linear relationships, and resists overfitting.

- **Implementation:**
  - I used `RandomForestClassifier` from `sklearn.ensemble` with the following parameters:
    - `n_estimators` (number of trees)
    - `class_weight` (to handle class imbalance)
    - `random_state` (for reproducibility)
    - Enabled out-of-bag error estimation

- **Early Stopping:**
  - Added early stopping to prevent overfitting and optimize training time. The initial model training took 18 minutes without early stopping.

### 3. Variable Selection

#### Selected Features:
```python
features = ['step', 'type_encoded', 'amount', 'amount_balance_ratio',
            'oldbalanceOrg', 'newbalanceOrig',
            'balance_change_orig', 'balance_change_dest']
```
I selected these features based on domain knowledge and their relevance to fraud detection.

### 4. Model Performance

#### Evaluation Metrics:
- **Classification Report:**
  - Precision, recall, F1-score, and support for each class.

- **ROC AUC Score:**
  - Assessed the model’s ability to distinguish between classes.

- **Accuracy and Precision:**
  - Calculated separately for better insight.

- **Confusion Matrix:**
  - Visualized predictions (true positives, true negatives, false positives, and false negatives).

- **Feature Importance:**
  - Plotted to understand each feature’s contribution.

These tools provided a comprehensive performance evaluation and helped identify improvement areas.

### 5. Key Factors Predicting Fraud

#### Significant Features:
- `oldbalanceOrg`
- `amount`
- `newbalanceOrig`
- `balance_change_orig`
- `balance_change_dest`

These factors align with common fraud patterns:
- **Large Balance Discrepancies:** Discrepancies between original and new balances often indicate fraud.
- **Unusually Large Transactions:** High transaction amounts are red flags.
- **Balance Changes:** Significant decreases in originator’s balance and increases in the destination’s balance signal fraud.

### 6. Prevention Infrastructure

#### Recommendations:
- **Real-time Transaction Monitoring:**
  - Implement systems to flag suspicious activities using predefined rules or machine learning models.

- **Multi-Factor Authentication:**
  - Enforce strong authentication, such as two-factor authentication.

- **Anomaly Detection:**
  - Use machine learning to identify unusual patterns and deviations.

- **Data Encryption and Security:**
  - Protect sensitive data using robust encryption protocols.

- **Employee Training:**
  - Educate employees on fraud schemes and prevention best practices.

### 7. Determining Effectiveness

#### Actions Taken:
- **Monitor Fraud Metrics:**
  - Tracked key metrics, such as detected fraudulent transactions, financial loss prevented, and detection rate. Compared results before and after implementing preventive measures.

- **Conduct Regular Audits:**
  - Performed periodic audits to ensure system functionality and address weaknesses, such as model decay.

- **Seek Feedback:**
  - Gathered input from employees, customers, and stakeholders to evaluate the fraud prevention program.

---

### Conclusion
This project demonstrates a systematic approach to fraud detection and prevention, leveraging machine learning and robust evaluation methods to enhance security and performance.

