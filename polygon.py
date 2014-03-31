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

    @property
    def point_count(self):
        return len(self.points)

    @property
    def min_x(self):
        return min(self.points)[0]

    @property
    def max_x(self):
        return max(self.points)[0]

    @property
    def min_y(self):
        return min(self.points)[1]

    @property
    def max_y(self):
        return max(self.points)[1]

    def move(self, delta_x, delta_y):
        for i, point in enumerate(self.points):
            new_point = (point[0] + delta_x, point[1] + delta_y)
            self.points[i] = new_point

    def add_point(self, point):
        if self.point_count < self.max_points:
            self.points.append(point)

    def remove_point(self, point_index):
        if self.point_count > self.min_points:
            del self.points[point_index]
