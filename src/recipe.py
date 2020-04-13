from dataclasses import dataclass
from typing import List

@dataclass
class Quantity:
    amount: float
    unit: str

@dataclass
class Ingredient:
    name: str
    quantity: Quantity

@dataclass
class Step:
    ingredients: List[Ingredient]
    information: str # TODO: This will probably be an AST section 

@dataclass
class Recipe:
    title: str
    steps: List[Step] = list
    ingredients: List[Ingredient] = list

