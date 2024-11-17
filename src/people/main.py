from family_graph import FamilyGraph
from workplace_generator import WorkPlaceGenerator
from school_generator import SchoolGenerator
from cars_generator import CarGenerator, CarAssigner
from crime_generator import CrimeGenerator
from utilities import DataGenerator, AgeGroup
import random

generator = DataGenerator()
graphs: list[FamilyGraph] = []

oldest_groups = list(AgeGroup)[-5:] # Last 5 age groups
N_GRAPHS = 25 # Start with N_GRAPHS families
N_PROGENITORS = 25 # Each family has N_PROGENITORS progenitors
data_dir = "../../data/db/"

# Create families
for i in range(N_GRAPHS):
    graphs.append(FamilyGraph(generator, N_PROGENITORS, random.choice(oldest_groups)))

n_people = 0
# Write families to csv
for i, graph in enumerate(graphs):
    n_people += graph.write_to_csv(filename=data_dir+"families.csv", append=i)
print(f"\33[1;34m[Main]\33[0m: {n_people} people written to {data_dir}families.csv")

people = [g.levels for g in graphs]

# Create schools and write to csv
school_gen = SchoolGenerator(people)
school_gen.write_to_csv(filename=data_dir+"schools.csv")
school_gen.write_attendance_to_csv(filename=data_dir+"attendance_school.csv")

# Create workplaces and write to csv
workplace_gen = WorkPlaceGenerator(people)
workplace_gen.write_to_csv(filename=data_dir+"workplaces.csv")
workplace_gen.write_attendance_to_csv(filename=data_dir+"attendance_workplace.csv")

# Create crimes and write to csv
crime_gen = CrimeGenerator(people)
crime_gen.write_to_csv(filename=data_dir+"crimes_assign.csv")

# Create cars and write to csv
car_gen = CarGenerator()
car_assigner = CarAssigner(people, car_gen)
car_assigner.write_to_csv(filename=data_dir+"cars_assign.csv")