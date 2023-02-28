import numpy as np
import sys
import os
import geopy
import geopy.distance 
from geographiclib.geodesic import Geodesic

class Graph(object):
    def __init__(self, nodes, init_graph, construct=False):
        self.nodes = nodes
        self.graph = self.cosntruct_graph(nodes, init_graph) if construct == True else init_graph

    def cosntruct_graph(self, nodes, init_graph):
        graph = {}
        for node in nodes:
            graph[node] = {}

        graph.update(init_graph)

        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if graph[adjacent_node].get(node, False) == False:
                    graph[adjacent_node][node] = value
                    
        return graph

    def get_nodes(self):
        return self.nodes

    def get_outgoing_edges(self, node):
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections

    def value(self, node1, node2):
        return self.graph[node1][node2]

def dijkstra_algorithm(graph, start_node):
    univisted_nodes = list(graph.get_nodes())

    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in univisted_nodes:
        shortest_path[node] = max_value
    
    shortest_path[start_node] = 0

    while univisted_nodes:
        current_min_node = None
        for node in univisted_nodes:
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        neighbours = graph.get_outgoing_edges(current_min_node)
        for neighbour in neighbours:
            tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbour)
            if tentative_value < shortest_path[neighbour]:
                shortest_path[neighbour] = tentative_value
                previous_nodes[neighbour] = current_min_node

        univisted_nodes.remove(current_min_node)

    return previous_nodes, shortest_path


def get_shortest_path(init_graph, nodes, start_node, target_node):
    path = []
    node = target_node
    graph = Graph(nodes, init_graph, construct=True)
    previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node= start_node)

    while node != start_node:
        path.append(node)
        node = previous_nodes[node]

    path.append(start_node)
    path = list(reversed(path))
    # print(path)
    # print("We found the follwowing best path with a value of {}.".format(shortest_path[target_node]))
    # print(" -> ".join(path))

    return path

if __name__ == "__main__":
    # nodes = ["0", "1", "2", "3", "4"]

    # init_graph = {}
    # for node in nodes:
    #     init_graph[node] = {}

    # init_graph["0"]["1"] = 1
    # init_graph["0"]["4"] = 3
    # init_graph["1"]["2"] = 2
    # init_graph["1"]["3"] = 3
    # init_graph["2"]["3"] = 1
    # init_graph["2"]["4"] = 5
    # init_graph["3"]["4"] = 1

    # graph = Graph(nodes, init_graph)

    # previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node= "3")

    # print_result(previous_nodes, shortest_path, start_node= "3", target_node= "4")

    # Empty array for route name
    route_name = []
    # Empty array for QgsPoints of coordinates of Bases
    points_route = [] 
    # Empty array for Names of Bases
    names_route = [] 

    # Read the text file
    txt=open("D:/AD TEWA/ScenarioGenratorQGIS/Coordinates files/DOMESTIC ATS ROUTES INDIA.txt",'r')

    # Reading all lines in text file
    coords_bases = [line.split(',') for line in txt.readlines()]

    # Extracting names of routes from text file
    route_id = [id for id in coords_bases if len(id) == 1]

    coords_bases = [elem for elem in coords_bases if elem != ['0.000000', '9999.000000\n']]
    data = dict()
    for i in route_id:
        if i != route_id[-1]:
            first_index = coords_bases.index(i)
            next_index = coords_bases.index(route_id[route_id.index(i) + 1])
            data[i[0].strip('\n')] = coords_bases[first_index+1 : next_index]

    for keys, value in data.items():
        for x in range(len(value)):
            value[x][-1] = value[x][-1].strip('\n')
            value[x][-1] = value[x][-1].lstrip()

    ATS_points = {}
    for key, values in data.items():
        for x in range(len(values)):
            ATS_points[values[x][3]] = [values[x][0], values[x][1]]

    print(ATS_points)
    # print(data)
    # nodes = []
    # for key, value in data.items():
    #     for i in range(len(value)):
    #         nodes.append(value[i][3])
    # nodes = list(set(nodes))

    # init_graph = {}
    # for node in nodes:
    #     init_graph[node] = {}
        
    # for key, value in data.items():
    #     for i in range(len(value)-1):
    #         init_graph[value[i][3]][value[i+1][3]] = geopy.distance.geodesic((value[i][0], value[i][1]), (value[i+1][0], value[i+1][1])).km
    
    
    # # print(list(init_graph.keys()))
    
    # # print(init_graph)
    # # previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node= " AHMEDABAD")
    # path = get_shortest_path(init_graph=init_graph, nodes= list(init_graph.keys()), start_node= "AHMEDABAD", target_node= "LEH")
    # print(path)
