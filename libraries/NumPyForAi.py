# numpy_for_ai_engineer.py

import numpy as np

# ==================================================
# NUMPY FOR AI ENGINEER
# Learn these topics and you're job-ready for
# AI/ML projects.
# ==================================================


# --------------------------------------------------
# 1. ARRAY
# --------------------------------------------------
# Definition:
# Array = Fast and memory-efficient container
# for numerical data.
#
# AI Use:
# Datasets, images, embeddings, model inputs.

arr = np.array([10, 20, 30, 40, 50])

print(arr)


# --------------------------------------------------
# 2. SHAPE
# --------------------------------------------------
# Definition:
# Shape tells rows and columns.

data = np.array([
    [1, 2, 3],
    [4, 5, 6]
])

print("Shape:", data.shape)

# AI Use:
# Understanding dataset dimensions.


# --------------------------------------------------
# 3. SIZE
# --------------------------------------------------
# Definition:
# Total number of elements.

print("Size:", data.size)


# --------------------------------------------------
# 4. DTYPE
# --------------------------------------------------
# Definition:
# Data type stored inside array.

print("Dtype:", data.dtype)

# AI Use:
# float32 is commonly used in Deep Learning.


# --------------------------------------------------
# 5. INDEXING
# --------------------------------------------------
# Definition:
# Access single element.

print(arr[0])

# AI Use:
# Selecting specific feature values.


# --------------------------------------------------
# 6. SLICING
# --------------------------------------------------
# Definition:
# Access multiple elements.

print(arr[1:4])

# AI Use:
# Train/Test data splitting.


# --------------------------------------------------
# 7. RESHAPE
# --------------------------------------------------
# Definition:
# Change dimensions without changing data.

a = np.arange(12)

reshaped = a.reshape(3, 4)

print(reshaped)

# AI Use:
# Convert flat data into model format.


# --------------------------------------------------
# 8. VECTOR OPERATIONS
# --------------------------------------------------
# Definition:
# Math on entire array without loops.

x = np.array([1, 2, 3])

y = np.array([4, 5, 6])

print(x + y)

print(x - y)

print(x * y)

# AI Use:
# Feature transformations.


# --------------------------------------------------
# 9. BROADCASTING
# --------------------------------------------------
# Definition:
# NumPy automatically matches dimensions.

matrix = np.array([
    [1, 2],
    [3, 4]
])

print(matrix + 10)

# AI Use:
# Add bias in Neural Networks.


# --------------------------------------------------
# 10. AGGREGATION FUNCTIONS
# --------------------------------------------------
# Definition:
# Summary statistics.

scores = np.array([10, 20, 30, 40])

print(np.sum(scores))

print(np.mean(scores))

print(np.max(scores))

print(np.min(scores))

# AI Use:
# Data analysis.


# --------------------------------------------------
# 11. BOOLEAN MASKING
# --------------------------------------------------
# Definition:
# Filter data using conditions.

data = np.array([10, 20, 30, 40, 50])

filtered = data[data > 25]

print(filtered)

# AI Use:
# Data cleaning.


# --------------------------------------------------
# 12. RANDOM NUMBERS
# --------------------------------------------------
# Definition:
# Generate random values.

print(np.random.rand(2, 2))

print(np.random.randint(1, 100, (2, 2)))

# AI Use:
# Weight initialization.


# --------------------------------------------------
# 13. DOT PRODUCT
# --------------------------------------------------
# Definition:
# Multiply corresponding values and sum.

v1 = np.array([1, 2, 3])

v2 = np.array([4, 5, 6])

print(np.dot(v1, v2))

# AI Use:
# Core operation in Machine Learning.


# --------------------------------------------------
# 14. MATRIX MULTIPLICATION
# --------------------------------------------------
# Definition:
# Multiply rows and columns.

A = np.array([
    [1, 2],
    [3, 4]
])

B = np.array([
    [5, 6],
    [7, 8]
])

print(np.matmul(A, B))

# AI Use:
# Neural Network calculations.


# --------------------------------------------------
# 15. NORMALIZATION
# --------------------------------------------------
# Definition:
# Scale data between 0 and 1.

data = np.array([10, 20, 30, 40, 50])

normalized = (
    (data - np.min(data))
    /
    (np.max(data) - np.min(data))
)

print(normalized)

# AI Use:
# Better model performance.


# --------------------------------------------------
# 16. STANDARDIZATION
# --------------------------------------------------
# Definition:
# Mean = 0
# Standard Deviation = 1

standardized = (
    (data - np.mean(data))
    /
    np.std(data)
)

print(standardized)

# AI Use:
# Common preprocessing step.


# --------------------------------------------------
# 17. NaN HANDLING
# --------------------------------------------------
# Definition:
# NaN = Missing Value

arr = np.array([1, 2, np.nan, 4])

print(np.isnan(arr))

print(np.nanmean(arr))

# AI Use:
# Missing value handling.


# --------------------------------------------------
# 18. AI ENGINEER INTERVIEW REVISION
# --------------------------------------------------

# NumPy = Numerical Python Library

# Array = Fast numerical container

# Shape = Rows and Columns

# Size = Total elements

# Dtype = Data type

# Indexing = Single value access

# Slicing = Multiple value access

# Reshape = Change dimensions

# Broadcasting = Auto dimension matching

# Dot Product = Multiply + Sum

# Matrix Multiplication = Linear Algebra

# Boolean Masking = Filtering

# Normalization = Scale 0-1

# Standardization = Mean 0 Std 1

# NaN = Missing value

# Vectorization = Avoid loops