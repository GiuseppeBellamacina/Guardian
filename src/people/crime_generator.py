from utilities import FileReader, AgeGroup
from person import Person
import random

class Crime:
    def __init__(self, type, desc, score, prob):
        self.type = type
        self.desc = desc
        self.score = score
        self.prob = prob
    
    def __str__(self):
        return f'{self.type}, {self.desc}, {self.score}, {self.prob}'

    def __repr__(self):
        return self.__str__()

class CrimeGenerator:
    def __init__(self, people: list[Person], crimes_file='../../data/files/crimes.csv'):
        try:
            print("\33[1;33m[CrimeGenerator]\33[0m: Generation started")
            self.crimes = FileReader.read_csv(crimes_file, Crime)
            self.people = self._filter_people(self._flatten(people))
            self.assignments = self._assign_crime()
            print("\33[1;32m[CrimeGenerator]\33[0m: Generation completed")
        except Exception as e:
            print("\33[1;31m[CrimeGenerator]\33[0m: Generation failed")
            print(e)
    
    def _flatten(self, lst):
        return [item for sublist in lst for subsublist in sublist for item in subsublist]
    
    def _filter_people(self, lst):
        return [p for p in lst if AgeGroup.LATE_TEEN <= p.age.group <= AgeGroup.EARLY_LATE_ELDERLY]
    
    def _assign_crime(self):
        index = 0
        assignments = {}
        for p in self.people:
            for c in self.crimes:
                if random.random() <= c.prob / 10:
                    assignments[index] = (p.cf, c)
                    index += 1
        return assignments

    def write_to_csv(self, filename="crimes_assign.csv"):
        c = 0
        with open(filename, "w", encoding='utf-8') as f:
            f.write("crime_id,criminal,type,description,severity_score\n")
            for k, v in self.assignments.items():
                f.write(f"{k},{v[0]},{v[1].type},{v[1].desc},{v[1].score}\n")
                c += 1
        f.close()
        print(f"\33[1;34m[CrimeGenerator]\33[0m: {c} crimes written to {filename}")