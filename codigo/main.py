import pandas as pd
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt
import dijkstra

def create_graph():

    df = pd.read_csv('calles_de_medellin_con_acoso.csv', sep=";")
    risk_media = df["harassmentRisk"].mean()
    df["harassmentRisk"].fillna(risk_media, inplace=True)
    
    G = nx.DiGraph()
    
    vertices = []
    destinations = []
    
    for i in range(len(df)):
        G.add_node(df.iloc[i]["origin"])
        G.add_node(df.iloc[i]["destination"])
        vertices.append(df.iloc[i]["origin"])
        destinations.append(df.iloc[i]["destination"])
    
    for i in range(len(vertices)):
        v1 = vertices[i]
        v2 = destinations[i]
        distance = df.iloc[i]["length"]
        double_via = df.iloc[i]["oneway"]
        risk = df.iloc[i]["harassmentRisk"]
        geometry = df.iloc[i]["geometry"]
        new_weight = distance * (risk * 10)
        G.add_edge(v1, v2, weight=new_weight, geometry=geometry, old_distance=distance)
        if double_via:
            G.add_edge(v2, v1, weight=new_weight, geometry=geometry, old_distance=distance)

    return G

def print_graph(G):
    d = nx.to_dict_of_dicts(G)
    i = 1
    for keys, values in d.items():
        print(i)
        print(keys + " connected to")
        for value in values:
            print("=> " + value + ": {'weight': " + str(values[value]["weight"]) + "}"+ ", {'original weight': " + str(values[value]["old_distance"]) + "}")
        print("")
        i += 1

def print_path(G):
    d = nx.to_dict_of_dicts(G)

    starting_node = input("Write the starting node: ")

    while starting_node not in d.keys():
        starting_node = input("\nWrite a valid starting node: ")

    destination_node = input("\nWrite the destination node: ")

    while destination_node not in d.keys():
        destination_node = input("\nWrite a valid destination node: ")
        
    while starting_node == destination_node:
        print("\nThe starting node and the destination node are the same.")
        destination_node = input("\nWrite another destination node: ")

        while destination_node not in d.keys():
            destination_node = input("\nWrite a valid destination node: ")

    path = dijkstra.dijkstra_path(G, starting_node, destination_node)
    cost = dijkstra.dijkstra_path_length(G, starting_node, destination_node)

    print("\nThe path found is:\n")
    
    print(" -> ".join(path))
    print("\nCost: " + str(cost)+"\n")

    path_geometry = []

    for i in range(len(path)-1):
        path_geometry.append(G[path[i]][path[i+1]]["geometry"])

    return [starting_node, destination_node, path_geometry]
    
def generate_plot(starting_node, destination_node, path_geometry):

    path_geometry = pd.DataFrame(path_geometry, columns =['geometry'])
    path_geometry['geometry'] = path_geometry['geometry'].apply(wkt.loads)
    path_geometry = gpd.GeoDataFrame(path_geometry)
    area = pd.read_csv('poligono_de_medellin.csv',sep=';')
    area['geometry'] = area['geometry'].apply(wkt.loads)
    area = gpd.GeoDataFrame(area)
    
    edges = pd.read_csv('calles_de_medellin_con_acoso.csv',sep=';')
    edges['geometry'] = edges['geometry'].apply(wkt.loads)
    edges = gpd.GeoDataFrame(edges)
    
    fig, ax = plt.subplots(figsize=(12,8))
    edges.plot(ax=ax, linewidth=0.3, missing_kwds={'color': 'dimgray'})
    area.plot(ax=ax, facecolor='black')
    path_geometry.plot(ax=ax,linewidth=2, cmap = 'hsv')
    
    plt.title("Safe and shortest route from " + starting_node + " to " + destination_node)
    plt.tight_layout()
    plt.savefig(starting_node + "_to_" + destination_node + ".png")

def main():
    G = create_graph()
    print_graph(G)
    inputs_plot = print_path(G)
    generate_plot(inputs_plot[0], inputs_plot[1], inputs_plot[2])


main()