from utilities import DataGenerator
from person import Person
import random

class Family:
    def __init__(self, generator: DataGenerator, family_root: Person):
        self.generator = generator
        self.family_root = family_root
        self.partner = None
        self.children: list[Person] = []
    
    def add_partner(self, partner: Person | None = None):
        if partner:
            self.partner = partner
        else:
            self.partner = Person(
                generator=self.generator,
                age=self.generator.get_age(similar_to=int(self.family_root.age), n=2),
                gender='F' if self.family_root.gender == 'M' else 'M',
                city=self.generator.get_city(self.family_root.city)
            )
        self.partner.set_new_family(self)
    
    def add_child(self):
        parent_ages = []
        if self.family_root:
            parent_ages.append(self.family_root.age)
        if self.partner:
            parent_ages.append(self.partner.age)
        parent_age = min([int(age) for age in parent_ages]) if parent_ages else None
        
        age = self.generator.get_age(similar_to=parent_age - 20)
        
        while any(int(child.age) == age for child in self.children):
            age.age_value += 2
               
        child = Person(
            generator=self.generator,
            age=age,
            city=self.family_root.city,
            last_name=self.family_root.last_name if self.family_root.gender == 'M' else self.partner.last_name
        )
        child.set_original_family(self)
        self.children.append(child)
    
    def get_children(self):
        return self.children
    
    def get_partner(self):
        return self.partner
    
    def create_family(self, partner: Person | None = None, n_children_max: int = 3, no_partner: bool = False):
        if not no_partner:
            self.add_partner(partner)
            n_children = random.randint(0, n_children_max)
            for _ in range(n_children):
                self.add_child()
    
    def __str__(self):
        family_root_str = f"Family_root: {self.family_root}" if self.family_root else "No family_root"
        partner_str = f"Partner: {self.partner}" if self.partner else "No partner"
        children_str = "\n".join([f"Child: {child}" for child in self.children])
        return f"{family_root_str}\n{partner_str}\nChildren:\n{children_str}"