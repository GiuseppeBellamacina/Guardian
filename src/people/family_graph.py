from utilities import DataGenerator, AgeGroup
from family import Family
from person import Person
import random

class FamilyGraph:
    """
    Generates a family graph with multiple levels.
    """
    def __init__(self, generator: DataGenerator, number_of_progenitors: int, oldest_group: AgeGroup, limit_group: AgeGroup = AgeGroup.INFANT, start_max_children: int = 8):
        print("\33[1;33m[FamilyGraph]\33[0m: Generation started")
        self.generator = generator
        self.levels = []
        self.current_level = -1
        self.generate_progenitors(number_of_progenitors, oldest_group)
        self.generate_full_family_tree(limit_group, start_max_children)
        print("\33[1;32m[FamilyGraph]\33[0m: Graph generated")
    
    def add_level(self):
        self.levels.append([])
        self.current_level += 1

    def generate_progenitors(self, number_of_progenitors: int, oldest_group: AgeGroup):
        self.add_level()
        for i in range(number_of_progenitors):
            p = Person(
                self.generator,
                age=self.generator.get_age(group=oldest_group, n=1)
            )
            self.levels[self.current_level].append(p)

    def generate_initial_families(self, max_children: int = 10):
        self.add_level()
        progenitors = [p for p in self.levels[0]]
        
        for progenitor in progenitors:
            family = Family(self.generator, progenitor)
            progenitor.set_original_family(family)
            progenitor.set_new_family(family)
            family.create_family(n_children_max=max_children)
            self.levels[0].append(family.get_partner())
            family.get_partner().set_original_family(family)
            family.get_partner().set_new_family(family)
            self.levels[1].extend(family.get_children())
    
    def generate_next_level(self, max_children: int = 4):        
        current_level_individuals = self.levels[self.current_level]
        if not current_level_individuals:
            return False
        
        min_age_group = AgeGroup.LATE_YOUTH

        males = [p for p in current_level_individuals if p.gender == 'M' and p.age.group >= min_age_group]
        females = [p for p in current_level_individuals if p.gender == 'F' and p.age.group >= min_age_group]
        
        if len(males) > len(females):
            family_roots = random.sample(males, len(females))
            potential_partners = females
        else:
            family_roots = random.sample(females, len(males))
            potential_partners = males
        
        if not family_roots:
            return False
        
        used_partners = set()
        
        self.add_level()
        added_any = False
        
        for root in family_roots:
            family = Family(self.generator, root)
            
            partner = next(
                (p for p in potential_partners 
                if p.original_family != root.original_family and p not in used_partners), 
                None
            )
            
            if partner:
                used_partners.add(partner)
                family.create_family(partner=partner, n_children_max=max_children)
            else:
                family.create_family(n_children_max=max_children, no_partner=True)
            
            root.set_new_family(family)
            
            children = family.get_children()
            self.levels[self.current_level].extend(children)
            
            if children:
                added_any = True
        return added_any

    
    def generate_full_family_tree(self, limit_group: AgeGroup = AgeGroup.INFANT, start_max_children: int = 8):
        self.generate_initial_families()
        
        while True:
            should_continue = self.generate_next_level(max_children=start_max_children)
            if not should_continue:
                break
            
            start_max_children -= 3
            next_level_individuals = self.levels[self.current_level]
            ages = [int(individual.age) for individual in next_level_individuals]
            avg_age = sum([age for age in ages]) / len(ages)
            
            if self.generator._get_age_group(avg_age) <= limit_group:
                break
        
    def write_to_csv(self, filename: str, append: bool = False):
        number_of_lines = 0
        mode = 'a' if append else 'w'
        
        with open(filename, mode, encoding='utf-8') as f:
            if not append:
                f.write("cf,name,last_name,birthdate,gender,city,gen1,gen2,partner_of\n")
            for level, individuals in enumerate(self.levels):
                for individual in individuals:
                    f.write(f"{individual.to_csv()}\n")
                    number_of_lines += 1
        f.close()
        print(f"\33[1;34m[FamilyGraph]\33[0m: Written {number_of_lines} lines to {filename}")
        