import os
import re
import pandas as pd

df = pd.read_csv("hash_map.csv")
print(df)

#dim_red_methods = ["lsa","pca","umap","tsne"]
#dim_red_method_rx = re.compile("(lsa)|(pca)|(umap)|(tsne)")

dim_red_method_rx = re.compile("lsa|pca|umap|tsne")
normalization_method_rx = re.compile("normalize_total|tfidf")
plot_rx = re.compile("plot")

dim_red_method_list = []
norm_method_list    = []
plot_status_list    = []

for idx, row in df.iterrows():
    txt = row["path"]

    #Dimensionality reduction
    dim_red_method_str = ""
    obj = dim_red_method_rx.findall(txt)
    if obj:
        print(obj)
        dim_red_method_str = ", ".join(obj)
    dim_red_method_list.append(dim_red_method_str)

    #Normalization method
    obj = normalization_method_rx.search(txt)
    norm_method = ""
    if obj:
        norm_method = obj.group(0)
    norm_method_list.append(norm_method)

    #Plot method
    obj = plot_rx.search(txt)
    plot_status = False
    if obj:
        plot_status = True
    plot_status_list.append(plot_status)


df["dim_red_method"] = dim_red_method_list
df["norm_method"]    = norm_method_list
df["plot_status"]    = plot_status_list

print(df)
