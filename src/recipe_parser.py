from recipe import Ingredient, Quantity, Step, Recipe
import commonmark
from argparse import ArgumentParser, FileType
from bs4 import BeautifulSoup
import re
import sys
import os
from collections import defaultdict
import itertools

with open(os.path.join(os.path.dirname(__file__), 'html_template.html')) as f:
    html_template = f.read()

def _add_classes(tag, *args):
    tag['class'] = tag.get("class", []) + list(args)

def populate_tag_with_ingredient(soup, parent, number, unit, name):
    if number:
        number_tag = soup.new_tag("span", **{"class": ["ingredient-number"]})
        number_tag.string = str(float(number)).rstrip("0").rstrip(".")
        unit_tag = soup.new_tag("span", **{"class": ["ingredient-unit"]})
        unit_tag.string = unit
        parent.extend((number_tag, unit_tag))
    name_tag = soup.new_tag("span", **{"class": ["ingredient-name"]})
    name_tag.string = name
    parent.append(name_tag)

def build_summary(soup: BeautifulSoup, ingredient_dict: dict):
    """
    Builds a html summary of ingredients as a list
    """
    list_tag = soup.new_tag("ul")
    _add_classes(list_tag, "ingredients", "summarized-ingredients")

    specific_ingredients   = [(name, unit, number) for ((name,unit),number) in ingredient_dict.items() if number != 0]
    unspecific_ingredients = [(name, unit, number) for ((name,unit),number) in ingredient_dict.items() if number == 0]
    specific_ingredients = sorted(specific_ingredients, key=lambda x: x[0]) # Sort by name
    unspecific_ingredients = sorted(unspecific_ingredients, key=lambda x: x[0]) # Sort by name
    for name, unit, number in itertools.chain(specific_ingredients, unspecific_ingredients):
        li = soup.new_tag("li")
        _add_classes(li, "ingredient")
        populate_tag_with_ingredient(soup, li, number, unit, name)
        list_tag.append(li)

    heading = soup.new_tag("h2")
    heading.string = "Zutaten"

    section = soup.new_tag("section")
    section.extend((heading, list_tag))
    return section


def parse_recipe(input):
    """
    Parse a recipe from markdown

    Args:
        input: str, The recipe as markdown
    """
    parser = commonmark.Parser()
    ast = parser.parse(input)

    renderer = commonmark.HtmlRenderer()
    html = renderer.render(ast)
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup.prettify())
    recipe = Recipe(soup.h1.text)
    steps = soup.find("h2", text="Zubereitung")

    if (nextPart := steps.findNextSibling("h2")) is not None:
        steps_upto = soup.index(nextPart)
    else:
        steps_upto = float("inf")

    ingredient_summary = defaultdict(lambda: 0)
    for step in steps.findNextSiblings("h3"):
        if soup.index(step) >= steps_upto:
            break
        next = step.findNextSibling("h3")
        ingredients = step.findNextSibling("ul") # TODO: Handle ingredients is None
        if next is None or soup.index(ingredients) < soup.index(next):
            _add_classes(ingredients, "ingredients", "step-ingredients")
            # Collect ingredients
            for item in ingredients.findChildren("li"):
                _add_classes(item, "ingredient")
                match = re.match(r"^(?P<amount>(?P<number>[\d\.]+)(?P<unit>\S*))?\s*(?P<name>.*)$", item.text)
                if not match:
                    print(f"warning: could not parse ingredient {item.text}", file=sys.stderr)
                else:
                    item.contents.clear()
                    populate_tag_with_ingredient(soup, item, match.group("number"), match.group("unit"), match.group("name"))
                    ingredient_summary[(match.group("name"), match.group("unit"))] += float(match.group("number") or 0)
        wrapping_div = soup.new_tag("div", **{"class": ["step-container"]})
        thing = step.findNextSibling()
        while thing is not None and thing != nextPart and (next is None or soup.index(thing) < soup.index(next)):
            new_thing = thing.findNextSibling()
            thing.wrap(wrapping_div)
            thing = new_thing
        desc_div = soup.new_tag("div", **{"class": ["step-description"]})
        for el in ingredients.findNextSiblings(): # TODO: Ingredients is None
            el.wrap(desc_div)

    summary_tag = build_summary(soup, ingredient_summary)
    steps.insert_before(summary_tag)

    print(html_template.format(body=soup.prettify()))



if __name__ == "__main__":
    parser = ArgumentParser(description="Simple test interface for the recipe parser")
    parser.add_argument("file", type=FileType(), help="A markdown file to read")

    args = parser.parse_args()
    parse_recipe(args.file.read())
