class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __str__(self):
        return 'id: ' + str(self.id) + ', x: ' + str(self.x) + ', y: ' + str(self.y)

    def inRegionOfInterest(self, x, y):

        region = 0.1
        if abs(self.x - x) <= region and abs(self.y - y) <= region:
            return True
        else:
            return False