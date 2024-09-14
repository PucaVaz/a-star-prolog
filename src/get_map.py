import osmnx as ox

class CityGraphBuilder:
    def __init__(self, place_name):
        self.place_name = place_name
        self.graph = ox.graph_from_place(self.place_name, network_type='drive')
        self.node_id_mapping = {}
        self.node_coord_mapping = {}
        self.edges = []

    def build_node_mapping(self):
        osm_node_ids = list(self.graph.nodes)
        self.node_id_mapping = {osm_id: idx for idx, osm_id in enumerate(osm_node_ids, start=1)}
        self.node_coord_mapping = {
            idx: (self.graph.nodes[osm_id]['y'], self.graph.nodes[osm_id]['x'])
            for osm_id, idx in self.node_id_mapping.items()
        }
        return self

    def build_edges(self):
        for u, v, data in self.graph.edges(data=True):
            u_id = self.node_id_mapping[u]
            v_id = self.node_id_mapping[v]
            distance = data.get('length', 0) / 1000.0
            name = data.get('name', 'Unknown')
            if isinstance(name, list):
                name = ', '.join(name)
            name = str(name).replace("'", "\\'")
            self.edges.append((u_id, v_id, distance, name))
        return self

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write('% Locations in the city (Nodes)\n')
            for osm_id, new_id in self.node_id_mapping.items():
                f.write(f"location({new_id}, 'Intersection {new_id}').\n")

            f.write('\n% Streets between locations (Edges with Distances as Weights)\n')
            f.write('% street(Node1, Node2, Distance, Name).\n')

            for u_id, v_id, distance, name in self.edges:
                f.write(f"street({u_id}, {v_id}, {distance:.2f}, '{name}').\n")

    def save_node_coordinates(self, filename):
        with open(filename, 'w') as f:
            f.write('node_id,latitude,longitude\n')
            for node_id, (lat, lon) in self.node_coord_mapping.items():
                f.write(f"{node_id},{lat},{lon}\n")

# Usage
place_name = "João Pessoa, Brazil"
builder = CityGraphBuilder(place_name)
builder.build_node_mapping().build_edges()
builder.save_to_file('city_data.pl')
builder.save_node_coordinates('node_coordinates.csv')
