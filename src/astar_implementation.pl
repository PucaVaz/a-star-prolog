% Load the city data
:- [city_data].

% Define neighbor relationships based on the street data
neighbor(Node, Neighbor, Cost) :-
    street(Node, Neighbor, Cost, _).

neighbor(Node, Neighbor, Cost) :-
    street(Neighbor, Node, Cost, _).

% Heuristic function (currently set to zero)
heuristic(_, _, 0).

% Main A* algorithm predicate
astar(Start, Goal, Path, Cost) :-
    heuristic(Start, Goal, H),
    F is H,
    astar_search([node(Start, [Start], 0, F)], [], Goal, RevPath, Cost),
    reverse(RevPath, Path).

% A* search implementation
astar_search(OpenList, ClosedList, Goal, Path, Cost) :-
    OpenList \= [],
    get_best_node(OpenList, BestNode, RestOpenList),
    BestNode = node(CurrentNode, CurrentPath, G, _),
    (CurrentNode = Goal ->
        Path = CurrentPath,
        Cost = G
    ;
        % Expand the current node
        findall(
            node(Neighbor, [Neighbor|CurrentPath], GNew, FNew),
            (
                neighbor(CurrentNode, Neighbor, StepCost),
                \+ member(Neighbor, ClosedList),
                GNew is G + StepCost,
                heuristic(Neighbor, Goal, HNew),
                FNew is GNew + HNew
            ),
            Successors
        ),
        % Update the open list with successors
        add_to_open_list(Successors, RestOpenList, [CurrentNode|ClosedList], NewOpenList),
        astar_search(NewOpenList, [CurrentNode|ClosedList], Goal, Path, Cost)
    ).

% Select the best node (with the lowest F value) from the open list
get_best_node([Node], Node, []).
get_best_node(OpenList, BestNode, RestOpenList) :-
    select(BestNode, OpenList, RestOpenList),
    BestNode = node(_, _, _, F),
    \+ (
        member(node(_, _, _, F1), RestOpenList),
        F1 < F
    ).

% Add successors to the open list, updating costs if necessary
add_to_open_list([], OpenList, _, OpenList).
add_to_open_list([node(Node, Path, G, F)|Successors], OpenList, ClosedList, NewOpenList) :-
    (member(Node, ClosedList) ->
        % Skip if the node is already in the closed list
        add_to_open_list(Successors, OpenList, ClosedList, NewOpenList)
    ;
        (select(node(Node, _, GExisting, _), OpenList, TempOpenList) ->
            % Update if a better path is found
            (G < GExisting ->
                add_to_open_list(Successors, [node(Node, Path, G, F)|TempOpenList], ClosedList, NewOpenList)
            ;
                add_to_open_list(Successors, OpenList, ClosedList, NewOpenList)
            )
        ;
            % Add new node to the open list
            add_to_open_list(Successors, [node(Node, Path, G, F)|OpenList], ClosedList, NewOpenList)
        )
    ).

% Find nodes associated with a street name
street_nodes(StreetName, Node1, Node2) :-
    street(Node1, Node2, _, StreetName) ;
    street(Node2, Node1, _, StreetName).

% A* search between streets
astar_between_streets(StreetNameStart, StreetNameEnd, Path, Cost) :-
    setof(
        [P, C],
        (
            street_nodes(StreetNameStart, StartNode1, StartNode2),
            street_nodes(StreetNameEnd, EndNode1, EndNode2),
            (
                astar(StartNode1, EndNode1, P, C) ;
                astar(StartNode1, EndNode2, P, C) ;
                astar(StartNode2, EndNode1, P, C) ;
                astar(StartNode2, EndNode2, P, C)
            )
        ),
        PathsAndCosts
    ),
    % Select the path with the minimum cost
    sort(2, @=<, PathsAndCosts, [[Path, Cost]|_]).
