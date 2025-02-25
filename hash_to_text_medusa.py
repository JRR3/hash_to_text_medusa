import os
import re
import pandas as pd
df = pd.read_csv("hash_map.csv")
print(df)
#methods = ["lsa","pca","umap","tsne"]
#method_rx = re.compile("(lsa)|(pca)|(umap)|(tsne)")
method_rx = re.compile("lsa|pca|umap|tsne")
operation = ["plot","TMC"]
method_list = []
normalization_list = []
for idx, row in df.iterrows():
    txt = row["path"]
    method_str = ""
    obj = method_rx.findall(txt)
    if obj:
        print(obj)
        method_str = ", ".join(obj)
    method_list.append(method_str)

df["method"] = method_list
print(df)
