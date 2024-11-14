from utilities import AgeGroup
import random

class WorkPlace:
    def __init__(self, name, category, city):
        self.name = name
        self.category = category
        self.city = city
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()

class WorkPlaceGenerator:
    """
    Generates workplaces for people.
    """
    def __init__(self, people):
        try:
            print("\33[1;33m[WorkPlaceGenerator]\33[0m: Generation started")
            self.people = self._filter_workers(self._flatten(people))
            self.workplaces = self._generate_workplaces()
            self.attended_workplaces = self._assign_workplaces()
            print("\33[1;32m[WorkPlaceGenerator]\33[0m: Generation completed")
        except Exception as e:
            print("\33[1;31m[WorkPlaceGenerator]\33[0m: Error: " + str(e))
            raise e
        
    def _flatten(self, lst):
        return [item for sublist in lst for subsublist in sublist for item in subsublist]
    
    def _filter_workers(self, lst):
        return [p for p in lst if AgeGroup.EARLY_YOUTH <= p.age.group <= AgeGroup.LATE_LATE_SENIOR]
    
    def _generate_workplaces(self):
        cities = {p.residence for p in self.people}
        categories = ["Azienda", "Fabbrica", "Ufficio", "Ospedale"]
        templates = ["Azienda di {0}", "Fabbrica di {0}", "Ufficio di {0}", "Ospedale di {0}"]

        workplaces = []
        for city in cities:
            for category, template in zip(categories, templates):
                workplace_name = template.format(city.name)
                workplaces.append(WorkPlace(workplace_name, category, city.name))
        return workplaces
    
    def _assign_workplaces(self):
        attended = {}
        for p in self.people:
            workplace = None
            city_workplaces = [w for w in self.workplaces if w.city == p.city.name]
            
            if AgeGroup.EARLY_YOUTH <= p.age.group <= AgeGroup.LATE_YOUNG_ADULT:
                if p.age.group == AgeGroup.EARLY_YOUTH and random.random() <= 0.3:
                    workplace = random.choice(city_workplaces)
                elif p.age.group == AgeGroup.LATE_YOUTH and random.random() <= 0.5:
                    workplace = random.choice(city_workplaces)
                elif p.age.group == AgeGroup.EARLY_YOUNG_ADULT and random.random() <= 0.3:
                    workplace = random.choice(city_workplaces)
                elif p.age.group == AgeGroup.LATE_YOUNG_ADULT and random.random() <= 0.1:
                    workplace = random.choice(city_workplaces)
            elif AgeGroup.EARLY_MIDDLE_AGED_ADULT <= p.age.group <= AgeGroup.EARLY_LATE_SENIOR:
                workplace = random.choice(city_workplaces)
                
            if workplace:
                attended[workplace] = attended.get(workplace, []) + [p.cf]
        return attended
    
    def write_to_csv(self, filename="workplaces.csv"):
        c = 0
        with open(filename, "w", encoding='utf-8') as f:
            f.write("workplace,category,city\n")
            for k, v in self.attended_workplaces.items():
                f.write(f"{k.name},{k.category},{k.city}\n")
                c += 1
        f.close()
        print(f"\33[1;34m[WorkPlaceGenerator]\33[0m: {c} workplaces written to {filename}")
    
    def write_attendance_to_csv(self, filename="workplace_attendance.csv"):
        c = 0
        with open(filename, "w", encoding='utf-8') as f:
            f.write("workplace,cf\n")
            for k, v in self.attended_workplaces.items():
                for cf in v:
                    f.write(f"{k.name},{cf}\n")
                    c += 1
        f.close()
        print(f"\33[1;34m[WorkPlaceGenerator]\33[0m: {c} attendances written to {filename}")