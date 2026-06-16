# matplotlib_for_ai_engineer.py

import matplotlib.pyplot as plt
import numpy as np

# ==================================================
# MATPLOTLIB FOR AI ENGINEER
# Learn these topics and you're job-ready for
# AI/ML projects.
# ==================================================


# --------------------------------------------------
# 1. IMPORT MATPLOTLIB
# --------------------------------------------------
# Definition:
# pyplot is the plotting module.

import matplotlib.pyplot as plt

# AI Use:
# Creating visualizations for EDA and ML.


# --------------------------------------------------
# 2. SIMPLE LINE PLOT
# --------------------------------------------------
# Definition:
# Connect data points using lines.

x = [1, 2, 3, 4, 5]

y = [10, 20, 30, 40, 50]

plt.plot(x, y)

plt.title("Simple Line Plot")

plt.xlabel("X Values")

plt.ylabel("Y Values")

plt.show()

# AI Use:
# Training Loss Curve
# Accuracy Curve


# --------------------------------------------------
# 3. LINE COLOR
# --------------------------------------------------
# Definition:
# Change line color.

plt.plot(
    x,
    y,
    color="red"
)

plt.title("Line Color Example")

plt.show()

# AI Use:
# Better visualization readability.


# --------------------------------------------------
# 4. LINE STYLE
# --------------------------------------------------
# Definition:
# Change line pattern.

plt.plot(
    x,
    y,
    linestyle="--"
)

plt.title("Line Style Example")

plt.show()

# AI Use:
# Compare multiple metrics.


# --------------------------------------------------
# 5. LINE WIDTH
# --------------------------------------------------
# Definition:
# Change line thickness.

plt.plot(
    x,
    y,
    linewidth=3
)

plt.title("Line Width Example")

plt.show()


# --------------------------------------------------
# 6. MARKERS
# --------------------------------------------------
# Definition:
# Highlight data points.

plt.plot(
    x,
    y,
    marker="o"
)

plt.title("Markers Example")

plt.show()

# AI Use:
# Show actual observations.


# --------------------------------------------------
# 7. SCATTER PLOT
# --------------------------------------------------
# Definition:
# Shows relationship between variables.

age = [20, 25, 30, 35, 40]

salary = [20000, 30000, 45000, 60000, 75000]

plt.scatter(
    age,
    salary
)

plt.title("Age vs Salary")

plt.xlabel("Age")

plt.ylabel("Salary")

plt.show()

# AI Use:
# Feature Relationship Analysis


# --------------------------------------------------
# 8. BAR CHART
# --------------------------------------------------
# Definition:
# Compare categories.

students = [
    "Amit",
    "Rahul",
    "Priya"
]

marks = [80, 90, 70]

plt.bar(
    students,
    marks
)

plt.title("Student Marks")

plt.show()

# AI Use:
# Category comparison


# --------------------------------------------------
# 9. HORIZONTAL BAR CHART
# --------------------------------------------------
# Definition:
# Horizontal version of bar chart.

plt.barh(
    students,
    marks
)

plt.title("Horizontal Bar Chart")

plt.show()


# --------------------------------------------------
# 10. HISTOGRAM
# --------------------------------------------------
# Definition:
# Shows distribution of data.

data = np.random.normal(
    50,
    10,
    1000
)

plt.hist(data)

plt.title("Histogram")

plt.show()

# AI Use:
# Check distribution
# Detect skewness
# Detect outliers


# --------------------------------------------------
# 11. BINS IN HISTOGRAM
# --------------------------------------------------
# Definition:
# Number of groups.

plt.hist(
    data,
    bins=20
)

plt.title("Histogram with Bins")

plt.show()


# --------------------------------------------------
# 12. PIE CHART
# --------------------------------------------------
# Definition:
# Shows proportions.

values = [40, 30, 20, 10]

labels = [
    "AI",
    "ML",
    "DL",
    "Data"
]

plt.pie(
    values,
    labels=labels
)

plt.title("Pie Chart")

plt.show()


# --------------------------------------------------
# 13. LEGEND
# --------------------------------------------------
# Definition:
# Identifies graph lines.

x = [1, 2, 3, 4]

y1 = [10, 20, 30, 40]

y2 = [15, 25, 35, 45]

plt.plot(
    x,
    y1,
    label="Sales"
)

plt.plot(
    x,
    y2,
    label="Profit"
)

plt.legend()

plt.show()

# AI Use:
# Compare multiple metrics.


# --------------------------------------------------
# 14. GRID
# --------------------------------------------------
# Definition:
# Add reference lines.

plt.plot(x, y1)

plt.grid(True)

plt.show()

# AI Use:
# Easier graph reading.


# --------------------------------------------------
# 15. FIGURE SIZE
# --------------------------------------------------
# Definition:
# Control graph dimensions.

plt.figure(
    figsize=(8, 5)
)

plt.plot(x, y1)

plt.title("Figure Size Example")

plt.show()


# --------------------------------------------------
# 16. SUBPLOTS
# --------------------------------------------------
# Definition:
# Multiple plots in one figure.

plt.subplot(1, 2, 1)

plt.plot(x, y1)

plt.title("Plot 1")

plt.subplot(1, 2, 2)

plt.plot(x, y2)

plt.title("Plot 2")

plt.show()

# AI Use:
# Compare graphs side-by-side.


# --------------------------------------------------
# 17. SAVE FIGURE
# --------------------------------------------------
# Definition:
# Save graph as image.

plt.plot(x, y1)

plt.savefig("graph.png")

plt.close()

# AI Use:
# Reports
# Dashboards


# --------------------------------------------------
# 18. TRAINING LOSS CURVE
# --------------------------------------------------
# Definition:
# Visualize model learning.

loss = [
    1.0,
    0.8,
    0.6,
    0.4,
    0.2
]

plt.plot(loss)

plt.title("Training Loss")

plt.xlabel("Epoch")

plt.ylabel("Loss")

plt.show()

# AI Use:
# Monitor training.


# --------------------------------------------------
# 19. ACCURACY CURVE
# --------------------------------------------------
# Definition:
# Visualize model accuracy.

accuracy = [
    60,
    70,
    80,
    90,
    95
]

plt.plot(accuracy)

plt.title("Accuracy Curve")

plt.xlabel("Epoch")

plt.ylabel("Accuracy")

plt.show()

# AI Use:
# Evaluate model performance.


# --------------------------------------------------
# 20. MULTIPLE LINES
# --------------------------------------------------
# Definition:
# Compare multiple datasets.

plt.plot(
    [1, 2, 3],
    [10, 20, 30],
    label="Model A"
)

plt.plot(
    [1, 2, 3],
    [15, 25, 35],
    label="Model B"
)

plt.legend()

plt.show()

# AI Use:
# Model comparison.


# --------------------------------------------------
# 21. AI ENGINEER INTERVIEW REVISION
# --------------------------------------------------

# Matplotlib = Visualization Library

# plot() = Line Graph

# scatter() = Relationship Graph

# bar() = Category Comparison

# barh() = Horizontal Bar Chart

# hist() = Distribution Analysis

# pie() = Percentage Distribution

# title() = Graph Title

# xlabel() = X Axis Name

# ylabel() = Y Axis Name

# legend() = Graph Identification

# grid() = Reference Lines

# figure() = Graph Size

# subplot() = Multiple Graphs

# savefig() = Save Plot

# show() = Display Plot

# Histogram = Distribution Analysis

# Scatter Plot = Correlation Analysis

# Loss Curve = Model Learning

# Accuracy Curve = Model Evaluation


# --------------------------------------------------
# 22. MOST IMPORTANT FOR AI ENGINEERS
# --------------------------------------------------

# ⭐⭐⭐⭐⭐ Histogram

# ⭐⭐⭐⭐⭐ Scatter Plot

# ⭐⭐⭐⭐⭐ Line Plot

# ⭐⭐⭐⭐⭐ Loss Curve

# ⭐⭐⭐⭐⭐ Accuracy Curve

# ⭐⭐⭐⭐⭐ Labels & Titles

# ⭐⭐⭐⭐ Subplots

# ⭐⭐⭐⭐ Bar Charts

# ⭐⭐⭐⭐ Save Figures

# ⭐⭐⭐ Grid

# --------------------------------------------------
# QUICK MEMORY TRICK
# --------------------------------------------------

# plot()      -> Trend

# scatter()   -> Relationship

# hist()      -> Distribution

# bar()       -> Comparison

# pie()       -> Percentage

# legend()    -> Identify Lines

# grid()      -> Easy Reading

# savefig()   -> Save Plot

# show()      -> Display Plot