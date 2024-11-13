from family_graph import FamilyGraph
from workplace_generator import WorkPlaceGenerator
from school_generator import SchoolGenerator
from utilities import DataGenerator, AgeGroup
import random

generator = DataGenerator()
graphs: list[FamilyGraph] = []

oldest_groups = list(AgeGroup)[-5:] # Last 5 age groups
N = 15 # Start with 15 families
data_dir = "../../db/"

# Each graph has 10 progenitors
for i in range(N):
    graphs.append(FamilyGraph(generator, 15, random.choice(oldest_groups)))

# Generate families
for i, graph in enumerate(graphs):
    graph.generate_full_family_tree()
    graph.write_to_csv(filename=data_dir+"families.csv", append=i)

# Create schools
school_gen = SchoolGenerator([g.levels for g in graphs])
school_gen.write_to_csv(filename=data_dir+"schools.csv")
school_gen.write_attendance_to_csv(filename=data_dir+"attendance_school.csv")

# Create workplaces
workplace_gen = WorkPlaceGenerator([g.levels for g in graphs])
workplace_gen.write_to_csv(filename=data_dir+"workplaces.csv")
workplace_gen.write_attendance_to_csv(filename=data_dir+"attendance_workplace.csv")