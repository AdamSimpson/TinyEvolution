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
        self.max_polygon_count = 6000;
        self.min_polygon_count = 50;
        self.mutate_polygon_count_rate = 0.0015;
        self.mutate_polygon_order_rate = 0.003;
        self.mutate_polygon_rate = 0.9;
        self.mutate_polygon_point_count_rate = 0.003;
        self.mutate_polygon_location_rate = 0.004;
        self.mutate_polygon_point_rate = 0.006;
        self.mutate_polygon_color_rate = 0.003;

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
        if self.will_mutate(self.mutate_polygon_count_rate):
            self.mutate_polygon_count()

        # check if each polygon should mutate
        for polygon in self.polygons:
            if self.will_mutate(self.mutate_polygon_rate):
                self.mutate_polygon(polygon)
            # check if each point should mutate
            for point in polygon.points:
                if self.will_mutate(self.mutate_polygon_point_rate):
                    self.mutate_polygon_point(polygon, point)

    # Mutate number of polygons in DNA
    def mutate_polygon_count(self):
        if np.random.rand() < 0.75 and self.polygon_count < self.max_polygon_count:
            self.add_polygon()
        elif self.polygon_count > self.min_polygon_count:
            random_index = np.random.randint(low=0, high=self.polygon_count)
            self.remove_polygon(random_index)

    # Add random polygon to DNA
    def add_polygon(self):
        center_x = np.random.random_integers(low=0,high=self.max_x)
        center_y = np.random.random_integers(low=0,high=self.max_y)
        x_points = np.random.random_integers(low=center_x-1,high=center_x+1,size=3).tolist()
        y_points = np.random.random_integers(low=center_y-1,high=center_y+1,size=3).tolist()

        points = zip(x_points, y_points)
        color_rgb = np.random.random_integers(low=0, high=255, size=3).tolist()
        color_a = [np.random.random_integers(low=30, high=60)]
        color = tuple(color_rgb + color_a)
        new_polygon = Polygon(points, color)
        self.polygons.append(new_polygon)

    # Remove specified polygon from DNA
    def remove_polygon(self, polygon_index):
        del self.polygons[polygon_index]

    # Mutate polygon order
    def mutate_polygon_order(self, polygon):
        # Get random polygon
#        random_remove_index = np.random.randint(low=0, high=self.polygon_count)
        random_insert_index = np.random.randint(low=0, high=self.polygon_count)
        index = self.polygons.index(polygon)
        self.polygons.pop(index)
        # Insert it back into new spot
        self.polygons.insert(random_insert_index, polygon)

    # Mutate specified polygon
    def mutate_polygon(self, polygon):
        # Mutate polygon point count
        if self.will_mutate(self.mutate_polygon_point_count_rate):
            self.mutate_polygon_point_count(polygon)

        # Mutate polygon location
        if self.will_mutate(self.mutate_polygon_location_rate):
            self.mutate_polygon_location(polygon)

        # Mutate stacking order of polygons
        if self.will_mutate(self.mutate_polygon_order_rate):
            self.mutate_polygon_order(polygon)

        # Mutate polygon color
        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_red(polygon)

        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_green(polygon)            

        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_blue(polygon)

        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_alpha(polygon)

    # Mutate number of points in specified polygon
    def mutate_polygon_point_count(self, polygon):
        if np.random.rand() < 0.5:
            # Grab random polygon and random point
            random_polygon_index = np.random.randint(low=0, high=self.polygon_count)
            polygon = self.polygons[random_polygon_index]
            random_point_index = np.random.randint(low=1, high=polygon.point_count)
            point_x, point_y = polygon.points[random_point_index]
            # Grab point to "left" of point
#            previous_point_x, previous_point_y = polygon.points[random_point_index-1]

            # Create and add point that is inbetween point and previous point
#            new_x = (previous_point_x + point_x) / 2
#            new_y = (previous_point_y + point_y) / 2
#            new_point = (new_x, new_y)

            new_point = (point_x, point_y)

            polygon.add_point(new_point)
        else:
            random_index = np.random.randint(low=0, high=polygon.point_count)
            polygon.remove_point(random_index)

    # Translate the polygon up/down and left/right
    def mutate_polygon_location(self, polygon):
        # Number of pixels to edge of image
        pixels_to_left   = polygon.min_x
        pixels_to_right  = self.max_x - polygon.max_x
        pixels_to_top    = self.max_y - polygon.max_y
        pixels_to_bottom = polygon.min_y

        dx = np.random.random_integers(low=-3, high=3)
        dy = np.random.random_integers(low=-3, high=3)

        # Make sure to stay in bounds
        np.clip(dx, -pixels_to_left, pixels_to_right)
        np.clip(dy, -pixels_to_bottom, pixels_to_top)

        # Move the polygon
        polygon.move(delta_x = dx, delta_y = dy)

    # Mutate a polygon point
    def mutate_polygon_point(self, polygon, point):
        index = polygon.points.index(point)
        point_x, point_y = polygon.points[index]

        # Number of pixels to edge of image
        pixels_to_left   = point_x
        pixels_to_right  = self.max_x - point_x
        pixels_to_top    = self.max_y - point_y
        pixels_to_bottom = point_y

#        dx = np.random.random_integers(low=-pixels_to_left, high=pixels_to_right)
#        dy = np.random.random_integers(low=-pixels_to_bottom, high=pixels_to_top)

        dx = np.random.random_integers(low=-3, high=3)
        dy = np.random.random_integers(low=-3, high=3)

        # Make sure to stay in bounds
        np.clip(dx, -pixels_to_left, pixels_to_right)
        np.clip(dy, -pixels_to_bottom, pixels_to_top)

        # Update point
        new_points = polygon.points
        new_points[index] = (point_x + dx, point_y + dy)
        polygon.points = new_points

    def mutate_polygon_red(self, polygon):
        dc = 255*np.random.normal(scale=0.1)

        new_color = (
            np.clip(polygon.color[0] + int(dc), 0, 255),
            polygon.color[1],
            polygon.color[2],
            polygon.color[3]
        )

        polygon.color = new_color

    def mutate_polygon_green(self, polygon):
        dc = 255*np.random.normal(scale=0.1)

        new_color = (
            polygon.color[0],
            np.clip(polygon.color[1] + int(dc), 0, 255), 
            polygon.color[2],
            polygon.color[3]
        )

        polygon.color = new_color


    def mutate_polygon_blue(self, polygon):
        dc = 255*np.random.normal(scale=0.1)

        new_color = (
            polygon.color[0],
            polygon.color[1],
            np.clip(polygon.color[2] + int(dc), 0, 255),
            polygon.color[3]
        )

        polygon.color = new_color

    def mutate_polygon_alpha(self, polygon):
        dc = 60*(np.random.normal(scale=0.1) )

        new_color = (
            polygon.color[0],
            polygon.color[1],
            polygon.color[2],
            np.clip(polygon.color[3] + int(dc), 30, 60)
        )

        polygon.color = new_color


    # Mutate the selected polygon color
    def mutate_polygon_color(self, polygon):
        dc = 255*np.random.normal(scale=0.1, size=4)

        new_color = (
            np.clip(polygon.color[0] + dc[0], 0, 255),
            np.clip(polygon.color[1] + dc[1], 0, 255),
            np.clip(polygon.color[2] + dc[2], 0, 255),      
            np.clip(polygon.color[3] + dc[3], 30, 90),
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
