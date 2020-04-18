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

def _populate_tag_with_ingredient(soup, parent, number, unit, name):
    if number:
        number_tag = soup.new_tag("span", **{"class": ["ingredient-number"], "data-default-amount": str(number)})
        number_tag.string = str(float(number)).rstrip("0").rstrip(".")
        unit_tag = soup.new_tag("span", **{"class": ["ingredient-unit"]})
        unit_tag.string = unit
        parent.extend((number_tag, unit_tag))
    name_tag = soup.new_tag("span", **{"class": ["ingredient-name"]})
    name_tag.string = name
    parent.append(name_tag)

def _build_summary(soup: BeautifulSoup, ingredient_dict: dict):
    """
    Builds a html summary of ingredients as a list
    """
    list_tag = soup.new_tag("ul")
    _add_classes(list_tag, "ingredients", "summarized-ingredients")

    # We sort ingredients on two keys: First of all we want to group ingredients with specific amounts and ingredients without specific amounts.
    # Within those groups we use the name of the ingredient.
    ingredients = sorted([(name, unit, number) for ((name,unit),number) in ingredient_dict.items()],
                         key=lambda x:(x[2]==0, x[0].lower()))
    for name, unit, number in ingredients:
        li = soup.new_tag("li")
        _add_classes(li, "ingredient")
        _populate_tag_with_ingredient(soup, li, number, unit, name)
        list_tag.append(li)

    heading = soup.new_tag("h2")
    heading.string = "Zutaten"

    multiplier = soup.new_tag("form")
    _add_classes(multiplier, "multiplier-form")
    label = soup.new_tag("label", **{"for": "multiplier-input"})
    label.string = "Multiplikator:"
    inp = soup.new_tag("input", type="number", step="any", min="0", value="1", id="multiplier-input")
    _add_classes(inp, "multiplier-input")
    btn = soup.new_tag("button", type="button", onclick="scaleIngredients();")
    btn.string = "Umrechnen"
    _add_classes(btn, "multiplier-submit")
    multiplier.extend((label, inp, btn))

    section = soup.new_tag("section")
    section.extend((heading, list_tag, multiplier))
    return section

def _sectionize_from_heading(soup, tag):
    def heading_level(tag):
        if tag is None:
            return 0
        match = re.match(r"h(\d)", tag.name)
        if match is None:
            return float("inf")
        return int(match.group(1))

    level = heading_level(tag)
    wrapper = soup.new_tag("section", id=tag.string)
    tag.wrap(wrapper)
    while not heading_level(sibling := wrapper.findNextSibling()) <= level:
        sibling.wrap(wrapper)
    return wrapper



def parse_and_render_recipe(input, js_path_prefix="", css_path_prefix=""):
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
                    _populate_tag_with_ingredient(soup, item, match.group("number"), match.group("unit"), match.group("name"))
                    ingredient_summary[(match.group("name"), match.group("unit"))] += float(match.group("number") or 0)

        wrapping_div = _sectionize_from_heading(soup, step)
        _add_classes(wrapping_div, "step-container")
        desc_div = soup.new_tag("div", **{"class": ["step-description"]})
        for el in ingredients.findNextSiblings(): # TODO: Ingredients is None
            el.wrap(desc_div)

    summary_tag = _build_summary(soup, ingredient_summary)
    steps.insert_before(summary_tag)

    tags = set()
    tags_el = soup.find("h2", text="Schlagwörter")
    if tags_el is None:
        tags_el = soup.find("h2", text="Tags")
    if tags_el is not None:
        tags_section = _sectionize_from_heading(soup, tags_el)
        _add_classes(tags_section, "tags")
        for ul in tags_section.findChildren("ul"):
            _add_classes(ul, "tags-list")
            for li in ul.findChildren("li"):
                _add_classes(li, "tag")
                tags.add(li.string)

    html_out = html_template.format(body=soup.prettify(), js_path_prefix=js_path_prefix, css_path_prefix=css_path_prefix)

    return soup.h1.text, ingredient_summary, tags, html_out



if __name__ == "__main__":
    parser = ArgumentParser(description="Simple test interface for the recipe parser")
    parser.add_argument("file", type=FileType(), help="A markdown file to read")

    args = parser.parse_args()
    title, ingredients, tags, html = parse_and_render_recipe(args.file.read())
    print(html)
