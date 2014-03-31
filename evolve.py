from PIL import Image
import numpy as np
import DNA
import Polygon

def main():
    
    # Open master image
    master_image = Image.open("master.png")    
    width, height = master_image.size

    # Create initial polygons
    polygons = []
    for i in range(50):
        x_points = np.random.random_integers(low=0,high=width,size=3).tolist()
        y_points = np.random.random_integers(low=0,high=height,size=3).tolist()
        points = zip(x_points, y_points)
        color = tuple(np.random.random_integers(low=0, high=255, size=4).tolist())
        polygon = Polygon(points, color)
        polygons.append(polygon)

    # Create initial DNA
    best_dna = DNA(polygons, master_image)

    # Evolve DNA
    for i in range(10):
        child = best_dna.create_child()
        if child.fitness < best_dna.fitness:
            best_dna = child
        else:
            del child

    best_dna.save()

if __name__ == "__main__":
    main()
