from argparse import ArgumentParser
from pathlib import Path
import logging
import json
from recipe_parser import parse_and_render_recipe

def build(source: Path, dest: Path):
    recipes_path = "recipes"
    recipe_out = dest / recipes_path
    recipe_out.mkdir(exist_ok=True, parents=True)

    recipes = []
    for infile in source.iterdir():
        if infile.is_file():
            html_filename = infile.stem + ".html"
            outfile = recipe_out / html_filename
            title, ingredients, tags, html = parse_and_render_recipe(infile.read_text(), js_path_prefix="../", css_path_prefix="../")
            ingredient_names = list(set(name.lower() for name,_ in ingredients.keys()))
            meta = {"modified": infile.stat().st_mtime, "title": title, "ingredients": ingredient_names, "url": f"{recipes_path}/{html_filename}"}
            recipes.append(meta)
            outfile.write_text(html)
    recipes = sorted(recipes, key=lambda meta: meta["modified"])
    with open(dest / "index.json", "w") as f:
        json.dump(recipes, f, indent=4)

def main():
    logger = logging.getLogger(__name__)
    parser = ArgumentParser(description="Build a recipe website from a repository of markdown recipes")
    parser.add_argument("-s", "--source", help="The source directory containing markdown files", required=True)
    parser.add_argument("-d", "--destination", help="The destination directory for the output", required=True)

    args = parser.parse_args()
    source_dir = Path(args.source)
    if not source_dir.is_dir():
        logger.error("Source directory is not a directory!")
        return 1
    dest_dir = Path(args.destination)
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True)
    if not dest_dir.is_dir():
        logger.error("Destination directory is not a directory!")
        return 1

    build(source_dir, dest_dir)

if __name__ == '__main__':
    exit(main())
