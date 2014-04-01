from PIL import Image
import numpy as np
from dna import DNA
from polygon import Polygon

def main():
    
    # Open master image in RGB mode
    master_image = Image.open("obama.png").convert(mode="RGB")   
    width, height = master_image.size

    # Create initial polygons
    polygons = []
    for i in range(200):
        x_points = np.random.random_integers(low=0,high=width,size=3).tolist()
        y_points = np.random.random_integers(low=0,high=height,size=3).tolist()
        points = zip(x_points, y_points)
        color = tuple(np.random.random_integers(low=0, high=255, size=4).tolist())
        polygon = Polygon(points, color)
        polygons.append(polygon)

    # Create initial DNA
    parent = DNA(polygons, master_image)

    # Evolve DNA and breed fittest
    for i in range(1000):
        child = parent.breed()
        if child.fitness < parent.fitness:
            parent = child

    # Save image and polygon information
    parent.save()

if __name__ == "__main__":
    main()
