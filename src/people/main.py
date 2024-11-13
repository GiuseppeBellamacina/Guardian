from family_graph import FamilyGraph
from workplace_generator import WorkPlaceGenerator
from school_generator import SchoolGenerator
from utilities import DataGenerator, AgeGroup
import random

generator = DataGenerator()
graphs: list[FamilyGraph] = []

oldest_groups = list(AgeGroup)[-5:] # Last 5 age groups
N_GRAPHS = 15 # Start with N_GRAPHS families
N_PROGENITORS = 15 # Each family has N_PROGENITORS progenitors
data_dir = "../../data/db/"

# Create families
for i in range(N_GRAPHS):
    graphs.append(FamilyGraph(generator, N_PROGENITORS, random.choice(oldest_groups)))

# Write families to csv
for i, graph in enumerate(graphs):
    graph.write_to_csv(filename=data_dir+"families.csv", append=i)

# Create schools and write to csv
school_gen = SchoolGenerator([g.levels for g in graphs])
school_gen.write_to_csv(filename=data_dir+"schools.csv")
school_gen.write_attendance_to_csv(filename=data_dir+"attendance_school.csv")

# Create workplaces and write to csv
workplace_gen = WorkPlaceGenerator([g.levels for g in graphs])
workplace_gen.write_to_csv(filename=data_dir+"workplaces.csv")
workplace_gen.write_attendance_to_csv(filename=data_dir+"attendance_workplace.csv")