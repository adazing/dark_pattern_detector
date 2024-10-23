import pandas as pd

data = pd.read_csv(open("new_data.csv", "r", encoding="utf8"))
# print(data.head())
new_data = data[["Text"]]
new_data["class"] = "Not Dark Pattern"
print(new_data)
new_data.to_csv("no_dp_data.csv", index=False, header=False)

