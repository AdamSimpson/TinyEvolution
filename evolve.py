from mpi4py import MPI
from PIL import Image
import numpy as np
from dna import DNA
from polygon import Polygon
import time
import copy

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Open master image in RGB mode
    master_image = Image.open("obama.png").convert(mode="RGB")   
    width, height = master_image.size

    # Create initial polygons on rank 0 and distribute
    # Algorithm assumes parent is the same on all ranks
    if rank == 0:
        polygons = []
        for i in range(200):
            x_points = np.random.random_integers(low=0,high=width,size=3).tolist()
            y_points = np.random.random_integers(low=0,high=height,size=3).tolist()
            points = zip(x_points, y_points)
            color = tuple(np.random.random_integers(low=0, high=255, size=4).tolist())
            polygon = Polygon(points, color)
            polygons.append(polygon)
    else:
        polygons = None
    
    # Brodcast initial polygon data
    polygons = comm.bcast(polygons, root=0)

    # Create initial DNA
    parent = DNA(polygons, master_image)

    allgather_time = 0
    bcast_time = 0
    loop_time = 0

    # Evolve DNA and breed fittest
    loop_clock = time.clock()
    for i in range(10000):

        sub_parent = parent.copy()
        for j in range(10):
            child = sub_parent.breed()
            if child.fitness < sub_parent.fitness:
                sub_parent = child            
       
        # Gather all ranks fitnesses
        cf = child.fitness
        t0 = time.clock()
        fitnesses = comm.allgather(cf)
        allgather_time += time.clock() - t0

        # Find rank with minimum fitness
        best_fitness = min(fitnesses)
        best_rank = fitnesses.index(best_fitness)

        # If lowest child lower than current parent scatter child
	if best_fitness < parent.fitness:
            # Set polygon data to be sent
            if best_rank == rank:
                polygons = child.polygons
            else:
                polygons = None

            # Brodcast best polygon data
            t0 = time.clock()
            polygons = comm.bcast(polygons, root=best_rank)
            bcast_time += time.clock() - t0

            if best_rank == rank:
                parent = child
            else:
                parent = DNA(polygons, master_image)

        # Save image and polygon information
        if i%100 == 0 and rank == 0:
            parent.save(str(i))

    loop_time = time.clock() - loop_clock
    print "loop time: ", toop_time
    print "Allgather time: ", allgather_time, "bcast time: ", bcast_time

if __name__ == "__main__":
    main()
