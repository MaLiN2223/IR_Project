import pandas as pd

df = pd.read_csv("C:/Users/Malin/Downloads/data.csv")
print(df.groupby("Vaccine").count())
