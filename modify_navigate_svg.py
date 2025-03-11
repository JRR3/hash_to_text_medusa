import os
import re
import numpy as np
import pandas as pd

#====================================================
#Read the hash map and extract relevant information
#====================================================

df = pd.read_csv("hash_map.csv")

#dim_red_methods = ["lsa","pca","umap","tsne"]
#dim_red_method_rx = re.compile("(lsa)|(pca)|(umap)|(tsne)")

dim_red_method_rx = re.compile("lsa|pca|umap|tsne")
normalization_method_rx = re.compile("normalize_total|tfidf")
plot_rx        = re.compile("plot_embeddings")
tsne_config_rx = re.compile("px~\d+")
umap_config_rx = re.compile("m_dist~0.\d+_n_neigh~\d+")
polygon_rx     = re.compile(r'^<polygon')

def increase_polygon_height(polygon_line, height_increase):

    # Extract the points attribute using a regular expression
    match = re.findall(r'points="([^"]+)"', polygon_line)

    if not match:
        return polygon_line  # Return the original line if no points attribute is found

    points_str = match.group(1)
    points = [
        tuple(map(float,
                  pair.split(','))
                  ) for pair in points_str.split()
    ]

    # Find the min and max y-coordinates
    min_y = min(y for x, y in points)
    max_y = max(y for x, y in points)

    # Calculate the current height
    current_height = max_y - min_y

    # Calculate the new height
    new_height = current_height + height_increase

    # Calculate the new max_y
    new_max_y = min_y + new_height

    # Modify the y-coordinates of the points
    new_points = []
    for x, y in points:
        if y == max_y:
            new_points.append((x, new_max_y))
        else:
            new_points.append((x, y))

    # Reconstruct the points string
    new_points_str = ' '.join([f'{x},{y}' for x, y in new_points])

    # Replace the points attribute in the original line
    new_polygon_line = polygon_line.replace(
        points_str, new_points_str)

    return new_polygon_line

embedding_method_list = []

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
    embedding_method_str = ""
    if obj:
        if len(obj) == 1:
            dim_red_method_str = obj[0]
            embedding_method_str = ""
        elif len(obj) == 2:
            dim_red_method_str = obj[0]
            embedding_method_str = obj[1]
        elif 2 < len(obj):
            raise ValueError("Unexpected number of dim reds.")

    dim_red_method_list.append(dim_red_method_str)
    embedding_method_list.append(embedding_method_str)

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
df["embed_method"]   = embedding_method_list
df["norm_method"]    = norm_method_list
df["plot_status"]    = plot_status_list
df["embed_config"]   = embed_config_list

# df["tsne_config"]    = tsne_config_list
# df["umap_config"]    = umap_config_list

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
tmc_rx      = re.compile("<text.+GenerateTMC_.+</text>")
hash_rx     = re.compile("<text.+hash: ?(\w+) ?</text>")
y_pos_rx    = re.compile("y=\"([-]?\d+[.]?\d*)\"")

source = "navigate.svg"
target = "x_navigate.svg"

pre_norm_status    = False
pre_dim_red_status = False
pre_embed_status   = False
pre_plot_emb_status= False
pre_tmc_status     = False
y_old_pos          = 0
y_pos              = 0

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

            #==========TMC status
            tmc_status = False
            obj = tmc_rx.match(new_line)
            if obj:
                #print(new_line)
                tmc_status = True

            #==========y pos status
            y_pos_status = False
            obj = y_pos_rx.search(new_line)
            if obj:
                #print(new_line)
                y_old_pos = y_pos
                y_pos_status = True
                y_pos = obj.group(1)
                y_pos = np.float32(y_pos)

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

                #==========Replace the hash string
                h_string = "hash: "
                new_line = re.sub(h_string,"",new_line)
    

            modify_status = False
            #==================================Modifications

            #Change the norm and the TMC lines.
            cond_1 = hash_status and pre_norm_status
            cond_2 = hash_status and pre_tmc_status
            if cond_1 or cond_2:
                modify_status = True
                mask = df["hash"] == hash_str
                row = df[mask].iloc[0]
                norm_method = row["norm_method"]
                new_line = re.sub(hash_str,
                                  norm_method,
                                  new_line)

            if hash_status and pre_dim_red_status:
                modify_status = True
                mask = df["hash"] == hash_str
                row = df[mask].iloc[0]
                dim_red_method = row["dim_red_method"]
                new_line = re.sub(hash_str,
                                  dim_red_method,
                                  new_line)

            cond_1 = hash_status and pre_embed_status
            cond_2 = hash_status and pre_plot_emb_status
            if cond_1 or cond_2:
                modify_status = True
                mask = df["hash"] == hash_str
                row = df[mask].iloc[0]
                embed_method = row["embed_method"]
                embed_config = row["embed_config"]
                txt = embed_method
                txt += "("
                txt += embed_config
                txt += ")"
                new_line = re.sub(hash_str,
                                  txt,
                                  new_line)

            pre_norm_status    = norm_status
            pre_tmc_status     = tmc_status
            pre_dim_red_status = dim_red_status
            pre_embed_status   = embed_status
            pre_plot_emb_status= plot_embeddings_status

            print("------------------")
            if modify_status:
                # We need to modify the y value of the
                # new line that we are going to add 
                # below the hash.
                print(line)
                print(f"{y_old_pos=}")
                print(f"{y_pos=}")
                delta_y = y_pos - y_old_pos
                y_pos_new = y_pos + delta_y
                print(f"{y_pos_new=}")
                y_pos_new_str = "y=\"" + str(y_pos_new) + "\""
                new_line = re.sub(y_pos_rx,
                                  y_pos_new_str,
                                  new_line)
                print(new_line)
                f_out.write(line)
                f_out.write(new_line)
            else:
                f_out.write(new_line)
                #print(new_line)
