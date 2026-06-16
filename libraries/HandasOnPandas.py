import pandas as pd
import numpy as np

# -------------------------------
# 📝 Task 1: Create DataFrames
# -------------------------------
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['NY', 'LA', 'Chicago']}
df1 = pd.DataFrame(data)
print("Task 1 - DataFrame from dict:\n", df1)

df2 = pd.DataFrame(np.arange(1, 10).reshape(3, 3),
                   columns=['A', 'B', 'C'])
print("\nTask 1 - DataFrame from NumPy:\n", df2)

# -------------------------------
# 🔄 Task 2: Basic Operations
# -------------------------------
print("\nTask 2 - Head:\n", df1.head())
print("Task 2 - Info:")
print(df1.info())
print("Task 2 - Describe:\n", df1.describe())

# -------------------------------
# 🎯 Task 3: Indexing & Selection
# -------------------------------
print("\nTask 3 - Single column:\n", df1['Name'])
print("Task 3 - Multiple columns:\n", df1[['Name', 'City']])
print("Task 3 - Row by index:\n", df1.loc[1])   # Bob’s row

# -------------------------------
# 📊 Task 4: Filtering Data
# -------------------------------
print("\nTask 4 - Age > 25:\n", df1[df1['Age'] > 25])
print("Task 4 - City == 'LA':\n", df1[df1['City'] == 'LA'])

# -------------------------------
# 🔍 Task 5: Grouping & Aggregation
# -------------------------------
print("\nTask 5 - Group by City (mean Age):\n", df1.groupby('City')['Age'].mean())
print("Task 5 - Value counts (City):\n", df1['City'].value_counts())
