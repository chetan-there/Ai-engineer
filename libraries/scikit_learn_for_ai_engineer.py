# scikit_learn_for_ai_engineer.py

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    LabelEncoder
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_squared_error,
    accuracy_score
)

import pandas as pd
import numpy as np

# ==================================================
# SCIKIT-LEARN FOR AI ENGINEER
# Learn these topics and you're job-ready for
# AI/ML projects.
# ==================================================


# --------------------------------------------------
# 1. WHAT IS SCIKIT-LEARN?
# --------------------------------------------------
# Definition:
# Most popular Machine Learning library in Python.
#
# AI Use:
# Training ML models.
#
# Alternate Names:
# sklearn
# scikit-learn


# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------
# Definition:
# Create sample dataset.

data = pd.DataFrame({
    "Experience": [1, 2, 3, 4, 5],
    "Salary": [20000, 30000, 40000, 50000, 60000]
})

print(data)


# --------------------------------------------------
# 3. FEATURES (X)
# --------------------------------------------------
# Definition:
# Input variables used for prediction.
#
# Alternate Name:
# Independent Variables

X = data[["Experience"]]

print(X)


# --------------------------------------------------
# 4. TARGET (Y)
# --------------------------------------------------
# Definition:
# Output variable to predict.
#
# Alternate Names:
# Label
# Dependent Variable

y = data["Salary"]

print(y)


# --------------------------------------------------
# 5. TRAIN TEST SPLIT
# --------------------------------------------------
# Definition:
# Split data into training and testing.
#
# AI Use:
# Evaluate model performance.

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print(X_train)


# --------------------------------------------------
# 6. STANDARD SCALER
# --------------------------------------------------
# Definition:
# Mean = 0
# Std = 1
#
# AI Use:
# Improve ML performance.

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

print(X_train_scaled)


# --------------------------------------------------
# 7. MIN MAX SCALER
# --------------------------------------------------
# Definition:
# Scale values between 0 and 1.

minmax = MinMaxScaler()

X_scaled = minmax.fit_transform(X)

print(X_scaled)


# --------------------------------------------------
# 8. LABEL ENCODER
# --------------------------------------------------
# Definition:
# Convert text into numbers.
#
# AI Use:
# ML models need numbers.

encoder = LabelEncoder()

cities = ["Nagpur", "Pune", "Mumbai"]

encoded = encoder.fit_transform(cities)

print(encoded)


# --------------------------------------------------
# 9. MODEL
# --------------------------------------------------
# Definition:
# Algorithm that learns patterns.
#
# Alternate Names:
# Estimator
# Learner

model = LinearRegression()


# --------------------------------------------------
# 10. TRAIN MODEL
# --------------------------------------------------
# Definition:
# Learn patterns from data.
#
# Alternate Name:
# fit()

model.fit(
    X_train,
    y_train
)

print("Model Trained")


# --------------------------------------------------
# 11. PREDICTION
# --------------------------------------------------
# Definition:
# Use model to predict unseen data.
#
# Alternate Name:
# Inference

prediction = model.predict(X_test)

print(prediction)


# --------------------------------------------------
# 12. EVALUATION
# --------------------------------------------------
# Definition:
# Measure model performance.

mse = mean_squared_error(
    y_test,
    prediction
)

print(mse)


# --------------------------------------------------
# 13. PIPELINE
# --------------------------------------------------
# Definition:
# Chain preprocessing + model.

from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LinearRegression())
])

print(pipeline)


# --------------------------------------------------
# 14. CROSS VALIDATION
# --------------------------------------------------
# Definition:
# Evaluate model on multiple splits.

from sklearn.model_selection import cross_val_score

scores = cross_val_score(
    model,
    X,
    y,
    cv=3
)

print(scores)


# --------------------------------------------------
# 15. GRID SEARCH
# --------------------------------------------------
# Definition:
# Find best hyperparameters.

from sklearn.model_selection import GridSearchCV

# AI Use:
# Model tuning


# --------------------------------------------------
# 16. CLASSIFICATION
# --------------------------------------------------
# Definition:
# Predict categories.
#
# Examples:
# Spam / Not Spam
# Fraud / Not Fraud

from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression()


# --------------------------------------------------
# 17. REGRESSION
# --------------------------------------------------
# Definition:
# Predict continuous values.
#
# Examples:
# Salary
# House Price

regressor = LinearRegression()


# --------------------------------------------------
# 18. CLUSTERING
# --------------------------------------------------
# Definition:
# Group similar records.
#
# Example:
# Customer Segmentation

from sklearn.cluster import KMeans

kmeans = KMeans(
    n_clusters=3
)


# --------------------------------------------------
# 19. ACCURACY SCORE
# --------------------------------------------------
# Definition:
# Classification performance metric.

y_true = [1, 0, 1]

y_pred = [1, 0, 1]

print(
    accuracy_score(
        y_true,
        y_pred
    )
)


# --------------------------------------------------
# 20. FEATURE ENGINEERING
# --------------------------------------------------
# Definition:
# Create useful features.
#
# AI Use:
# Better predictions.


# --------------------------------------------------
# 21. COMMON ALGORITHMS
# --------------------------------------------------

# LinearRegression

# LogisticRegression

# DecisionTreeClassifier

# RandomForestClassifier

# KNeighborsClassifier

# SVC

# KMeans


# --------------------------------------------------
# 22. AI ENGINEER INTERVIEW REVISION
# --------------------------------------------------

# sklearn = Machine Learning Library

# X = Features

# y = Target

# train_test_split = Train/Test Division

# fit() = Training

# predict() = Prediction

# StandardScaler = Mean 0 Std 1

# MinMaxScaler = Scale 0-1

# LabelEncoder = Text to Number

# LinearRegression = Regression Model

# LogisticRegression = Classification Model

# KMeans = Clustering

# Pipeline = Workflow Automation

# Cross Validation = Multiple Evaluation

# GridSearchCV = Hyperparameter Tuning

# Accuracy = Classification Metric

# MSE = Regression Metric


# --------------------------------------------------
# 23. MOST IMPORTANT FOR AI ENGINEERS
# --------------------------------------------------

# ⭐⭐⭐⭐⭐ train_test_split

# ⭐⭐⭐⭐⭐ StandardScaler

# ⭐⭐⭐⭐⭐ LabelEncoder

# ⭐⭐⭐⭐⭐ fit()

# ⭐⭐⭐⭐⭐ predict()

# ⭐⭐⭐⭐⭐ LinearRegression

# ⭐⭐⭐⭐⭐ LogisticRegression

# ⭐⭐⭐⭐⭐ RandomForest

# ⭐⭐⭐⭐⭐ Evaluation Metrics

# ⭐⭐⭐⭐⭐ Pipeline

# ⭐⭐⭐⭐ Cross Validation

# ⭐⭐⭐⭐ GridSearchCV

# ⭐⭐⭐⭐ KMeans


# --------------------------------------------------
# QUICK MEMORY TRICK
# --------------------------------------------------

# X           -> Features

# y           -> Target

# fit()       -> Learn

# predict()   -> Predict

# scaler      -> Normalize

# encoder     -> Text -> Number

# regression  -> Number Output

# classification -> Category Output

# clustering  -> Group Similar Data

# pipeline    -> Automation

# accuracy    -> Classification Score

# mse         -> Regression Error