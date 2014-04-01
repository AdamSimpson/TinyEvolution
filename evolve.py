from mpi4py import MPI
from PIL import Image
import numpy as np
from dna import DNA
from polygon import Polygon
import time

def main():

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Open master image in RGB mode
    master_image = Image.open("master.png").convert(mode="RGB")   
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
        # Create child
        child = parent.breed()

        # Gather all ranks fitnesses
        fitness = child.fitness
        fitnesses = comm.allgather(fitness)

        # Find rank with minimum fitness
        min_fitness = min(fitnesses)

        # If lowest child lower than current parent scatter child
        if min_fitness < parent.fitness:
            best_child_rank = fitnesses.index(min_fitness)

            # Set polygon data to be sent
            if best_child_rank == rank:
                polygons = child.polygons
            else:
                polygons = None

            # Brodcast best polygon data
            polygons = comm.bcast(polygons, root=best_child_rank)

            if best_child_rank == rank:
                parent = child
            else:
                parent = DNA(polygons, master_image)

    # Save image and polygon information
    parent.save()

if __name__ == "__main__":
    main()
