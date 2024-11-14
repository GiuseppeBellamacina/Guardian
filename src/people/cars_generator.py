from person import Person
from utilities import Date, FileReader, AgeGroup
from datetime import datetime
import random

class CarAssigner:
    def __init__(self, people: list[Person], generator: 'CarGenerator'):
        try:
            print("\33[1;33m[CarAssigner]\33[0m: Generation started")
            self.people = self._filter_drivers(self._flatten(people))
            self.generator = generator
            self.assignments = self._assign_cars()
            print("\33[1;32m[CarAssigner]\33[0m: Generation completed")
        except Exception as e:
            print("\33[1;31m[CarAssigner]\33[0m: Generation failed")
            print(e)
    
    def _flatten(self, lst):
        return [item for sublist in lst for subsublist in sublist for item in subsublist]
    
    def _filter_drivers(self, lst):
        return [p for p in lst if AgeGroup.EARLY_YOUTH <= p.age.group < AgeGroup.LATE_ELDERLY]
    
    def _assign_cars(self):
        assignments = {}
        for p in self.people:
            if random.random() <= 0.7:
                assignments[p.cf] = Car(owner=p, generator=self.generator)
        return assignments
    
    def write_to_csv(self, filename="cars_assign.csv"):
        c = 0
        with open(filename, "w", encoding='utf-8') as f:
            f.write("plate,manifacturer,model,last_revision,insurance_expiration,is_stolen,owner\n")
            for k, v in self.assignments.items():
                f.write(f"{v.plate},{v.manifacturer},{v.model},{v.last_revision},{v.insurance_expiration},{v.is_stolen},{k}\n")
                c += 1
        f.close()
        print(f"\33[1;34m[CarAssigner]\33[0m: {c} cars written to {filename}")

class Car:
    def __init__(self,
                 owner: Person |None=None,
                 generator: 'CarGenerator'=None):
        self.owner = owner
        self.plate = generator.generate_plate()
        self.manifacturer, self.model = generator.get_manifacturer_and_model()
        self.last_revision = generator.generate_last_revision()
        self.insurance_expiration = generator.generate_insurance_expiration()
        self.is_stolen = random.choices([True, False], weights=[0.03, 0.97])[0]
    
    def __str__(self):
        return f'{self.manifacturer} {self.model}, plate: {self.plate}, last revision: {self.last_revision}, insurance expiration: {self.insurance_expiration}, stolen: {self.is_stolen}'
    
    def __repr__(self) -> str:
        return self.__str__()

class CarGenerator:
    def __init__(self, cars_file="../../data/files/cars.csv"):
        try:
            print("\33[1;33m[CarGenerator]\33[0m: Initializing car generator")
            self.cars = FileReader.read_csv(cars_file)
            self.generated_plates = set()
            print("\33[1;32m[CarGenerator]\33[0m: Data are ready")
        except Exception as e:
            print("\33[1;31m[CarGenerator]\33[0m: Error: " + str(e))
    
    def generate_date(self, year: int) -> Date:
        month = random.randint(1, 12)
        if month in [1, 3, 5, 7, 8, 10, 12]:
            day = random.randint(1, 31)
        elif month in [4, 6, 9, 11]:
            day = random.randint(1, 30)
        else:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                day = random.randint(1, 29)
            else:
                day = random.randint(1, 28)
        return Date(day, month, year)

    def generate_last_revision(self) -> Date:
        current_year = datetime.now().year
        revision_year = current_year - random.choices([0, 1, 2, 3], weights=[0.45, 0.4, 0.1, 0.05])[0]
        return self.generate_date(revision_year)

    def generate_insurance_expiration(self) -> Date:
        current_year = datetime.now().year
        expiration_year = current_year + random.choices([-2, -1, 0, 1], weights=[0.05, 0.05, 0.1, 0.8])[0]
        return self.generate_date(expiration_year)

    def get_manifacturer_and_model(self) -> tuple[str, str]:
        return random.choice(self.cars)
    
    def generate_plate(self) -> str:
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '0123456789'
        plate = ''.join(random.choices(letters, k=2)) + ''.join(random.choices(numbers, k=3)) + ''.join(random.choices(letters, k=2))
        while plate in self.generated_plates:
            plate = ''.join(random.choices(letters, k=2)) + ''.join(random.choices(numbers, k=3)) + ''.join(random.choices(letters, k=2))
        self.generated_plates.add(plate)
        return plate