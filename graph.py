from __future__ import annotations
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import math

def _get_lines(filename):
    with open(filename) as fh:
        lines = fh.readlines()
    return lines


class BadGraphInput(Exception):
    def __init__(self, message: str):
        super().__init__(f'Graph could not be create due to bad input: {message}')


class Graph:
    def __init__(self):
        self.matrix = None

    def from_neighbourhood_matrix_file(self, filename: str):
        input = _get_lines(filename)
        self.from_neighbourhood_matrix([[int(val) for val in line.split(' ')] for line in input])
        
    def from_neighbourhood_matrix(self, matrix: list):
        self.matrix = matrix
        self.validate()

    def from_adjacency_list_file(self, filename: str):
        input = _get_lines(filename)
        adj_list = {}
        for line in input:
            index, rest = line.split(':')
            adj_list[int(index)] = [int(v) for v in rest.split(' ')]

        self.from_adjacency_list(adj_list)

    def from_adjacency_list(self, adj_list: dict):
        node_count = len(adj_list)
        matrix = [[0]*node_count for _ in range(node_count)]
        for node, neighbours in adj_list.items():
            for neigh in neighbours:
                matrix[node-1][neigh-1] += 1

        self.matrix = matrix
        self.validate()

    def from_incidence_matrix_file(self, filename: str):
        input = _get_lines(filename)
        inc_matrix = [[int(val) for val in line.split(' ')] for line in input]
        self.from_incidence_matrix(inc_matrix)

    def from_incidence_matrix(self, inc_matrix: list):
        node_count = len(inc_matrix)
        matrix = [[0]*node_count for _ in range(node_count)]
        inc_matrix = np.transpose(np.array(inc_matrix))

        for edge in inc_matrix:
            neigbours = []
            for i, node in enumerate(edge):
                if node == 1:
                    neigbours.append(i)

            if len(neigbours) != 2:
                raise BadGraphInput(f'invalid edge, {len(neigbours)} nodes')

            matrix[neigbours[0]][neigbours[1]] += 1
            matrix[neigbours[1]][neigbours[0]] += 1

        self.matrix = matrix
        self.validate()

    def validate(self):
        if any([self.matrix[i][i] for i in range(len(self.matrix))]):
            self.matrix = None
            raise BadGraphInput("can't have loops")
        if any([v>1 for row in self.matrix for v in row], ):
            self.matrix = None
            raise BadGraphInput("can't have multiple edges")
        if not np.array_equal(np.transpose(np.array(self.matrix)), np.array(self.matrix)):
            self.matrix = None
            raise BadGraphInput("incorrect graph")    

    def as_neighbourhood_matrix(self):
        return self.matrix

    def as_adjacency_list(self):
        return {i+1: [j+1 for j,v in enumerate(row) if v==1] for i,row in enumerate(self.matrix)}

    def as_incidence_matrix(self):
        edge_count = sum(sum(row) for row in self.matrix)//2
        node_count = len(self.matrix)
        
        matrix = [[0]*edge_count for _ in range(node_count)]

        current_edge = 0
        for i in range(len(self.matrix)-1):
            for j in range(i+1, len(self.matrix[0])):
                if self.matrix[i][j] == 1:
                    matrix[i][current_edge] = 1
                    matrix[j][current_edge] = 1
                    current_edge += 1

        return matrix


class GraphDrawer:
    def __init__(self):
        self.graph = None
        self.r = 1.
        self.xy = [0.,0.]
        self.title = ''

    def parse(self, graph: Graph) -> GraphDrawer:
        adj_list = graph.as_adjacency_list()
        g=nx.Graph()
        for node, neighs in adj_list.items():
            if not neighs:
                g.add_node(node)
                continue
            for neigh in neighs:
                g.add_edge(node, neigh)
        self.graph = g
        return self

    def with_title(self, title: str) -> GraphDrawer:
        self.title = title
        return self

    def to_screen(self):
        self.__draw()
        plt.show()
        GraphDrawer.__plt_close()

    def to_file(self, filename: str):
        self.__draw()
        plt.savefig(filename)
        GraphDrawer.__plt_close()

    def __plt_close():
        plt.clf()
        plt.cla()
        plt.close()

    def __draw(self):
        if self.graph is None:
            raise TypeError('Graph to draw is None')
        circ=plt.Circle((self.xy[0], self.xy[1]), self.r, color='r', fill=False, linestyle=':')
        _, ax = plt.subplots()
        ax.add_patch(circ)
        nx.draw(self.graph,
            pos=self.__make_pos(),
            labels=None,
            node_color='#D3D3D3'
        )
        plt.axis('scaled')
        plt.title(self.title)

    def __make_pos(self) -> dict:
        nodes = sorted(self.graph.nodes())
        alpha = 2*math.pi/len(nodes)
        result = {}

        for i,node in enumerate(nodes):
            x = self.xy[0] + self.r * math.sin(i*alpha)
            y = self.xy[1] + self.r * math.cos(i*alpha)
            result[node] = np.array([x,y])

        return result
