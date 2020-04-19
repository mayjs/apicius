from argparse import ArgumentParser
from pathlib import Path
import logging
import json
from recipe_parser import parse_and_render_recipe, html_template

def render_table_row(title, ingredients, tags, url):
    rendered_tags = '<ul class="tags-list">{}</ul>'.format(
        "\n".join(f'<li class="tag">{tag}</li>' for tag in tags)
    )
    template = f"""
        <tr class="recipe-row" data-tags="{" ".join(tags)}" data-title="{title}" data-ingredients="{" ".join(ingredients)}">
            <td><a href="{url}">{title}</a></td>
            <td>{rendered_tags}</td>
        </tr>
    """
    # <td>{", ".join(ingredients)}</td>
    return template

def build(source: Path, dest: Path):
    logger = logging.getLogger("build")
    recipes_path = "recipes"
    recipe_out = dest / recipes_path
    recipe_out.mkdir(exist_ok=True, parents=True)

    recipes = []
    table_rows = []
    for infile in source.iterdir():
        if infile.is_file():
            logger.info(f"Handling {infile}")
            html_filename = infile.stem + ".html"
            outfile = recipe_out / html_filename
            title, ingredients, tags, html = parse_and_render_recipe(infile.read_text(), js_path_prefix="../", css_path_prefix="../")
            ingredient_names = list(set(name.lower() for name,_ in ingredients.keys()))
            url = f"{recipes_path}/{html_filename}"
            meta = {"modified": infile.stat().st_mtime, "title": title, "ingredients": ingredient_names, "url": url}
            recipes.append(meta)
            table_rows.append(render_table_row(title, ingredient_names, tags, url))
            outfile.write_text(html)
    recipes = sorted(recipes, key=lambda meta: meta["modified"])
    with open(dest / "index.json", "w") as f:
        json.dump(recipes, f, indent=4)

    nl = "\n"
    body = f"""
        <h2>Rezept-Übersicht:</h2>
        <form class="search-form" onsubmit="search(); event.preventDefault();">
            <label for="search-input">Suche:</label>
            <input class="search-input" id="search-input" type="Suche" placeholder="Suche" oninput="searchTermChanged();" value="">
            <button class="search-submit" onclick="search();" type="button">
            Suchen
            </button>
        </form>
        <table>
        <tr>
            <th>Name</th>
            <th>Tags</th>
        </tr>
        {nl.join(table_rows)}
    </table>
    """
    html = html_template.format(body=body, css_path_prefix="", js_path_prefix="")
    (dest / "index.html").write_text(html)

def main():
    logging.basicConfig(level=logging.INFO)
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
