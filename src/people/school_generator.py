from utilities import AgeGroup
import random

class School:
    def __init__(self, name, category, city):
        self.name = name
        self.category = category
        self.city = city
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()

class SchoolGenerator:
    """
    Generates schools for people.
    """
    def __init__(self, people):
        try:
            print("\33[1;33m[SchoolGenerator]\33[0m: Generation started")
            self.people = self._filter_scholars(self._flatten(people))
            self.schools = self._generate_school()
            self.attended_schools = self._assign_school()
            print("\33[1;32m[SchoolGenerator]\33[0m: Generation completed")
        except Exception as e:
            print("\33[1;31m[SchoolGenerator]\33[0m: Error: " + str(e))
            raise e
        
    def _flatten(self, lst):
        return [item for sublist in lst for subsublist in sublist for item in subsublist]
    
    def _filter_scholars(self, lst):
        return [p for p in lst if AgeGroup.MIDDLE_CHILD <= p.age.group <= AgeGroup.LATE_YOUNG_ADULT]
    
    def _generate_school(self):
        cities = {p.residence for p in self.people}
        categories = ["Scuola Elementare", "Scuola Media", "Scuola Superiore", "Università"]
        templates = ["Scuola Elementare di {0}", "Scuola Media di {0}", "Scuola Superiore di {0}", "Università di {0}"]

        schools = []
        for city in cities:
            for category, template in zip(categories, templates):
                school_name = template.format(city.name)
                schools.append(School(school_name, category, city.name))
        return schools
    
    def _assign_school(self):
        attended = {}
        for p in self.people:
            school = None
            city_schools = [s for s in self.schools if s.city == p.city.name]
            
            if p.age.group == AgeGroup.MIDDLE_CHILD:
                school = next((s for s in city_schools if s.category == "Scuola Elementare"), None)
            elif p.age.group == AgeGroup.LATE_CHILD:
                school = next((s for s in city_schools if s.category == "Scuola Media"), None)
            elif AgeGroup.EARLY_TEEN <= p.age.group <= AgeGroup.LATE_TEEN:
                school = next((s for s in city_schools if s.category == "Scuola Superiore"), None)
            else:
                university = next((s for s in city_schools if s.category == "Università"), None)
                if university:
                    if p.age.group == AgeGroup.EARLY_YOUTH and random.random() <= 0.7:
                        school = university
                    elif p.age.group == AgeGroup.LATE_YOUTH and random.random() <= 0.5:
                        school = university
                    elif p.age.group == AgeGroup.EARLY_YOUNG_ADULT and random.random() <= 0.3:
                        school = university
                    elif random.random() <= 0.1:
                        school = university
                        
            if school:
                attended[school] = attended.get(school, []) + [p.cf]
        return attended
    
    def write_to_csv(self, filename="schools.csv"):
        c = 0
        with open(filename, "w", encoding='utf-8') as f:
            f.write("school,category,city\n")
            for k, v in self.attended_schools.items():
                f.write(f"{k.name},{k.category},{k.city}\n")
                c += 1
        f.close()
        print(f"\33[1;34m[SchoolGenerator]\33[0m: {c} schools written to {filename}")
    
    def write_attendance_to_csv(self, filename="school_attendance.csv"):
        c = 0
        with open(filename, "w", encoding='utf-8') as f:
            f.write("school,cf\n")
            for k, v in self.attended_schools.items():
                for cf in v:
                    f.write(f"{k.name},{cf}\n")
                    c += 1
        f.close()
        print(f"\33[1;34m[SchoolGenerator]\33[0m: {c} attendances written to {filename}")
