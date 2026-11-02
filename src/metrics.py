import networkx as nx
import osmnx as ox

def comparison(city,g,grid):
    undirected=ox.convert.to_undirected(g)
    return {'city':city,'Walking network length (km)':sum(d['length'] for _,_,d in undirected.edges(data=True))/1000,'Medical facilities per grid':float(grid.medical_count.mean()),'15-min medical grid coverage (%)':float((grid.medical_min<=15).mean()*100),'Connected components':nx.number_connected_components(undirected)}
