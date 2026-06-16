import numpy as np

# -------------------------------
# 📝 Task 1: Create Arrays
# -------------------------------
oned = np.arange(1, 11)   # 1D array from 1 to 10
print("Task 1 - 1D Array:", oned)

twod = np.arange(1, 10).reshape(3, 3)   # 2D array (3x3)
print("Task 1 - 2D Array:\n", twod)

# -------------------------------
# 🔄 Task 2: Array Operations
# -------------------------------
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([10, 20, 30, 40, 50])

print("\nTask 2 - Add:", arr1 + arr2)
print("Task 2 - Subtract:", arr2 - arr1)
print("Task 2 - Multiply:", arr1 * arr2)
print("Task 2 - Divide:", arr2 / arr1)
print("Task 2 - Square:", np.square(arr1))

# -------------------------------
# 🎯 Task 3: Indexing & Slicing
# -------------------------------
print("\nTask 3 - First 5 elements:", oned[:5])
print("Task 3 - Second row of 2D array:", twod[1])
print("Task 3 - Alternate elements:", oned[::2])

# -------------------------------
# 📊 Task 4: Statistical Functions
# -------------------------------
stats_arr = np.array([5, 10, 15, 20, 25])
print("\nTask 4 - Mean:", np.mean(stats_arr))
print("Task 4 - Median:", np.median(stats_arr))
print("Task 4 - Std Dev:", np.std(stats_arr))
print("Task 4 - Max:", np.max(stats_arr))
print("Task 4 - Min:", np.min(stats_arr))

# -------------------------------
# 🔍 Task 5: Boolean Masking & Filtering
# -------------------------------
mask_arr = np.arange(1, 21)
print("\nTask 5 - Even numbers:", mask_arr[mask_arr % 2 == 0])
print("Task 5 - Numbers > 10:", mask_arr[mask_arr > 10])
