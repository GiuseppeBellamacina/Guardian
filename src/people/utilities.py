from datetime import datetime
import pandas as pd
import random
import re

class City():
    """
    Represents a city with a code and a name.
    """
    def __init__(self, zone, region, name, code):
        self.zone = zone
        self.region = region
        self.name = name
        self.code = code
    
    def __str__(self):
        return f"{self.name} ({self.code}) in {self.region} ({self.zone})"

class Date():
    """
    Represents a date with day, month and year.
    """
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year
    
    def __str__(self):
        return f"{self.day:02}/{self.month:02}/{self.year}"

class FileReader():
    """
    Reads data from a file.
    """
    @staticmethod
    def read_simple(file_path):
        lines = []
        with open(file_path, 'r') as file:
            for line in file:
                lines.append(line.strip())
        return lines
    
    @staticmethod
    def read_pattern(file_path, pattern):
        tuples = []
        with open(file_path, 'r') as file:
            for line in file:
                tuples.append(tuple(re.split(pattern, line.strip())))
        return tuples
    
    @staticmethod
    def read_csv(file_path, object_type=None):
        df = pd.read_csv(file_path)
        if object_type:
            return [object_type(*row) for row in df.itertuples(index=False)]
        return [tuple(row) for row in df.itertuples(index=False)]

class DataGenerator():
    """
    Generates random data for a person.
    """
    def __init__(
        self,
        cities_file='../../data/province.csv',
        male_file='../../data/nomiM.txt',
        female_file='../../data/nomiF.txt',
        last_names_file='../../data/cognomi.txt'
    ):
        print("\33[1;33m[DataGenerator]\33[0m: Initializing data generator")
        try:
            self.cities = FileReader.read_csv(cities_file, City)
            self.male_names = FileReader.read_simple(male_file)
            self.female_names = FileReader.read_simple(female_file)
            self.last_names = FileReader.read_simple(last_names_file)
            print("\33[1;32m[DataGenerator]\33[0m: Data are ready")
        except Exception as e:
            print("\33[1;31m[DataGenerator]\33[0m: Error: " + str(e))
    
    def get_gender(self):
        return random.choice(['M', 'F'])

    def get_age(self):
        age_group_probabilities = {
            "baby": (0, 2, 0.02),
            "child": (3, 12, 0.1),
            "teen": (13, 17, 0.08),
            "youth": (18, 25, 0.15),
            "adult": (26, 50, 0.45),
            "senior": (51, 65, 0.12),
            "elderly": (66, 90, 0.07),
            "centenarian": (91, 110, 0.01)
        }
        group = random.choices(
            list(age_group_probabilities.keys()), 
            weights=[p[2] for p in age_group_probabilities.values()]
        )[0]
        min_age, max_age, _ = age_group_probabilities[group]
        return random.randint(min_age, max_age)

    
    def get_name(self, gender):
        if gender not in ['M', 'F']:
            raise ValueError
        if gender == 'M':
            return random.choice(self.male_names)
        else:
            return random.choice(self.female_names)
    
    def get_last_name(self):
        return random.choice(self.last_names)

    def get_city(self):
        return random.choice(self.cities)

    def get_birthdate(self, age):
        today = datetime.today()
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        if birth_month == 2:
            if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
                birth_day = random.randint(1, 29)
            else:
                birth_day = random.randint(1, 28)
        elif birth_month in {4, 6, 9, 11}:
            birth_day = random.randint(1, 30)
        else:
            birth_day = random.randint(1, 31)
        if (birth_month, birth_day) > (today.month, today.day):
            birth_year -= 1
        return Date(birth_day, birth_month, birth_year)