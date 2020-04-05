from xml.etree import ElementTree as et
import numpy as np

class Node:
    def __init__(self, id, x, y, target):
        self.id = id
        self.x = x
        self.y = y
        self.target = target

    def __str__(self):
        return str(self.id) + ' -> ' + str(self.target) + '\n(x, y) = (' + str(self.x) + ', ' + str(self.y) + ')'\
               
    def toList(self):
        return [self.id, self.x, self.y]


class FindPath:
    def __init__(self, mandatoryNodes, terminalNodes, intersectionNodes):
        # intersection nodes: 9, 10, 11, 12 ; 19, 20, 21 ; 28, 29, 30
        # terminal nodes:111, 114

        # -here are the mandatory nodes through which the car must pass
        # -as a convention: first number is the initial node and the last number will be the ending point !!!!!
        self.mandatoryNodes = mandatoryNodes
        self.mandatoryNodes = [terminalNodes[0]] + self.mandatoryNodes + [terminalNodes[1]]
        self.f = open('PathFinding\\The Path.txt', 'w')
        self.f.write('Mandatory nodes: ' + str(self.mandatoryNodes) + '\n')

        # we create an adjacency list based on the xml data provided

        self.intersectionNodes = intersectionNodes  # nodes that are in an intersection
        # important because are the only nodes that have multiple targets

        self.terminalNodes = terminalNodes  # nodes that do not have a target

        # next we extract the relevant data from the xml file
        tree = et.parse('PathFinding\\EliminationMap.graphml.xml')
        root = tree.getroot()
        graph = root.find('graph')
        nodes = graph.findall('node')
        edges = graph.findall('edge')

        # save the data in an adjacency list
        self.adjlist = []
        for n in nodes:
            ID = int(n.attrib['id'])
            data = n.findall('data')
            x = float(data[0].text)
            y = float(data[1].text)
            target = []
            for e in edges:
                if int(e.attrib['source']) == ID:
                    target.append(int(e.attrib['target']))

            node = Node(ID, x, y, target)
            self.adjlist.append(node)

        self.visited = np.zeros((1, self.adjlist.__sizeof__()),
                                dtype=np.int8)  # store which nodes were visited and how many times
        self.cost = 0  # the cost of the road (between all nodes there will be a cost of one)
        self.thePath = []  # store the path taken
        self.minCost = int(1e10)  # here we will store the minimum cost of a complete path
        self.minCostPath = []  # here we will save the path associated with the minimum cost


        self.initNode = self.mandatoryNodes[0]
        self.mandatoryNodes.sort()  # we sort the list so we can compare it with the mandatory visited list
        self.mandatoryVisited = []  # here we will store through which mandatory nodes we already passed

    def findPath(self, node):
        """
        -use backtracking to find the shortest path that passes through all the mandatory points
        -we will take the cost as 1 because the nodes are approximately 30 cm apart from one another => no need for diff val
        """

        # check if the node was visited more than 2 times and if so return (does not apply to intersection nodes)
        if self.visited[0][node.id - 1] == 2 and node not in self.intersectionNodes:
            return

        self.visited[0][node.id - 1] += 1
        self.cost += 1
        self.thePath.append(node)

        youCanDeleteIt = 0
        # if we reach a mandatory node check if we`ve been thorough all of them.. if so => we have a result
        if node.id in self.mandatoryNodes:
            if node.id not in self.mandatoryVisited:
                youCanDeleteIt = 1
                self.mandatoryVisited.append(node.id)
            self.mandatoryVisited.sort()
            if self.mandatoryVisited == self.mandatoryNodes:
                # if the cost of the calculated path is less than the minimum cost => we have a new min path
                if self.cost < self.minCost:
                    self.minCost = self.cost
                    self.minCostPath = self.thePath.copy()

        # inspect the next nodes
        for nextN in node.target:
            self.findPath(self.adjlist[nextN - 1])

        if youCanDeleteIt:
            self.mandatoryVisited.remove(node.id)
        self.thePath.pop()
        self.cost -= 1
        self.visited[0][node.id - 1] -= 1

    def run(self):
        self.findPath(self.adjlist[self.initNode - 1])
        pathList = []
        for element in self.minCostPath:
            pathList.append(element.toList())
        # print(pathList)

        for elem in self.minCostPath:
            self.f.write(elem.__str__() + '\n')
        self.f.close()

        graph = et.Element('graph')
        for elem in pathList:
            node = et.SubElement(graph, 'node')
            ID = et.SubElement(node, 'id')
            x = et.SubElement(node, 'x')
            y = et.SubElement(node, 'y')
            ID.text = str(elem[0])
            x.text = str(elem[1])
            y.text = str(elem[2])
        tree = et.ElementTree(graph)
        tree.write('PathFinding\\path.xml')
        tree.write('src\\brain\\path.xml')
        return pathList

if __name__ == "__main__":
    intersectionNodes = [9, 10, 11, 12, 19, 20, 21, 28, 29, 30]
    terminalNodes = [112, 114]
    mandatoryNodes = [106, 38]
    pathfinder = FindPath(mandatoryNodes, terminalNodes, intersectionNodes)
    print(pathfinder.run())