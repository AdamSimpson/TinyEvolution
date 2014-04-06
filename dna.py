import numpy as np
import math
from PIL import Image,ImageDraw,ImageChops,ImageStat
from polygon import Polygon
import cPickle
import copy

class DNA(object):
    def __init__(self, polygons, master_image):
        self.polygons = polygons
        self.image = None
        self.master_image = master_image
        self.max_x = master_image.size[0]
        self.max_y = master_image.size[1]
        self._fitness = None
        self.max_polygon_count = 100;
        self.min_polygon_count = 0;
        self.mutate_polygon_order_rate = 0.0015;
        self.mutate_polygon_point_add_rate = 0.0007;
        self.mutate_polygon_point_remove_rate = 0.0007;
        self.mutate_add_polygon_rate = 0.0015;
        self.mutate_remove_polygon_rate = 0.0007;
        self.mutate_polygon_color_rate = 0.0007;
        self.mutate_polygon_point_rate = 0.0015;

    @property
    def polygon_count(self):
        return len(self.polygons)

    # fitness property is calculated if == None
    @property
    def fitness(self):
        if self._fitness == None:
            self.calculate_fitness()
        return self._fitness

    # Convenience function to determine if mutation will occur given the rate of mutation
    def will_mutate(self, rate):
        will_mutate = np.random.rand() < rate
        return will_mutate

    # Handle all DNA mutations
    def mutate(self):
        # Reset fitness and image to None
        self._fitness = None
        self.image = None

        # check if polygon count should mutate
        if self.will_mutate(self.mutate_add_polygon_rate) and self.polygon_count < self.max_polygon_count:
            self.add_polygon()

        if self.will_mutate(self.mutate_remove_polygon_rate) and self.polygon_count > self.min_polygon_count:
            self.remove_polygon()

        if self.will_mutate(self.mutate_polygon_order_rate):
            self.mutate_polygon_order()

        # check if each polygon should mutate
        for polygon in self.polygons:
            self.mutate_polygon(polygon)
            # check if each point should mutate
            for point in polygon.points:
                if self.will_mutate(self.mutate_polygon_point_rate):
                    self.mutate_polygon_point(polygon, point, 3)
            for point in polygon.points:
                if self.will_mutate(self.mutate_polygon_point_rate):
                    self.mutate_polygon_point(polygon, point, 20)
            for point in polygon.points:
                if self.will_mutate(self.mutate_polygon_point_rate):
                    self.mutate_polygon_point(polygon, point, 200)

    # Add random polygon to DNA
    def add_polygon(self):
        center_x = np.random.random_integers(low=0,high=self.max_x)
        center_y = np.random.random_integers(low=0,high=self.max_y)
        x_points = np.random.random_integers(low=center_x-3,high=center_x+3,size=3).tolist()
        y_points = np.random.random_integers(low=center_y-3,high=center_y+3,size=3).tolist()

        points = zip(x_points, y_points)
        color_rgb = np.random.random_integers(low=0, high=255, size=3).tolist()
        color_a = [np.random.random_integers(low=30, high=60)]
        color = tuple(color_rgb + color_a)
        new_polygon = Polygon(points, color)
        random_index = np.random.random_integers(low=0, high=self.polygon_count)
        self.polygons.insert(random_index, new_polygon)

    # Remove specified polygon from DNA
    def remove_polygon(self):
        random_index = np.random.randint(low=0, high=self.polygon_count)
        del self.polygons[random_index]

    # Mutate polygon order
    def mutate_polygon_order(self):
        # Get random polygon
        random_index = np.random.randint(low=0, high=self.polygon_count)
        random_insert_index = np.random.randint(low=0, high=self.polygon_count)
        polygon = self.polygons.pop(random_index)
        # Insert it back into new spot
        self.polygons.insert(random_insert_index, polygon)

    # Mutate specified polygon
    def mutate_polygon(self, polygon):
        # Mutate polygon point count
        if self.will_mutate(self.mutate_polygon_point_add_rate):
            self.add_polygon_point(polygon)

        if self.will_mutate(self.mutate_polygon_point_remove_rate):
            self.remove_polygon_point(polygon)

        # Mutate polygon color
        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_red(polygon)

        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_green(polygon)            

        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_blue(polygon)

        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_alpha(polygon)

    # Add point to polygon
    def add_polygon_point(self, polygon):
        # Grab random polygon and random point
        random_point_index = np.random.randint(low=1, high=polygon.point_count)
        point_x, point_y = polygon.points[random_point_index]
        prev_x, prev_y = polygon.points[random_point_index-1]

        new_point_x = (prev_x + point_x)/2.0
        new_point_y = (prev_y + point_y)/2.0

        new_point = (new_point_x, new_point_y)

        polygon.add_point(random_point_index, new_point)

    # Remove point from polygon
    def remove_polygon_point(self, polygon):
        random_index = np.random.randint(low=0, high=polygon.point_count)
        polygon.remove_point(random_index)

    # Mutate a polygon point
    def mutate_polygon_point(self, polygon, point, amount):
        index = polygon.points.index(point)
        point_x, point_y = polygon.points[index]

        # Number of pixels to edge of image
        pixels_to_left   = point_x
        pixels_to_right  = self.max_x - point_x
        pixels_to_top    = self.max_y - point_y
        pixels_to_bottom = point_y

        dx = np.random.random_integers(low=-amount, high=amount)
        dy = np.random.random_integers(low=-amount, high=amount)

        # Make sure to stay in bounds
        dx = np.clip(dx, -pixels_to_left, pixels_to_right)
        dy = np.clip(dy, -pixels_to_bottom, pixels_to_top)

        # Update point
        new_points = polygon.points
        new_points[index] = (point_x + dx, point_y + dy)
        polygon.points = new_points

    def mutate_polygon_red(self, polygon):
        new_color = (
            np.random.random_integers(low=0,high=255),
            polygon.color[1],
            polygon.color[2],
            polygon.color[3]
        )

        polygon.color = new_color

    def mutate_polygon_green(self, polygon):
        new_color = (
            polygon.color[0],
            np.random.random_integers(low=0,high=255),
            polygon.color[2],
            polygon.color[3]
        )

        polygon.color = new_color


    def mutate_polygon_blue(self, polygon):
        new_color = (
            polygon.color[0],
            polygon.color[1],
            np.random.random_integers(low=0,high=255),
            polygon.color[3]
        )

        polygon.color = new_color

    def mutate_polygon_alpha(self, polygon):
        new_color = (
            polygon.color[0],
            polygon.color[1],
            polygon.color[2],
            np.random.random_integers(low=30,high=80)
        )

        polygon.color = new_color

    # Render the DNA to image
    def render(self):
        self.image = Image.new("RGB", (self.max_x, self.max_y))
        draw = ImageDraw.Draw(self.image,"RGBA")

        for polygon in self.polygons:
            draw.polygon(polygon.points, polygon.color)

    # Save the image and Polygon class to disk
    def save(self, suffix=None):
        # Render image if not already
        if self.image == None:
            self.render()

        # Setup file name
        if suffix == None:
            suffix = "0"
        file_name = "evolve-"+suffix+".png"

        self.image.save(file_name)

        # Save DNA polygons to disk
        with open("evolve_Polygon.dump", "wb") as output:
            cPickle.dump(self.polygons, output, cPickle.HIGHEST_PROTOCOL)

    # Compute fitness of DNA
    def calculate_fitness(self):
        self.render()
        diff = ImageChops.difference(self.image, self.master_image)              
        self._fitness = sum(ImageStat.Stat(diff).sum)

    # Compute fitness of DNA
    def calculate_fitness_slow(self):
        self.render()
        fitness = 0

        for j in range(self.max_y):
            for i in range(self.max_x):
                r_m, g_m, b_m = self.image.getpixel((i, j))
                r, g, b = self.master_image.getpixel((i, j))
                r2 = (r_m - r) * (r_m - r)
                g2 = (g_m - g) * (g_m - g)
                b2 = (b_m - b) * (b_m - b)
                fitness += math.sqrt(r2 + g2 + b2)

        self._fitness = fitness

    # Create copy of self and replicate
    def breed(self):
        # Clone polygons
        child = self.copy()

        # Replicate and possibly mutate
        child.mutate()
 
        return child

    # Create Copy of DNA
    def copy(self):
        polygons_copy = copy.deepcopy(self.polygons)
        dna_copy = DNA(polygons_copy, self.master_image)

        dna_copy._fitness = self._fitness

        return dna_copy
