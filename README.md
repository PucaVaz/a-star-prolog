# A* implementation using prolog and python

## Astar program 
This document details the implementation of the Prolog A* algorithm, designed for pathfinding between streets. The algorithm utilizes a graph-based structure generated by the accompanying script get_map.py. This script constructs a graph, including the respective nodes and edges, representing the street layout for the pathfinding process.\
The Prolog predicate astar/4 serves as the main entry point for executing the A* pathfinding algorithm. It is designed to find the shortest path from a given starting node (Start) to a destination node (Goal), returning the computed path (Path) and the total cost (Cost) of traversal.

Predicate Definition:
``` bash
astar(Start, Goal, Path, Cost)
```
Parameters:

	•	Start: The starting node from which the search begins.
	•	Goal: The target node where the search should end.
	•	Path: The list of nodes representing the shortest path from Start to Goal.
	•	Cost: The total cost associated with traversing the computed path.


## Get Map 
This project utilizes the osmnx library to extract a city’s street network data. The library generates a structured graph, mapping node IDs to sequential integers and defining the corresponding edges. This processed information is then written to a file named city_data.pl. The output in this file is structured in the following format:

#### Locations Section:
```prolog
% Locations in the city (Nodes)
location(1, 'Intersection 1').
location(2, 'Intersection 2').
...
```
#### Streets Section:
```prolog
% Streets between locations (Edges with Distances as Weights)
% street(Node1, Node2, Distance).
street(1, 2, 0.50, 'Main St').
street(2, 3, 0.75, 'Second Ave').
...
```

## Find the path
This Python script facilitates pathfinding using a Prolog A* algorithm for determining the shortest route between two streets within a city’s network. The underlying graph is represented by a Prolog file (city_data.pl), which includes node and edge mappings between street intersections. Below, we detail the primary functions of this script:

The script prompts the user to input two street names—one as the starting street and the other as the destination. It utilizes the following steps to achieve the desired pathfinding:

	•	Street Name Matching: The script uses a fuzzy matching algorithm (difflib) to match user input with street names available in the dataset.
	•	Node Pair Selection: Once the street names are matched, the script presents available node pairs (representing intersections) for each street. The user is asked to select the desired node for both the starting and destination streets.
	•	Prolog Integration: After selecting the appropriate nodes, the program constructs a Prolog goal using the A* algorithm. This goal is then executed by invoking SWI-Prolog through a subprocess.
	•	Result Parsing: The Prolog output is parsed to extract and display the path (as a sequence of node IDs) and the total cost of the route.


Current this code is somewhat disorganized, with several functions performing multiple tasks. This makes it difficult to maintain and extend. On a soon future, i want implement some desing pattern 
