import osmnx as ox

# Specify the city or area you are interested in
place_name = "João Pessoa, Brazil"

# Download the street network data
G = ox.graph_from_place(place_name, network_type='drive')

# Create a mapping from OSM node IDs to sequential integers starting from 1
osm_node_ids = list(G.nodes)
node_id_mapping = {osm_id: idx for idx, osm_id in enumerate(osm_node_ids, start=1)}

# Open a file to write the output
with open('city_data.pl.', 'w') as f:
    # Write the locations (nodes)
    f.write('% Locations in the city (Nodes)\n')
    for osm_id, new_id in node_id_mapping.items():
        f.write(f"location({new_id}, 'Intersection {new_id}').\n")

    f.write('\n% Streets between locations (Edges with Distances as Weights)\n')
    f.write('% street(Node1, Node2, Distance).\n')

    # Write the streets (edges)
    for u, v, data in G.edges(data=True):
        # Map the OSM node IDs to your sequential node IDs
        u_id = node_id_mapping[u]
        v_id = node_id_mapping[v]
        # Get the length of the edge in kilometers
        distance = data.get('length', 0) / 1000.0
        # Get the street name, default to 'Unknown' if not available
        name = data.get('name', 'Unknown')
        # If the name is a list (multiple names), join them into a string
        if isinstance(name, list):
            name = ', '.join(name)
        # Escape single quotes in the street name to avoid syntax errors
        name = name.replace("'", "\\'")
        # Write the street information including the name
        f.write(f"street({u_id}, {v_id}, {distance:.2f}, '{name}').\n")


