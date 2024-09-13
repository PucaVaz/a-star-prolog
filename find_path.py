import subprocess
import sys
import re
import difflib

def main():
    # Load street names and node pairs from city_data.pl
    street_nodes = get_street_nodes('city_data.pl')

    # Prompt the user for the starting and ending street names
    start_street_input = input("Enter the starting street name: ")
    end_street_input = input("Enter the ending street name: ")

    # Find the best matches for the input street names
    start_matches = find_best_match(start_street_input, street_nodes)
    end_matches = find_best_match(end_street_input, street_nodes)

    # Handle no matches
    if not start_matches:
        print(f"No similar street names found for '{start_street_input}'.")
        sys.exit(1)
    if not end_matches:
        print(f"No similar street names found for '{end_street_input}'.")
        sys.exit(1)

    # Allow the user to select the correct street
    start_street = select_street(start_matches, 'starting')
    end_street = select_street(end_matches, 'ending')

    # Get node options for the selected streets
    start_node_options = get_node_options(start_street, street_nodes)
    end_node_options = get_node_options(end_street, street_nodes)

    # Allow the user to select specific node pairs if multiple options are available
    start_node = select_node_pair(start_node_options, 'starting')
    end_node = select_node_pair(end_node_options, 'ending')

    # Construct the Prolog goal
    prolog_goal = (
        f"astar({start_node}, {end_node}, Path, Cost), "
        f"write(Path), nl, write(Cost), halt."
    )

    # Construct the command to run SWI-Prolog
    command = [
        'swipl',
        '-q',  # Suppress the welcome message
        '-s', 'astar_program.pl',
        '-g', prolog_goal
    ]

    try:
        # Run the Prolog command
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check for errors
        if result.returncode != 0:
            print("An error occurred while running the Prolog query:")
            print(result.stderr)
            sys.exit(1)

        # Capture the output
        output = result.stdout.strip()

        # Parse the output to extract the path and cost
        lines = output.split('\n')
        if len(lines) >= 2:
            path_str = lines[0]
            cost_str = lines[1]

            # Convert the path string to a Python list
            path = parse_prolog_list(path_str)
            cost = float(cost_str)

            # Display the results
            print(f"\nShortest path from '{start_street}' to '{end_street}':")
            print("Path (node IDs):", path)
            print("Total cost:", cost)
        else:
            print("No path found between the specified nodes.")

    except FileNotFoundError:
        print("SWI-Prolog executable 'swipl' not found. Please ensure SWI-Prolog is installed and added to your PATH.")
        sys.exit(1)

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

def select_street(matches, street_type):
    if len(matches) == 1:
        return matches[0]
    else:
        print(f"\nMultiple matches found for the {street_type} street name. Please select one:")
        for idx, name in enumerate(matches, 1):
            print(f"{idx}. {name}")
        while True:
            try:
                selection = int(input(f"Enter the number of your choice (1-{len(matches)}): "))
                if 1 <= selection <= len(matches):
                    return matches[selection - 1]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

def get_node_options(street_name, street_nodes):
    options = [(node1, node2) for name, node1, node2 in street_nodes if name == street_name]
    return options

def select_node_pair(node_options, street_type):
    if len(node_options) == 1:
        return node_options[0][0]  # Choose one of the nodes
    else:
        print(f"\nMultiple node pairs found for the {street_type} street '{node_options[0][0]}'. Please select one:")
        for idx, (node1, node2) in enumerate(node_options, 1):
            print(f"{idx}. Node {node1} <--> Node {node2}")
        while True:
            try:
                selection = int(input(f"Enter the number of your choice (1-{len(node_options)}): "))
                if 1 <= selection <= len(node_options):
                    # Let the user choose which node to use as the start/end
                    selected_pair = node_options[selection - 1]
                    node = choose_node_from_pair(selected_pair, street_type)
                    return node
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

def choose_node_from_pair(node_pair, street_type):
    node1, node2 = node_pair
    print(f"\nFor the {street_type} street, which node would you like to use?")
    print(f"1. Node {node1}")
    print(f"2. Node {node2}")
    while True:
        try:
            selection = int(input(f"Enter the number of your choice (1-2): "))
            if selection == 1:
                return node1
            elif selection == 2:
                return node2
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def parse_prolog_list(prolog_list_str):
    """
    Parses a Prolog list string into a Python list.
    Example: '[1,2,3]' -> [1, 2, 3]
    """
    # Remove the square brackets
    list_str = prolog_list_str.strip('[]')

    # Split the string by commas
    elements = list_str.split(',')

    # Convert elements to integers
    return [int(e.strip()) for e in elements if e.strip().isdigit()]

if __name__ == "__main__":
    main()
