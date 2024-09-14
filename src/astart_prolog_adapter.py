"""
Prolog Adapter for A* Algorithm implementation on SWI-Prolog
I know that isn't a good idea to have a constructor to a code that only uses one file, but I want to practice
Input: Prolog file and SWI-Prolog executable path
Output: Path and cost of the shortest path between two nodes
"""

import subprocess
import sys

class AstarPrologAdapter:
    def __init__(self, prolog_file='./src/astar_implementation.pl', prolog_path='swipl'):
        """
        Initialize the adapter with the Prolog file and the SWI-Prolog executable path.
        """
        self.prolog_file = prolog_file
        self.prolog_path = prolog_path
    """
    Find the shortest path between two nodes using the A* algorithm implemented in Prolog
    Input: Start node, end node
    Output: Path and cost of the shortest path
    """
    def find_path(self, start_node, end_node):
        # Construct the Prolog goal
        prolog_goal = self.__prolog_goal(start_node, end_node)
        # Construct the command to run SWI-Prolog
        command = self.__swipl_command(prolog_goal)

        try:
            # Run the Prolog command
            result = self.__run_prolog_command(command)

            # Check for errors
            if result.returncode != 0:
                print("An error occurred while running the Prolog query:")
                print(result.stderr)
                sys.exit(1)

            # Capture the output
            output = result.stdout.strip()

            # Parse the output to extract the path and cost
            path_str, cost_str = self.__extract_prolog_output(output)
            
            if path_str is not None and cost_str is not None:
                # Convert the path string to a Python list
                path = self.__parse_prolog_list(path_str)
                cost = float(cost_str)
                return path, cost
            else:
                print("No path found between the specified nodes.")
                return None, None
                
        except FileNotFoundError:
            print(f"SWI-Prolog executable '{self.prolog_path}' not found. Please ensure SWI-Prolog is installed and added to your PATH.")
            sys.exit(1)

    def __extract_prolog_output(self, output):
        """
        Extract the path and cost from the Prolog output
        """
        lines = output.split('\n')
        if len(lines) >= 2:
            path_str = lines[0]
            cost_str = lines[1]
            return path_str, cost_str
        else:
            return None, None
        
    def __prolog_goal(self, start_node, end_node):
        """
        Construct the Prolog goal
        e.g. astar(1, 5, Path, Cost), write(Path), nl, write(Cost), halt.
        """
        prolog_goal = (
            f"astar({start_node}, {end_node}, Path, Cost), "
            f"write(Path), nl, write(Cost), halt."
        )
        return prolog_goal
    
    def __swipl_command(self, prolog_goal):
        """
        Construct the command to run SWI-Prolog
        """
        command = [
            self.prolog_path,
            '-q',  # Suppress the welcome message
            '-s', self.prolog_file,
            '-g', prolog_goal
        ]
        return command
    
    def __run_prolog_command(self, command):
        """
        Run the Prolog command
        """
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result
    
    def __parse_prolog_list(self, prolog_list_str):
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
