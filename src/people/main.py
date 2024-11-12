from family_graph import FamilyGraph
from utilities import DataGenerator, AgeGroup
import random

generator = DataGenerator()
graphs: list[FamilyGraph] = []

oldest_groups = list(AgeGroup)[-5:]
N = 15

for i in range(N):
    graphs.append(FamilyGraph(generator, 10, random.choice(oldest_groups)))

for i, graph in enumerate(graphs):
    graph.generate_full_family_tree()
    graph.write_to_csv(filename="families.csv", append=i)