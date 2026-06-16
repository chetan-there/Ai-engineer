import pandas as pd

data = pd.read_csv("C:\proj-workspace\Ai-engg\Ai-enginner\python_fundamentals\practice\students.csv")

df = pd.DataFrame(data)

filter = df[
    (df["age"] > 25)
    &
    (df["salary"] > 50000)
]

print(filter)