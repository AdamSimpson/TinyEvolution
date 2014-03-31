class Polygon(object):
    def __init__(self, points, color):
        self._points = points
        self.color = color
        self.max_points=10
        self.min_points=3

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        if(points < self.max_points):
            self._points = points

    def point_count(self):
        len(self.points)

    def min_x(self):
        min(self.points)[0]

    def max_x(self):
        max(self.points)[0]

    def min_y(self):
        min(self.points)[1]

    def max_y(self):
        max(self.points)[1]

    def move(self, dx, dy):
        for point in self.points:
            point[0] += dx
            point[1] += dy

    def add_point(self, point):
        self.points.append(point)

    def remove_point(self, point_index):
        del self.points[point_index]
