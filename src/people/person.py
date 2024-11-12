from utilities import (
    DataGenerator,
    Date,
    City,
    Age
)
import re

class Person():
    """
    Represents a person with some personal information.
    """
    def __init__(self, generator: DataGenerator,
                 gender: str | None=None,
                 age: Age | None=None,
                 birthdate: Date | None=None,
                 name:str | None=None,
                 last_name: str | None=None,
                 city: City | None=None):
        self.gender = gender if gender else generator.get_gender()
        self.age = age if age else generator.get_age()
        self.birthdate = birthdate if birthdate else generator.get_birthdate(self.age.age_value)
        self.name = name if name else generator.get_name(self.gender)
        self.last_name = last_name if last_name else generator.get_last_name()
        self.city = city if city else generator.get_city()
        self.cf = CFGenerator.get_fiscal_code(self)
        self.original_family = None
        self.new_family = None
    
    def set_original_family(self, family):
        self.original_family = family
    
    def set_new_family(self, family):
        self.new_family = family
    
    def __str__(self):
        s = f"{self.name} {self.last_name}, {self.age.age_value} years old ({self.gender})\n"
        s += f"Born in {self.city}\n"
        s += f"on {self.birthdate}\n"
        s += f"CF: {self.cf}"
        return s

    def to_csv(self):
        s = ""
        s += self.cf + ","
        s += self.name + ","
        s += self.last_name + ","
        s += str(self.birthdate) + ","
        s += self.gender + ","
        s += self.city.name + ","
        
        # Solo livello 0
        if self.original_family.family_root == self or self.original_family.partner == self:
            s += ",,"
        else:
            s += self.original_family.family_root.cf + ","
            s += self.original_family.partner.cf + ","
        
        if self.new_family:
            if self.new_family.partner and self.new_family.partner != self:
                s += self.new_family.partner.cf
            elif self.new_family.family_root != self:
                s += self.new_family.family_root.cf
        
        return s
        

class CFGenerator():
    """
    Generates the fiscal code of a person.
    """
    @staticmethod
    def get_fiscal_code(person: Person):
        cf = ""
        cf += CFGenerator._get_surname_code(person.last_name)
        cf += CFGenerator._get_name_code(person.name)
        cf += CFGenerator._get_birthdate_code(person.birthdate)
        cf += CFGenerator._get_city_code(person.city)
        cf += CFGenerator._get_control_code(cf)
        return cf
    
    @staticmethod
    def _clean(s: str):
        s = s.upper()
        s = re.sub(r"[ÀÁÂÃÄÅ]", "A", s)
        s = re.sub(r"[ÈÉÊË]", "E", s)
        s = re.sub(r"[ÌÍÎÏ]", "I", s)
        s = re.sub(r"[ÒÓÔÕÖ]", "O", s)
        s = re.sub(r"[ÙÚÛÜ]", "U", s)
        s = re.sub(r"[^A-Z]", "", s)
        return s
    
    @staticmethod    
    def _get_surname_code(surname):
        surname = CFGenerator._clean(surname)
        consonants = "".join([c for c in surname if c not in "AEIOU"])
        vowels = "".join([c for c in surname if c in "AEIOU"])
        surname_code = consonants + vowels + "XXX"
        return surname_code[:3]
    
    @staticmethod
    def _get_name_code(name):
        name = CFGenerator._clean(name)
        consonants = "".join([c for c in name if c not in "AEIOU"])
        vowels = "".join([c for c in name if c in "AEIOU"])
        if len(consonants) >= 4:
            name_code = consonants[0] + consonants[2] + consonants[3]
        elif len(consonants) == 3:
            name_code = consonants[:3]
        elif len(consonants) == 2:
            name_code = consonants + vowels[0]
        elif len(consonants) == 1:
            name_code = consonants + vowels[:2]
        elif len(consonants) == 1 and len(vowels) == 1:
            name_code = consonants + vowels + "X"
        elif len(vowels) == 2:
            name_code = vowels + "X"
        else:
            name_code = consonants + vowels + "XXX"
        return name_code[:3]
    
    @staticmethod
    def _get_birthdate_code(birthdate: Date):
        months = {
            1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "H",
            7: "L", 8: "M", 9: "P", 10: "R", 11: "S", 12: "T"
        }
        year_code = str(birthdate.year)[-2:]
        month_code = months[birthdate.month]
        day_code = f"{birthdate.day:02}"
        return year_code + month_code + day_code
    
    @staticmethod
    def _get_city_code(city: City):
        return city.code

    @staticmethod
    def _get_control_code(cf):
        odd_values = {
            '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
            'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
            'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
            'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
        }
        even_values = {
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
            'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
            'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25
        }
        sum = 0
        for i, char in enumerate(cf):
            if (i + 1) % 2 == 0:
                sum += even_values[char]
            else:
                sum += odd_values[char]
        sum = sum % 26
        control_code = chr(sum + ord('A'))
        return control_code