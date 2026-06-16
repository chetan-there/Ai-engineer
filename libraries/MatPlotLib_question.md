MATPLOTLIB – INTERVIEW QUESTIONS & ANSWERS
PART 1: BASICS

1. What is Matplotlib?
   Answer:
   Matplotlib is a Python library used for data visualization and plotting graphs.
   Explanation:
   It helps convert data into visual charts for better understanding and analysis.

---

2. Why do we use Matplotlib?
   Answer:
   We use Matplotlib to visualize data and identify patterns, trends, and relationships.
   Explanation:
   Graphs make data easier to understand than raw numbers.

---

3. Which module is most commonly used?
   Answer:
   import matplotlib.pyplot as plt
   Explanation:
   pyplot provides functions similar to MATLAB for creating plots.

---

4. What is a plot?
   Answer:
   A plot is a graphical representation of data.

---

5. Why is visualization important in AI?
   Answer:
   Visualization helps understand data before training machine learning models.
   Explanation:
   • Detect outliers
   • Find trends
   • Check distributions
   • Analyze relationships

---

FIRST GRAPH 6. How do you create a simple line graph?
import matplotlib.pyplot as plt

x = [1,2,3,4]
y = [10,20,30,40]

plt.plot(x,y)
plt.show()

---

7. What does plt.show() do?
   Answer:
   Displays the graph.

---

8. What happens if plt.show() is not used?
   Answer:
   The graph may not appear in some environments.

---

LINE PLOT 9. What is a Line Plot?
Answer:
A graph where points are connected by lines.
Use Cases:
• Stock prices
• Temperature changes
• Sales trends

---

10. Example of Line Plot
    plt.plot(
    [1,2,3,4],
    [10,20,30,40]
    )
    plt.show()

---

11. How do you change line color?
    plt.plot(x,y,color="red")

---

12. How do you change line style?
    plt.plot(x,y,linestyle="--")
    Alternative:
    plt.plot(x,y,"--")

---

13. How do you change line width?
    plt.plot(
    x,
    y,
    linewidth=3
    )

---

TITLES & LABELS 14. How do you add a title?
plt.title("Sales Report")

---

15. How do you label X-axis?
    plt.xlabel("Month")

---

16. How do you label Y-axis?
    plt.ylabel("Sales")

---

17. Why are labels important?
    Answer:
    Labels help users understand graph meaning.

---

SCATTER PLOT 18. What is a Scatter Plot?
Answer:
A graph that shows individual data points.
Use Cases:
• Correlation analysis
• ML feature relationships

---

19. Example
    plt.scatter(x,y)
    plt.show()

---

20. Why use Scatter Plot in AI?
    Answer:
    To analyze relationships between features.
    Example:
    Age vs Salary
    Height vs Weight
    Experience vs Salary

---

BAR CHART 21. What is a Bar Chart?
Answer:
A graph using bars to compare categories.

---

22. Example
    names = ["A","B","C"]

marks = [80,90,70]

plt.bar(
names,
marks
)
plt.show()

---

23. When do we use Bar Charts?
    Answer:
    • Comparing categories
    • Department sales
    • Student marks

---

HISTOGRAM 24. What is a Histogram?
Answer:
A graph showing data distribution.

---

25. Example
    plt.hist(data)
    plt.show()

---

26. Why is Histogram important in AI?
    Answer:
    To understand:
    • Data distribution
    • Skewness
    • Outliers

---

PIE CHART 27. What is a Pie Chart?
Answer:
A chart representing proportions of a whole.

---

28. Example
    plt.pie(
    values,
    labels=labels
    )
    plt.show()

---

29. When should Pie Charts be used?
    Answer:
    When showing percentages or proportions.

---

SUBPLOTS 30. What is a Subplot?
Answer:
Multiple plots inside one figure.

---

31. Example
    plt.subplot(1,2,1)

plt.plot(x,y)

---

32. Why use Subplots?
    Answer:
    To compare multiple visualizations together.

---

LEGEND & GRID 33. What is a Legend?
Answer:
A legend identifies graph elements.
plt.legend()

---

34. Example
    plt.plot(
    x,
    y,
    label="Sales"
    )

plt.legend()

---

35. What is Grid?
    Answer:
    Grid adds reference lines to a graph.
    plt.grid(True)

---

FIGURE SIZE 36. How do you change figure size?
plt.figure(
figsize=(8,5)
)

---

37. What does figsize=(8,5) mean?
    Answer:
    width = 8 inches

height = 5 inches

---

SAVING GRAPHS 38. How do you save a graph?
plt.savefig(
"graph.png"
)

---

39. Common formats?
    png
    jpg
    pdf
    svg

---

AI ENGINEER IMPORTANT QUESTIONS 40. What graph is most used in AI projects?
Answer:
• Histogram
• Scatter Plot
• Line Plot
• Bar Plot

---

41. Why use Histogram in ML?
    Answer:
    To detect:
    • Skewed data
    • Outliers
    • Feature distribution

---

42. Why use Scatter Plot in ML?
    Answer:
    To identify feature relationships.

---

43. Why use Line Plot?
    Answer:
    To track trends over time.
    Examples:
    Loss Curve
    Accuracy Curve

---

44. How do you visualize model training?
    plt.plot(loss)

---

45. How do you visualize accuracy?
    plt.plot(accuracy)

---

46. What is EDA?
    Answer:
    EDA stands for Exploratory Data Analysis.
    Explanation:
    Process of understanding data before modeling.

---

47. Which library works closely with Matplotlib?
    Answer:
    Seaborn

---

48. Difference Between Matplotlib and Seaborn
    Matplotlib Seaborn
    Low Level High Level
    More Control Easier
    More Code Less Code

---

49. Why learn Matplotlib before Seaborn?
    Answer:
    Seaborn is built on top of Matplotlib.
    Understanding Matplotlib makes Seaborn easier.

---

50. Why is Matplotlib important for AI Engineers?
    Answer:
    Because it helps:
    • Analyze datasets
    • Detect data issues
    • Understand feature behavior
    • Monitor model performance

---

ONE-LINE SUMMARY
plot()
Line Graph
scatter()
Scatter Plot
bar()
Bar Chart
hist()
Histogram
pie()
Pie Chart
title()
Graph Title
xlabel()
X-axis Name
ylabel()
Y-axis Name
legend()
Graph Labels
grid()
Reference Lines
savefig()
Save Graph
show()
Display Graph

---

PRIORITY FOR AI ENGINEERS
Topic Priority
Line Plot ⭐⭐⭐⭐⭐
Scatter Plot ⭐⭐⭐⭐⭐
Histogram ⭐⭐⭐⭐⭐
Labels & Titles ⭐⭐⭐⭐⭐
Figure Size ⭐⭐⭐⭐
Bar Chart ⭐⭐⭐⭐
Saving Graphs ⭐⭐⭐⭐
Legends & Grid ⭐⭐⭐⭐
Pie Chart ⭐⭐⭐
Subplots ⭐⭐⭐
QUICK MEMORY TRICK
• Line Plot → Trend
• Scatter Plot → Relationship
• Histogram → Distribution
• Bar Chart → Comparison
• Pie Chart → Percentage
• Legend → Identify Lines
• Grid → Easy Reading
• savefig() → Save Plot
• show() → Display Plot
These topics cover about 95% of Matplotlib used by AI Engineers, Data Scientists, ML Engineers, and Data Analysts in real-world projects and interviews.
