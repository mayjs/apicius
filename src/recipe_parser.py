from recipe import Ingredient, Quantity, Step, Recipe
import commonmark
from argparse import ArgumentParser, FileType
from bs4 import BeautifulSoup
import re
import sys
import os

with open(os.path.join(os.path.dirname(__file__), 'html_template.html')) as f:
    html_template = f.read()


def dump_nodes(ast):
    indent = 0
    for n, entering in ast.walker():
        n.on_enter = print
        if not entering:
            indent -= 4
        if entering:
            print(" "*indent,n, n.level)
        if entering and n.t != "text":
            indent += 4


def process_ast(ast):
    res = Recipe(None)
    metadata = dict()

    class ParserState:
        def consume_node(self, node, entering):
            pass

    class ReadName(ParserState):
        def __init__(self):
            self.content = ""
            self.stack = 0

        def consume_node(self, node, entering):
            if self.stack > 0:
                if node.t == "heading" and entering and node.level==1:
                    self.stack += 1
                if node.t == "heading" and not entering and node.level==1:
                    self.stack -= 1
                if self.stack == 0:
                    res.title = self.content
                    return ReadParts()
                self.content += node.literal

            if node.t == "heading" and entering and node.level==1:
                self.stack = 1
                metadata[node] = { "is_name": True }

            return self

    class ReadParts(ParserState):
        def __init__(self):
            pass

        def consume_node(self, node, entering):
            return self

    state = ReadName()
    for n, entering in ast.walker():
        state = state.consume_node(n, entering)

    return res, metadata

def _add_classes(tag, *args):
    tag['class'] = tag.get("class", []) + list(args)

def parse_recipe(input):
    """
    Parse a recipe from markdown

    Args:
        input: str, The recipe as markdown
    """
    parser = commonmark.Parser()
    ast = parser.parse(input)

    # dump_nodes(ast)
    # res, meta = process_ast(ast)
    # print(res.title)


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
                match = re.match(r"^(?P<amount>(?P<number>[\d\.]+)(?P<unit>\w*))\s*(?P<name>.*)$", item.text)
                if not match:
                    print(f"warning: could not parse ingredient {item.text}", file=sys.stderr)
                else:
                    number = soup.new_tag("span", **{"class": ["ingredient-number"]})
                    number.string = match.group("number")
                    unit = soup.new_tag("span", **{"class": ["ingredient-unit"]})
                    unit.string = match.group("unit")
                    name = soup.new_tag("span", **{"class": ["ingredient-name"]})
                    name.string = match.group("name")
                    item.contents.clear()
                    item.extend([number, unit, name])
                    # TODO: Add to summary
        wrapping_div = soup.new_tag("div", **{"class": ["step-container"]})
        thing = step.findNextSibling()
        while thing is not None and thing != nextPart and (next is None or soup.index(thing) < soup.index(next)):
            new_thing = thing.findNextSibling()
            thing.wrap(wrapping_div)
            thing = new_thing
        desc_div = soup.new_tag("div", **{"class": ["step-description"]})
        for el in ingredients.findNextSiblings(): # TODO: Ingredients is None
            el.wrap(desc_div)

    print(html_template.format(body=soup.prettify()))



if __name__ == "__main__":
    parser = ArgumentParser(description="Simple test interface for the recipe parser")
    parser.add_argument("file", type=FileType(), help="A markdown file to read")

    args = parser.parse_args()
    parse_recipe(args.file.read())
