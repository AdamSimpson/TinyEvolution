import numpy as np
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
        self.max_polygon_count = 1000;
        self.min_polygon_count = 50;
        self.mutate_polygon_count_rate = 0.0;
        self.mutate_polygon_order_rate = 0.0;
        self.mutate_polygon_rate = 0.05;
        self.mutate_polygon_point_count_rate = 0.0;
        self.mutate_polygon_location_rate = 0.1;
        self.mutate_polygon_point_rate = 0.05;
        self.mutate_polygon_color_rate = 0.1;

    @property
    def polygon_count(self):
        return len(self.polygons)

    # fitness property is calculated if == None
    @property
    def fitness(self):
        if self._fitness == None:
            self.calculate_fitness()
        return self._fitness

    # Convenience function to determine if mutatin will occur given the rate of mutation
    def will_mutate(self, rate):
        will_mutate = np.random.rand() < rate
        return will_mutate

    # Handle all DNA mutations
    def mutate(self):
        # Reset fitness and image to None
        self._fitness = None
        self.image = None

        # check if each polygon should mutate
        for polygon in self.polygons:
            if self.will_mutate(self.mutate_polygon_rate):
                self.mutate_polygon(polygon)

        # check if polygon count should mutate
        if self.will_mutate(self.mutate_polygon_count_rate):
            self.mutate_polygon_count()

        # check if polygon order should mutate
        if self.will_mutate(self.mutate_polygon_order_rate):
            self.mutate_polygon_order()

    # Mutate number of polygons in DNA
    def mutate_polygon_count(self):
        if np.random.rand() < 0.5 and self.polygon_count < self.max_polygon_count:
            self.add_polygon()
        elif self.polygon_count > self.min_polygon_count:
            random_index = np.random.randint(low=0, high=self.polygon_count)
            self.remove_polygon(random_index)

    # Add random polygon to DNA
    def add_polygon(self):
        x_points = np.random.random_integers(low=0,high=self.max_x,size=3).tolist()
        y_points = np.random.random_integers(low=0,high=self.max_y,size=3).tolist()
        points = zip(x_points, y_points)
        color = tuple(np.random.random_integers(low=0, high=255, size=4).tolist())
        new_polygon = Polygon(points, color)
        self.polygons.append(new_polygon)

    # Remove specified polygon from DNA
    def remove_polygon(self, polygon_index):
        del self.polygons[polygon_index]

    # Mutate polygon order
    def mutate_polygon_order(self):
        # Get random polygon
        random_remove_index = np.random.randint(low=0, high=self.polygon_count)
        random_insert_index = np.random.randint(low=0, high=self.polygon_count)
        polygon = polygons.pop(random_remove_index)
        # Insert it back into new spot
        polygons.insert(random_insert_index, polygon)

    # Mutate specified polygon
    def mutate_polygon(self, polygon):
        # Mutate polygon point count
        if self.will_mutate(self.mutate_polygon_point_count_rate):
            self.mutate_polygon_point_count(polygon)

        # Mutate polygon location
        if self.will_mutate(self.mutate_polygon_location_rate):
            self.mutate_polygon_location(polygon)

        # Mutate one polygon point
        if self.will_mutate(self.mutate_polygon_point_rate):
            self.mutate_polygon_point(polygon)      

        # Mutate polygon color
        if self.will_mutate(self.mutate_polygon_color_rate):
            self.mutate_polygon_color(polygon)

    # Mutate number of points in specified polygon
    def mutate_polygon_point_count(self, polygon):
        if np.random.rand() < 0.5:
            # Grab random polygon and random point
            random_polygon_index = np.random.randint(low=0, high=self.polygon_count)
            polygon = self.polygons[random_index]
            random_point_index = np.random.randint(low=1, high=polygon.point_count)
            point_x, point_y = polygon.points[random_point_index]
            # Grab point to "left" of point
            previous_point_x, previous_point_y = polygon.points[random_point_index-1]

            # Create and add point that is inbetween point and previous point
            new_x = (previous_point_x + point_x) / 2
            new_y = (previous_point_y + point_y) / 2
            new_point = (new_x, new_y)

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

        # Use normal distribution to find displacement
        dx = self.max_x * np.random.normal(scale=0.1)
        dy = self.max_y * np.random.normal(scale=0.1)

        # Make sure to stay in bounds
        np.clip(dx, pixels_to_left, pixels_to_right)
        np.clip(dy, pixels_to_bottom, pixels_to_top)

        # Move the polygon
        polygon.move(delta_x = int(dx), delta_y = int(dy))

    # Mutate random polygon point
    def mutate_polygon_point(self, polygon):
        random_index = np.random.randint(low=0, high=polygon.point_count)
        point_x, point_y = polygon.points[random_index]

        # Number of pixels to edge of image
        pixels_to_left   = point_x
        pixels_to_right  = self.max_x - point_x
        pixels_to_top    = self.max_y - point_y
        pixels_to_bottom = point_y

        # Use normal distribution to find displacement
        dx = self.max_x * np.random.normal(scale=0.1)
        dy = self.max_y * np.random.normal(scale=0.1)

        # Make sure to stay in bounds
        np.clip(dx, pixels_to_left, pixels_to_right)
        np.clip(dy, pixels_to_bottom, pixels_to_top)

        # Update point
        new_points = polygon.points
        new_points[random_index] = (point_x + int(dx), point_y + int(dy))
        polygon.points = new_points

    # Mutate the selected polygon color
    def mutate_polygon_color(self, polygon):
        dc = 255*self.max_x * np.random.normal(scale=0.1, size=4).astype(int)
        new_color = (
            np.clip(polygon.color[0] + dc[0], 0, 255),
            np.clip(polygon.color[1] + dc[1], 0, 255),
            np.clip(polygon.color[2] + dc[2], 0, 255),      
            np.clip(polygon.color[3] + dc[3], 0, 255),
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

    # Create copy of self and replicate
    def breed(self):
        # Clone polygons
        polygons_copy = copy.deepcopy(self.polygons)
        child = DNA(polygons_copy, self.master_image)    
 
        # Replicate and possibly mutate
        child.mutate()
 
        return child

    # Create Copy of DNA
    def copy(self):
        polygons_copy = copy.deepcopy(self.polygons)
        dna_copy = DNA(polygons_copy, self.master_image)

        return dna_copy
