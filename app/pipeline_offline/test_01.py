import networkx as nx
G = nx.read_gpickle("indices/graph_raw.gpickle")
print(len(G), "nodes,", G.size(), "edges")
