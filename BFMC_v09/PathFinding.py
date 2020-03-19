from xml.etree import ElementTree as et
import numpy as np


# -here are the mandatory nodes through which the car must pass
# -as a convention: first number is the initial node and the last number will be the ending point !!!!!
mandatoryNodes = [113, 111]
f = open('PathFinding\\The Path.txt', 'w')
f.write('Mandatory nodes: ' + str(mandatoryNodes) + '\n')


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

# intersection nodes: 9, 10, 11, 12 ; 19, 20, 21 ; 28, 29, 30
# terminal nodes:111, 114


# we create an adjacency list based on the xml data provided

intersectionNodes = [9, 10, 11, 12, 19, 20, 21, 28, 29, 30]  # nodes that are in an intersection
# important because are the only nodes that have multiple targets

terminalNodes = [111, 114]  # nodes that do not have a target

# next we extract the relevant data from the xml file
tree = et.parse('PathFinding\\EliminationMap.graphml.xml')
root = tree.getroot()
graph = root.find('graph')
nodes = graph.findall('node')
edges = graph.findall('edge')

# save the data in an adjacency list
adjlist = []
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
    adjlist.append(node)


initNode = mandatoryNodes[0]
mandatoryNodes.sort()  # we sort the list so we can compare it with the mandatory visited list
mandatoryVisited = []  # here we will store through which mandatory nodes we already passed

visited = np.zeros((1, adjlist.__sizeof__()), dtype=np.int8)  # store which nodes were visited and how many times
cost = 0    # the cost of the road (between all nodes there will be a cost of one)
thePath = []    # store the path taken
minCost = int(1e10)    # here we will store the minimum cost of a complete path
minCostPath = []    # here we will save the path associated with the minimum cost


def findPath(node):
    """
    -use backtracking to find the shortest path that passes through all the mandatory points
    -we will take the cost as 1 because the nodes are approximately 30 cm apart from one another => no need for diff val
    """
    global cost, mandatoryVisited, minCost, minCostPath

    # check if the node was visited more than 2 times and if so return (does not apply to intersection nodes)
    if visited[0][node.id - 1] == 2 and node not in intersectionNodes:
        return

    visited[0][node.id - 1] += 1
    cost += 1
    thePath.append(node)

    youCanDeleteIt = 0
    # if we reach a mandatory node check if we`ve been thorough all of them.. if so => we have a result
    if node.id in mandatoryNodes:
        if node.id not in mandatoryVisited:
            youCanDeleteIt = 1
            mandatoryVisited.append(node.id)
        mandatoryVisited.sort()
        if mandatoryVisited == mandatoryNodes:
            # if the cost of the calculated path is less than the minimum cost => we have a new min path
            if cost < minCost:
                minCost = cost
                minCostPath = thePath.copy()

    # inspect the next nodes
    for nextN in node.target:
        findPath(adjlist[nextN - 1])

    if youCanDeleteIt:
        mandatoryVisited.remove(node.id)
    thePath.pop()
    cost -= 1
    visited[0][node.id - 1] -= 1


findPath(adjlist[initNode - 1])

pathList = []
for element in minCostPath:
    pathList.append(element.toList())
print(pathList)

for elem in minCostPath:
    f.write(elem.__str__() + '\n')
f.close()

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
