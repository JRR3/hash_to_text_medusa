import os
import re
import pandas as pd

#====================================================
#Read the hash map and extract relevant information
#====================================================

df = pd.read_csv("hash_map.csv")

#dim_red_methods = ["lsa","pca","umap","tsne"]
#dim_red_method_rx = re.compile("(lsa)|(pca)|(umap)|(tsne)")

dim_red_method_rx = re.compile("lsa|pca|umap|tsne")
normalization_method_rx = re.compile("normalize_total|tfidf")
plot_rx = re.compile("plot_embeddings")
tsne_config_rx = re.compile("px~\d+")
umap_config_rx = re.compile("m_dist~0.\d+_n_neigh~\d+")

dim_red_method_list = []
norm_method_list    = []
plot_status_list    = []
tsne_config_list    = []
umap_config_list    = []
embed_config_list   = []

for idx, row in df.iterrows():
    txt = row["path"]

    #-------------------------------------
    #Dimensionality reduction
    #-------------------------------------
    obj = dim_red_method_rx.findall(txt)
    dim_red_method_str = ""
    if obj:
        if len(obj) == 1:
            dim_red_method_str = obj[0]
        elif len(obj) == 2:
            dim_red_method_str = obj[0]

    dim_red_method_list.append(dim_red_method_str)

    #-------------------------------------
    #Normalization method
    #-------------------------------------
    obj = normalization_method_rx.search(txt)
    norm_method = ""
    if obj:
        norm_method = obj.group(0)
    norm_method_list.append(norm_method)

    #-------------------------------------
    #Embedding configuration
    #-------------------------------------
    embed_config = ""

    #tsne config
    obj = tsne_config_rx.search(txt)
    if obj:
        embed_config = obj.group(0)

    #umap config
    obj = umap_config_rx.search(txt)
    if obj:
        embed_config = obj.group(0)

    embed_config_list.append(embed_config)
    #-------------------------------------

    #Plot method
    obj = plot_rx.search(txt)
    plot_status = False
    if obj:
        plot_status = True
    plot_status_list.append(plot_status)


df["dim_red_method"] = dim_red_method_list
df["norm_method"]    = norm_method_list
df["plot_status"]    = plot_status_list
# df["tsne_config"]    = tsne_config_list
# df["umap_config"]    = umap_config_list
df["embed_config"]    = embed_config_list

df.to_csv("table.csv", index=False)


#====================================================
#Modify the navigation file.
#====================================================

#link_str = "/run/user/1000/gvfs/sftp:host=142.1.33.110,user=hoseoklee//mnt/data0/javier/repos/10x_10k_pbmc/outputs"
link_str = "/run/user/1000/gvfs/sftp:"
link_str+= "host=142.1.33.110,user=hoseoklee/"
link_str+= "/mnt/data0/javier/repos/10x_10k_pbmc/outputs"

norm_rx     = re.compile("<text.+normalization_.+</text>")
dim_red_rx  = re.compile("<text.+dim_red_.+</text>")
embed_rx    = re.compile("<text.+Embeddings_.+</text>")
plot_emb_rx = re.compile("<text.+plot_embeddings_.+</text>")
hash_rx     = re.compile("<text.+hash: ?(\w+) ?</text>")

source = "navigate.svg"
target = "x_navigate.svg"

pre_norm_status    = False
pre_dim_red_status = False
pre_embed_status   = False
pre_plot_emb_status= False

with open(target, "w") as f_out:
    with open(source, "r") as f_in:
        for line in f_in:
            #==========Replace the link string
            new_line = re.sub(link_str,".",line)

            #==========Norm status
            norm_status = False
            obj = norm_rx.match(new_line)
            if obj:
                #print(new_line)
                norm_status = True

            #==========DimRed status
            dim_red_status = False
            obj = dim_red_rx.match(new_line)
            if obj:
                #print(new_line)
                dim_red_status = True

            #==========Embed status
            embed_status = False
            obj = embed_rx.match(new_line)
            if obj:
                #print(new_line)
                embed_status = True

            #==========plot_embeddings status
            plot_embeddings_status = False
            obj = plot_emb_rx.match(new_line)
            if obj:
                #print(new_line)
                plot_embeddings_status = True

            #==========hash status
            hash_status = False
            obj = hash_rx.match(new_line)
            if obj:
                #print(new_line)
                hash_str = obj.group(1)
                hash_status = True

            if hash_status and pre_norm_status:
                mask = df["hash"] == hash_str
                row = df[mask].iloc[0]
                norm_method = row["norm_method"]
                new_line = re.sub(hash_str,
                                  norm_method,
                                  new_line)

            if hash_status and pre_dim_red_status:
                mask = df["hash"] == hash_str
                row = df[mask].iloc[0]
                dim_red_method = row["dim_red_method"]
                new_line = re.sub(hash_str,
                                  dim_red_method,
                                  new_line)

            cond_1 = hash_status and pre_embed_status
            cond_2 = hash_status and pre_plot_emb_status
            if cond_1 or cond_2:
                mask = df["hash"] == hash_str
                row = df[mask].iloc[0]
                embed_method = row["dim_red_method"]
                embed_config = row["embed_config"]
                txt = embed_method
                txt += "("
                txt += embed_config
                txt += ")"
                new_line = re.sub(hash_str,
                                  txt,
                                  new_line)

            pre_norm_status    = norm_status
            pre_dim_red_status = dim_red_status
            pre_embed_status   = embed_status
            pre_plot_emb_status= plot_embeddings_status

            f_out.write(new_line)
