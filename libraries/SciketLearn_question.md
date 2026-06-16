# SCIKIT-LEARN – INTERVIEW QUESTIONS & ANSWERS

## PART 1: BASICS

### 1. What is Scikit-Learn?

**Answer:**
Scikit-Learn is an open-source Machine Learning library for Python.

**Explanation:**
It provides tools for data preprocessing, model training, evaluation, and prediction.

---

### 2. Why do we use Scikit-Learn?

**Answer:**
We use Scikit-Learn to build Machine Learning models easily.

**Explanation:**

- Data Preprocessing
- Model Training
- Model Evaluation
- Prediction

---

### 3. How do you import Scikit-Learn?

**Answer:**

```python
import sklearn
```

Usually:

```python
from sklearn.model_selection import train_test_split
```

---

### 4. What are Features?

**Answer:**
Features are input variables used for prediction.

**Alternate Names:**

- Independent Variables
- Predictors
- Inputs

Example:

```python
X = df[["Age","Experience"]]
```

---

### 5. What is Target Variable?

**Answer:**
The value we want to predict.

**Alternate Names:**

- Label
- Output
- Dependent Variable

Example:

```python
y = df["Salary"]
```

---

# DATA SPLITTING

### 6. Why do we split data?

**Answer:**
To evaluate model performance on unseen data.

---

### 7. What is train_test_split()?

**Answer:**
Splits dataset into training and testing sets.

```python
from sklearn.model_selection import train_test_split

X_train,X_test,y_train,y_test = train_test_split(
    X,
    y,
    test_size=0.2
)
```

---

### 8. What does test_size=0.2 mean?

**Answer:**

```python
80% Training Data

20% Testing Data
```

---

### 9. What is random_state?

**Answer:**
Ensures reproducible results.

```python
random_state=42
```

---

# PREPROCESSING

### 10. What is Data Preprocessing?

**Answer:**
Preparing raw data before training.

Examples:

- Scaling
- Encoding
- Cleaning

---

### 11. What is StandardScaler?

**Answer:**
Converts data so:

```python
Mean = 0

Standard Deviation = 1
```

```python
from sklearn.preprocessing import StandardScaler
```

---

### 12. Why use StandardScaler?

**Answer:**
Many ML algorithms perform better when features are scaled.

---

### 13. What is MinMaxScaler?

**Answer:**
Scales values between:

```python
0 and 1
```

```python
from sklearn.preprocessing import MinMaxScaler
```

---

### 14. Difference Between StandardScaler and MinMaxScaler

| StandardScaler       | MinMaxScaler             |
| -------------------- | ------------------------ |
| Mean = 0             | Range = 0-1              |
| Uses Std Dev         | Uses Min-Max             |
| Good for Normal Data | Good for Neural Networks |

---

### 15. What is LabelEncoder?

**Answer:**
Converts text into numbers.

Example:

```python
Nagpur -> 0

Pune -> 1

Mumbai -> 2
```

---

### 16. Why do we encode data?

**Answer:**
Machine Learning models understand numbers, not text.

---

# MODEL TRAINING

### 17. What is a Model?

**Answer:**
A model learns patterns from data.

**Alternate Names:**

- Estimator
- Learner

---

### 18. What is fit()?

**Answer:**
Used to train a model.

```python
model.fit(X_train,y_train)
```

---

### 19. What is predict()?

**Answer:**
Used to make predictions.

```python
model.predict(X_test)
```

---

### 20. Difference Between fit() and predict()

| fit()           | predict()     |
| --------------- | ------------- |
| Learn           | Predict       |
| Training        | Testing       |
| Uses Known Data | Uses New Data |

---

# REGRESSION

### 21. What is Regression?

**Answer:**
Predicting numerical values.

Examples:

- Salary Prediction
- House Price Prediction

---

### 22. What is Linear Regression?

**Answer:**
A regression algorithm that finds a linear relationship between variables.

```python
from sklearn.linear_model import LinearRegression
```

---

### 23. Example of Linear Regression

```python
model = LinearRegression()

model.fit(X_train,y_train)
```

---

# CLASSIFICATION

### 24. What is Classification?

**Answer:**
Predicting categories.

Examples:

- Spam / Not Spam
- Fraud / Not Fraud

---

### 25. What is Logistic Regression?

**Answer:**
A classification algorithm.

```python
from sklearn.linear_model import LogisticRegression
```

---

### 26. What is Decision Tree?

**Answer:**
A tree-like model used for classification and regression.

---

### 27. What is Random Forest?

**Answer:**
A collection of multiple Decision Trees.

**Advantage:**

- More Accurate
- Less Overfitting

---

# CLUSTERING

### 28. What is Clustering?

**Answer:**
Grouping similar records together.

---

### 29. What is KMeans?

**Answer:**
A clustering algorithm.

```python
from sklearn.cluster import KMeans
```

---

### 30. Example Use Case

```python
Customer Segmentation
```

---

# EVALUATION

### 31. What is Model Evaluation?

**Answer:**
Measuring model performance.

---

### 32. What is Accuracy?

**Answer:**
Percentage of correct predictions.

```python
from sklearn.metrics import accuracy_score
```

---

### 33. What is Mean Squared Error (MSE)?

**Answer:**
Average squared prediction error.

```python
from sklearn.metrics import mean_squared_error
```

---

### 34. Lower MSE means?

**Answer:**

```python
Better Model
```

---

### 35. Higher Accuracy means?

**Answer:**

```python
Better Classification Model
```

---

# CROSS VALIDATION

### 36. What is Cross Validation?

**Answer:**
Evaluating a model on multiple train-test splits.

---

### 37. Why use Cross Validation?

**Answer:**
More reliable than a single train-test split.

---

### 38. What is cross_val_score()?

```python
from sklearn.model_selection import cross_val_score
```

---

# PIPELINE

### 39. What is Pipeline?

**Answer:**
Combines preprocessing and model training into one workflow.

```python
from sklearn.pipeline import Pipeline
```

---

### 40. Why use Pipeline?

**Answer:**

- Cleaner Code
- Less Errors
- Production Ready

---

# HYPERPARAMETER TUNING

### 41. What is Hyperparameter Tuning?

**Answer:**
Finding best model settings.

---

### 42. What is GridSearchCV?

**Answer:**
Tries multiple parameter combinations.

```python
from sklearn.model_selection import GridSearchCV
```

---

### 43. Why use GridSearchCV?

**Answer:**
To improve model performance.

---

# AI ENGINEER IMPORTANT QUESTIONS

### 44. Why is Scikit-Learn important?

**Answer:**
It provides end-to-end Machine Learning tools.

---

### 45. Most used preprocessing techniques?

**Answer:**

```python
StandardScaler

MinMaxScaler

LabelEncoder
```

---

### 46. Most used ML algorithms?

**Answer:**

```python
Linear Regression

Logistic Regression

Decision Tree

Random Forest

KNN
```

---

### 47. Most important evaluation metrics?

**Answer:**

```python
Accuracy

Precision

Recall

F1 Score

MSE
```

---

### 48. What is Overfitting?

**Answer:**
Model performs well on training data but poorly on new data.

---

### 49. What is Underfitting?

**Answer:**
Model fails to learn patterns properly.

---

### 50. Why learn Scikit-Learn before Deep Learning?

**Answer:**

Because it teaches:

- Data Preparation
- Model Training
- Evaluation
- Feature Engineering

which are fundamental AI concepts.

---

# ONE-LINE SUMMARY

### Scikit-Learn

```python
Machine Learning Library
```

### X

```python
Features
```

### y

```python
Target
```

### train_test_split()

```python
Split Data
```

### fit()

```python
Train Model
```

### predict()

```python
Make Predictions
```

### StandardScaler

```python
Mean = 0, Std = 1
```

### MinMaxScaler

```python
Scale 0 to 1
```

### LabelEncoder

```python
Text → Number
```

### Linear Regression

```python
Predict Numbers
```

### Logistic Regression

```python
Predict Categories
```

### Random Forest

```python
Many Decision Trees
```

### KMeans

```python
Grouping Data
```

### Accuracy

```python
Classification Score
```

### MSE

```python
Regression Error
```

### Pipeline

```python
Automation Workflow
```

### GridSearchCV

```python
Parameter Tuning
```

---

# PRIORITY FOR AI ENGINEERS

| Topic               | Priority   |
| ------------------- | ---------- |
| Features & Target   | ⭐⭐⭐⭐⭐ |
| Train-Test Split    | ⭐⭐⭐⭐⭐ |
| fit() & predict()   | ⭐⭐⭐⭐⭐ |
| StandardScaler      | ⭐⭐⭐⭐⭐ |
| LabelEncoder        | ⭐⭐⭐⭐⭐ |
| Linear Regression   | ⭐⭐⭐⭐⭐ |
| Logistic Regression | ⭐⭐⭐⭐⭐ |
| Random Forest       | ⭐⭐⭐⭐⭐ |
| Evaluation Metrics  | ⭐⭐⭐⭐⭐ |
| Pipeline            | ⭐⭐⭐⭐   |
| Cross Validation    | ⭐⭐⭐⭐   |
| GridSearchCV        | ⭐⭐⭐⭐   |
| KMeans              | ⭐⭐⭐⭐   |
| PCA                 | ⭐⭐⭐     |

These 50 questions cover roughly **90–95% of Scikit-Learn concepts asked in fresher AI Engineer, ML Engineer, and Data Scientist interviews**.
