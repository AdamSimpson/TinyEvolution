import numpy as np
from PIL import Image,ImageDraw,ImageChops
import Polygon
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
        self.mutate_polygon_count = 0.1;
        self.mutate_polygon_rate = 0.1;
        self.mutate_polygon_point_count_rate = 0.5;
        self.mutate_polygon_location_rate = 0.6;
        self.mutate_polygon_point_rate = 0.3;
        self.mutate_polygon_color_rate = 0.8;

    def polygon_count(self):
        return len(self.polygons)

    # fitness property is calculated if == None
    @property
    def fitness(self):
        if self._fitness == None:
            return self.calculate_fitness()
        else:
            return self._fitness

    # When replicated there is a chance of mutation for each polygon
    # as well as the total number of polygons
    def replicate(self):
        # Reset fitness and image to None
        self._fitness = None
        self.image = None

        # check if each polygon should mutate
        for polygon in self.polygons:
            will_mutate = np.random.rand() < self.mutation_rate
            if will_mutate:
                self.mutate_polygon(polygon)

        # check if polygon count should mutate
        will_mutate = np.random.rand() < self.mutate_polygons_rate
        if will_mutate:
            self.mutate_polygon_count()

    # Mutate number of polygons in DNA
    def mutate_polygon_count(self):
        if np.random.rand() < 0.5 and self.polygon_count() < self.max_polygon_count:
            self.add_polygon()
        elif self.polygon_count() > self.min_polygon_count:
            random_index = np.random.randint(0, height=self.polygon_count)
            self.remove_polygon(random_index)

    # Add random polygon to DNA
    def add_polygon(self):
        new_polygon = Polygon()
        self.polygons.append(new_polygon)

    # Remove specified polygon from DNA
    def remove_polygon(self, polygon_index):
        del self.polygons[polygon_index]

    # Mutate specified polygon
    def mutate_polygon(self, polygon):
        # Mutate polygon point count
        will_mutate = np.random.rand() < self.mutate_polygon_point_count_rate
        if will_mutate:
            self.mutate_polygon_point_count(polygon)

        # Mutate polygon location
        will_mutate = np.random.rand() < self.mutate_polygon_location_rate
        if will_mutate:
            self.mutate_polygon_location(polygon)

        # Mutate one polygon point
        will_mutate = np.random.rand() < self.mutate_polygon_point_rate
        if will_mutate:
            self.mutate_polygon_point(polygon)      

        # Mutate polygon color
        will_mutate = np.random.rand() < self.mutate_polygon_color_rate
        if will_mutate:
            self.mutate_polygon_color(polygon)

    # Mutate number of points in specified polygon
    def mutate_polygon_point_count(self, polygon):
        if np.rand() < 0.5:
            polygon.add_point()
        else:
            random_index = np.random.randint(low=0, high=polygon.point_count)
            polygon.remove_point(random_index)

    # Translate the polygon up/down and left/right
    # This needs to be fixed to something better
    def mutate_polygon_location(self, polygon):
        # Number of pixels to edge of image
        pixels_to_left   = polygon.min_x()
        pixels_to_right  = self.max_x - polygon.max_x()
        pixels_to_top    = self.max_y - polygon.max_y()
        pixels_to_bottom = polygon.min_y()

        max_change_x = 0.1 * self.max_x
        max_change_y = 0.1 * self.max_y

        # Generate random displacement
        dx = np.random.randint(low=-max_change_x, high=max_change_x)
        dy = np.random.randint(low=-max_change_y, high=max_change_y)

        # Make sure not to go out of bounds
        if polygon.max_x + dx > self.max_x:
            dx = pixels_to_right
        elif polygon.min_x + dx < 0:
            dx = pixels_to_left
        if polygon.max_y + dy > self.max_y:
            dy = pixels_to_top
        elif polygon.min_y + dy < 0:
            dy = pixels_to_bottom

        polygon.move(delta_x = dx, delta_y = dy)

    # Mutate random polygon point
    # This needs to be fixed to something better
    def mutate_polygon_point(self, polygon):
        random_index = np.random.randint(low=0, hight=polygon.point_count())
        point_x, point_y = polygon.points[random_index]

        # Number of pixels to edge of image
        pixels_to_left   = point_x
        pixels_to_right  = self.max_x - point_x
        pixels_to_top    = self.max_y - point_y
        pixels_to_bottom = point_y

        max_change_x = 0.1 * self.max_x
        max_change_y = 0.1 * self.max_y

        # Generate random displacement
        dx = np.random.randint(low=-max_change_x, high=max_change_x)
        dy = np.random.randint(low=-max_change_y, high=max_change_y)

        # Make sure not to go out of bounds
        if polygon.max_x + dx > self.max_x:
            dx = pixels_to_right
        elif polygon.min_x + dx < 0:
            dx = pixels_to_left
        if polygon.max_y + dy > self.max_y:
            dy = pixels_to_top
        elif polygon.min_y + dy < 0:
            dy = pixels_to_bottom

        new_points = polygon.points
        new_points[random_index] = (point_x + dx, point_y + dy)
        polygon.points = new_points

    # Mutate the selected polygon color
    def mutate_polygon_color(self, polygon):
        max_change = 25
        dc = np.random.randint(low=-max_change, high=max_change, size=4)
        new_color = (
            polygon.color[0] + dc[0],
            polygon.color[1] + dc[1],
            polygon.color[2] + dc[2],      
            polygon.color[3] + dc[3],
        )
        polygon.color = new_color

    # Render the DNA to image
    def render(self):
        del self.image
        self.image = Image.new("RGB", (self.max_x, self.max_y))
        draw = ImageDraw.Draw(image,"RGBA")

        for polygon in self.polygons:
            draw.polygon(polygon.points, polygon.color)

        del draw

    # Save the image and Polygon class to disk
    def save(self):
        # Save image
        self.image.save("Evolve.png")

        # Save DNA to disk
        with open("Evolve_Polygon.dump", "wb") as output:
            cPickle.dump(self, output, cPickle.HIGHEST_PROTOCOL)

    # Compute fitness of DNA
    def calculate_fitness(self):
        diff = ImageChops.difference(self.image, self.master_image)              
        self._fitness = ImageState.sum(diff)

    # create copy of self and replicate
    def create_child(self):
        # Clone
        polygons_copy = copy.deepcopy(self.polygons)
        child = DNA(polygon_copy, self.master_image)    
 
        child.replicate()
 
        # Replicate
        return child
