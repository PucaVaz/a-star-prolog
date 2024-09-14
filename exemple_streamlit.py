import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import osmnx as ox
from shapely.geometry import LineString
import streamlit as st
import re
import difflib
from src.astart_prolog_adapter import AstarPrologAdapter
import folium
from streamlit_folium import st_folium


def main():
    st.title("Find the street path using A* algorithm implemented in Prolog")
    if 'node_coord_mapping' not in st.session_state:
        st.session_state['node_coord_mapping'] = load_node_coordinates('./src/node_coordinates.csv')

    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state['step'] = 1

    # Reset button
    if st.button('Reset'):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Load street nodes
    if 'street_nodes' not in st.session_state:
        st.session_state['street_nodes'] = get_street_nodes('./src/city_data.pl')

    if st.session_state['step'] == 1:
        step1()
    elif st.session_state['step'] == 2:
        step2()
    elif st.session_state['step'] == 3:
        step3()
    elif st.session_state['step'] == 4:
        step4()
    elif st.session_state['step'] == 5:
        step5()

def step1():
    st.header("Enter Street Names")
    with st.form(key='street_form'):
        start_street_input = st.text_input("Enter the starting street name:")
        end_street_input = st.text_input("Enter the ending street name:")
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        st.session_state['start_street_input'] = start_street_input
        st.session_state['end_street_input'] = end_street_input
        st.session_state['step'] = 2
        st.rerun()

def step2():
    st.header("Select Streets")
    start_street_input = st.session_state['start_street_input']
    end_street_input = st.session_state['end_street_input']
    street_nodes = st.session_state['street_nodes']

    # Find best matches
    start_matches = find_best_match(start_street_input, street_nodes)
    end_matches = find_best_match(end_street_input, street_nodes)

    if not start_matches:
        st.error(f"No similar street names found for '{start_street_input}'.")
        st.stop()
    if not end_matches:
        st.error(f"No similar street names found for '{end_street_input}'.")
        st.stop()

    if len(start_matches) == 1:
        st.session_state['start_street'] = start_matches[0]
    else:
        start_street = st.selectbox("Select the starting street:", start_matches)
        st.session_state['start_street'] = start_street

    if len(end_matches) == 1:
        st.session_state['end_street'] = end_matches[0]
    else:
        end_street = st.selectbox("Select the ending street:", end_matches)
        st.session_state['end_street'] = end_street

    if 'start_street' in st.session_state and 'end_street' in st.session_state:
        st.session_state['step'] = 3
        st.rerun()
    else:
        st.stop()

def step3():
    st.header("Select Node Pairs")
    street_nodes = st.session_state['street_nodes']
    start_street = st.session_state['start_street']
    end_street = st.session_state['end_street']

    start_node_options = get_node_options(start_street, street_nodes)
    end_node_options = get_node_options(end_street, street_nodes)

    if len(start_node_options) == 1:
        st.session_state['start_node_pair'] = start_node_options[0]
    else:
        start_node_pair_strs = [f"Node {n1} <--> Node {n2}" for n1, n2 in start_node_options]
        start_node_pair_str = st.selectbox("Select the node pair for the starting street:", start_node_pair_strs)
        idx = start_node_pair_strs.index(start_node_pair_str)
        st.session_state['start_node_pair'] = start_node_options[idx]

    if len(end_node_options) == 1:
        st.session_state['end_node_pair'] = end_node_options[0]
    else:
        end_node_pair_strs = [f"Node {n1} <--> Node {n2}" for n1, n2 in end_node_options]
        end_node_pair_str = st.selectbox("Select the node pair for the ending street:", end_node_pair_strs)
        idx = end_node_pair_strs.index(end_node_pair_str)
        st.session_state['end_node_pair'] = end_node_options[idx]

    if 'start_node_pair' in st.session_state and 'end_node_pair' in st.session_state:
        st.session_state['step'] = 4
        st.rerun()
    else:
        st.stop()

def step4():
    st.header("Select Nodes")
    start_node_pair = st.session_state['start_node_pair']
    end_node_pair = st.session_state['end_node_pair']

    n1, n2 = start_node_pair
    start_node = st.selectbox("Select the node for the starting street:", [n1, n2])
    st.session_state['start_node'] = start_node

    n1, n2 = end_node_pair
    end_node = st.selectbox("Select the node for the ending street:", [n1, n2])
    st.session_state['end_node'] = end_node

    if 'start_node' in st.session_state and 'end_node' in st.session_state:
        st.session_state['step'] = 5
        st.rerun()
    else:
        st.stop()

def step5():
    st.header("Shortest path result")
    start_node = st.session_state['start_node']
    end_node = st.session_state['end_node']
    start_street = st.session_state['start_street']
    end_street = st.session_state['end_street']
    node_coord_mapping = st.session_state['node_coord_mapping']
    street_nodes = st.session_state['street_nodes']

    try:
        # Run the Prolog command
        path, cost = AstarPrologAdapter().find_path(start_node, end_node)

        # Display the results
        st.success(f"Shortest path from '{start_street}' to '{end_street}':")
        st.write("Path (node IDs):", path)
        st.write("Total cost:", cost)

        # Get coordinates of the nodes in the path
        path_coords = [node_coord_mapping[node_id] for node_id in path]

        # Create a Folium map centered on the path
        avg_lat = sum([lat for lat, lon in path_coords]) / len(path_coords)
        avg_lon = sum([lon for lat, lon in path_coords]) / len(path_coords)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

        # Add the path as a PolyLine
        folium.PolyLine(locations=path_coords, color='blue', weight=5).add_to(m)

        # Add markers for the start and end nodes
        folium.Marker(location=path_coords[0], popup='Start', icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(location=path_coords[-1], popup='End', icon=folium.Icon(color='red')).add_to(m)

        # Display the map in Streamlit
        st_folium(m, width=700, height=500)
    except FileNotFoundError:
        st.error("SWI-Prolog executable 'swipl' not found. Please ensure SWI-Prolog is installed and added to your PATH.")


def get_street_nodes(prolog_file):
    street_nodes = []
    pattern = re.compile(r"street\((\d+),\s*(\d+),[^,]*,\s*'([^']+)'\)\.")
    with open(prolog_file, 'r') as file:
        for line in file:
            match = pattern.match(line.strip())
            if match:
                node1 = int(match.group(1))
                node2 = int(match.group(2))
                street_name = match.group(3)
                street_nodes.append((street_name, node1, node2))
    return street_nodes

def find_best_match(input_name, street_nodes):
    street_names = list(set([sn[0] for sn in street_nodes]))
    matches = difflib.get_close_matches(input_name, street_names, n=5, cutoff=0.5)
    return matches

def get_node_options(street_name, street_nodes):
    options = [(node1, node2) for name, node1, node2 in street_nodes if name == street_name]
    return options

def load_node_coordinates(filename):
    df = pd.read_csv(filename)
    node_coord_mapping = {
        row['node_id']: (row['latitude'], row['longitude'])
        for _, row in df.iterrows()
    }
    return node_coord_mapping

if __name__ == "__main__":
    main()
