# pandas_for_ai_engineer.py

import pandas as pd
import numpy as np

# ==================================================
# PANDAS FOR AI ENGINEER
# Learn these topics and you're job-ready for
# Data Analysis, ML and AI projects.
# ==================================================


# --------------------------------------------------
# 1. SERIES
# --------------------------------------------------
# Definition:
# Series = One-dimensional labeled data structure.
#
# Similar To:
# Single column in Excel.

series = pd.Series([10, 20, 30, 40])

print(series)


# --------------------------------------------------
# 2. DATAFRAME
# --------------------------------------------------
# Definition:
# DataFrame = Two-dimensional table with rows
# and columns.
#
# Similar To:
# Excel Sheet / SQL Table

df = pd.DataFrame({
    "name": ["Ram", "Shyam", "Mohan"],
    "age": [21, 22, 23]
})

print(df)


# --------------------------------------------------
# 3. READ CSV
# --------------------------------------------------
# Definition:
# Load CSV file into DataFrame.

# df = pd.read_csv("students.csv")

# AI Use:
# Load datasets


# --------------------------------------------------
# 4. SAVE CSV
# --------------------------------------------------
# Definition:
# Save DataFrame into CSV.

# df.to_csv("output.csv", index=False)


# --------------------------------------------------
# 5. HEAD
# --------------------------------------------------
# Definition:
# First 5 rows.

print(df.head())


# --------------------------------------------------
# 6. TAIL
# --------------------------------------------------
# Definition:
# Last 5 rows.

print(df.tail())


# --------------------------------------------------
# 7. INFO
# --------------------------------------------------
# Definition:
# Summary of dataframe.

print(df.info())

# Returns:
# Rows
# Columns
# Datatypes
# Null Values


# --------------------------------------------------
# 8. DESCRIBE
# --------------------------------------------------
# Definition:
# Statistical summary.

print(df.describe())

# Returns:
# Count
# Mean
# Std
# Min
# Max


# --------------------------------------------------
# 9. SHAPE
# --------------------------------------------------
# Definition:
# Number of rows and columns.

print(df.shape)


# --------------------------------------------------
# 10. COLUMNS
# --------------------------------------------------
# Definition:
# Return column names.

print(df.columns)


# --------------------------------------------------
# 11. SELECT COLUMN
# --------------------------------------------------
# Definition:
# Access a single column.

print(df["name"])


# --------------------------------------------------
# 12. SELECT MULTIPLE COLUMNS
# --------------------------------------------------

print(df[["name", "age"]])


# --------------------------------------------------
# 13. LOC
# --------------------------------------------------
# Definition:
# Select using labels.

print(df.loc[0])


# --------------------------------------------------
# 14. ILOC
# --------------------------------------------------
# Definition:
# Select using index position.

print(df.iloc[0])


# --------------------------------------------------
# 15. FILTERING
# --------------------------------------------------
# Definition:
# Select rows using condition.

print(df[df["age"] > 21])

# AI Use:
# Data Cleaning


# --------------------------------------------------
# 16. SORTING
# --------------------------------------------------
# Definition:
# Sort rows.

print(df.sort_values("age"))


# --------------------------------------------------
# 17. ADD NEW COLUMN
# --------------------------------------------------

df["salary"] = [10000, 20000, 30000]

print(df)


# --------------------------------------------------
# 18. DELETE COLUMN
# --------------------------------------------------

df.drop("salary", axis=1)

# axis=1 -> column


# --------------------------------------------------
# 19. RENAME COLUMN
# --------------------------------------------------

df.rename(columns={"age": "Age"})


# --------------------------------------------------
# 20. MISSING VALUES
# --------------------------------------------------
# Definition:
# Missing data represented by NaN.

df2 = pd.DataFrame({
    "marks": [10, np.nan, 30]
})

print(df2.isnull())

print(df2.isnull().sum())


# --------------------------------------------------
# 21. FILL MISSING VALUES
# --------------------------------------------------

df2["marks"] = df2["marks"].fillna(0)

print(df2)


# --------------------------------------------------
# 22. DROP MISSING VALUES
# --------------------------------------------------

df2.dropna()


# --------------------------------------------------
# 23. DUPLICATES
# --------------------------------------------------
# Definition:
# Repeated rows.

print(df.duplicated())

df.drop_duplicates()


# --------------------------------------------------
# 24. VALUE COUNTS
# --------------------------------------------------
# Definition:
# Frequency of values.

print(df["name"].value_counts())


# --------------------------------------------------
# 25. UNIQUE VALUES
# --------------------------------------------------

print(df["name"].unique())


# --------------------------------------------------
# 26. GROUPBY
# --------------------------------------------------
# Definition:
# Group similar records together.

sales = pd.DataFrame({
    "city": ["Nagpur", "Pune", "Nagpur"],
    "sales": [100, 200, 300]
})

print(
    sales.groupby("city")["sales"].sum()
)

# AI Use:
# Aggregation and reporting


# --------------------------------------------------
# 27. APPLY FUNCTION
# --------------------------------------------------
# Definition:
# Apply custom function.

df["double_age"] = df["age"].apply(
    lambda x: x * 2
)

print(df)


# --------------------------------------------------
# 28. MERGE
# --------------------------------------------------
# Definition:
# Join multiple tables.

students = pd.DataFrame({
    "id": [1, 2],
    "name": ["Ram", "Shyam"]
})

marks = pd.DataFrame({
    "id": [1, 2],
    "marks": [80, 90]
})

merged = pd.merge(
    students,
    marks,
    on="id"
)

print(merged)

# Similar To:
# SQL JOIN


# --------------------------------------------------
# 29. EXPORT EXCEL
# --------------------------------------------------

# df.to_excel(
#     "students.xlsx",
#     index=False
# )


# --------------------------------------------------
# 30. AI ENGINEER INTERVIEW REVISION
# --------------------------------------------------

# Pandas = Data Analysis Library

# Series = Single Column

# DataFrame = Complete Table

# read_csv() = Load CSV

# to_csv() = Save CSV

# head() = First 5 Rows

# tail() = Last 5 Rows

# info() = Dataset Summary

# describe() = Statistics Summary

# shape = Rows and Columns

# columns = Column Names

# loc = Label Based Selection

# iloc = Position Based Selection

# filter = Select Rows

# sort_values() = Sorting

# fillna() = Replace Missing Values

# dropna() = Remove Missing Values

# duplicated() = Find Duplicates

# drop_duplicates() = Remove Duplicates

# value_counts() = Frequency Count

# unique() = Distinct Values

# groupby() = Group Records

# apply() = Custom Function

# merge() = Join Tables