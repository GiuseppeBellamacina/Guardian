from datetime import datetime
from enum import Enum
import pandas as pd
import random

class AgeGroup(Enum):
    INFANT = (0, 1, 0.01)  # Neonati fino a 1 anno
    TODDLER = (2, 3, 0.01)  # Bambini piccoli, 2-3 anni
    
    EARLY_CHILD = (4, 6, 0.04)  # Prima infanzia
    MIDDLE_CHILD = (7, 9, 0.04)  # Infanzia intermedia
    LATE_CHILD = (10, 12, 0.04)  # Preadolescenza

    EARLY_TEEN = (13, 15, 0.05)  # Adolescenti
    LATE_TEEN = (16, 17, 0.05)  # Fine adolescenza

    EARLY_YOUTH = (18, 21, 0.08)  # Giovani adulti
    LATE_YOUTH = (22, 25, 0.07)  # Fine gioventù

    EARLY_YOUNG_ADULT = (26, 30, 0.07)  # Prima età adulta
    LATE_YOUNG_ADULT = (31, 35, 0.07)  # Fine prima età adulta

    EARLY_MIDDLE_AGED_ADULT = (36, 40, 0.07)  # Prima età media
    MIDDLE_AGED_ADULT = (41, 45, 0.07)  # Età media
    LATE_MIDDLE_AGED_ADULT = (46, 50, 0.07)  # Fine età media

    EARLY_SENIOR = (51, 55, 0.04)  # Inizio terza età
    LATE_SENIOR = (56, 60, 0.04)  # Fine terza età

    EARLY_LATE_SENIOR = (61, 65, 0.04)  # Anziani in buona salute
    LATE_LATE_SENIOR = (66, 70, 0.04)  # Anziani più avanzati

    EARLY_ELDERLY = (71, 75, 0.03)  # Inizio anzianità
    MIDDLE_ELDERLY = (76, 80, 0.03)  # Anzianità intermedia
    LATE_ELDERLY = (81, 85, 0.02)  # Fine anzianità

    EARLY_LATE_ELDERLY = (86, 90, 0.01)  # Anziani molto avanzati
    CENTENARIAN = (91, 110, 0.01)  # Ultracentenari
    
    def __le__(self, other):
        return self.value[0] <= other.value[0]
    
    def __ge__(self, other):
        return self.value[0] >= other.value[0]
    
    def __lt__(self, other):
        return self.value[0] < other.value[0]
    
    def __gt__(self, other):
        return self.value[0] > other.value[0]


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
        return f"{self.year}-{self.month:02}-{self.day:02}"

class Age():
    """
    Represents a person's age.
    """
    def __init__(self, age_value: int, group: AgeGroup):
        self.age_value = age_value
        self.group = group
    
    def __le__(self, other: 'Age'):
        return self.age <= other.age
    
    def __ge__(self, other: 'Age'):
        return self.age >= other.age
    
    def __lt__(self, other: 'Age'):
        return self.age < other.age
    
    def __gt__(self, other: 'Age'):
        return self.age > other.age
        

class FileReader():
    """
    Reads data from a file.
    """
    @staticmethod
    def read_simple(file_path):
        lines = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                lines.append(line.strip())
        return lines
    
    @staticmethod
    def read_csv(file_path, object_type=None):
        df = pd.read_csv(file_path, encoding='utf-8')
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
    
    def get_gender(self) -> str:
        return random.choice(['M', 'F'])

    def get_age(self, **kwargs) -> Age:
        """
        Restituisce un'età casuale in anni.
        
        **kwargs:
            - group: AgeGroup
              Usa un gruppo specifico per generare l'età.
            
            - similar_to: int
              Genera un'età simile a quella fornita.
            
            - n: int
              Numero massimo di gruppi di età con cui allontanarsi dal gruppo di età target.
        """
        group = kwargs.get('group')
        similar_to = kwargs.get('similar_to')
        n = kwargs.get('n', 0)
        
        if similar_to is not None:
            group = self._get_age_group(similar_to, n)
        
        if group is None:
            group = random.choices(
                list(AgeGroup), 
                weights=[age_group.value[2] for age_group in AgeGroup]
            )[0]
        elif not isinstance(group, AgeGroup):
            raise ValueError("group must be un'istanza di AgeGroup")
        
        min_age, max_age, _ = group.value
        return Age(random.randint(min_age, max_age), group)
    
    def _get_age_group(self, age, n=0) -> AgeGroup:
        """
        Restituisce un gruppo di età entro `n` gruppi di distanza dall'età fornita,
        usando pesi per favorire i gruppi più vicini.
        """
        age_groups = list(AgeGroup)
        
        # Trova il gruppo target dell'età fornita
        target_group_index = None
        age = int(age)
        for i, age_group in enumerate(age_groups):
            min_age, max_age, _ = age_group.value
            if min_age <= age <= max_age:
                target_group_index = i
                break
        
        if age < 0:
            return AgeGroup.INFANT
        if age > 110:
            return AgeGroup.CENTENARIAN
        
        if target_group_index is None:
            return None

        if n == 0:
            return age_groups[target_group_index]
        
        # Definisce l'intervallo di gruppi vicino a target_group_index, limitato da n
        start = max(0, target_group_index - n)
        end = min(len(age_groups), target_group_index + n + 1)
        nearby_groups = age_groups[start:end]
        
        # Calcola i pesi in base alla distanza dal gruppo target
        weights = [1 / (abs(target_group_index - i) + 1) for i in range(start, end)]
        
        # Seleziona un gruppo dall'intervallo con probabilità pesata
        return random.choices(nearby_groups, weights=weights, k=1)[0]
    
    def get_name(self, gender) -> str:
        if gender not in ['M', 'F']:
            raise ValueError
        if gender == 'M':
            return random.choice(self.male_names)
        else:
            return random.choice(self.female_names)
    
    def get_last_name(self) -> str:
        return random.choice(self.last_names)

    def get_city(self, city: City = None) -> City:
        """
        Restituisce una città casuale, con probabilità ponderate per vicinanza
        rispetto alla città fornita.
        
        - Se `city` è fornita, seleziona casualmente uno dei criteri di vicinanza (nome, regione, zona) con un peso predefinito.
        - Se `city` non è fornita, restituisce una città casuale.
        """
        criteria = ["name", "region", "zone", None]
        weights = [0.4, 0.3, 0.2, 0.1]
        if city:
            selected_criterion = random.choices(criteria, weights, k=1)[0]
            if selected_criterion:
                filter_value = getattr(city, selected_criterion)
                if selected_criterion == "name":
                    return city
                else:
                    return random.choice([c for c in self.cities if getattr(c, selected_criterion) == filter_value])
        return random.choice(self.cities)

    def get_birthdate(self, age) -> Date:
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