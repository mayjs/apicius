function scaleIngredients() {
    let multiplier = parseFloat(document.getElementById("multiplier-input").value);
    if(multiplier > 0) {
        let ingredients = document.getElementsByClassName("ingredient-number");
        for (let i of ingredients) {
            defaultAmount = parseFloat(i.dataset.defaultAmount);
            i.innerHTML = defaultAmount * multiplier;
        }
    }
}

function search() {
    let search_terms = document.getElementById("search-input").value.toLowerCase().split(" ");
    let rows = document.getElementsByClassName("recipe-row");

    const contains_any_word = (haystack) => search_terms.some((search_term) => haystack.includes(search_term));
    for (let row of rows) {
        let matched = [row.dataset.title.toLowerCase(),
                       row.dataset.ingredients.toLowerCase(),
                       row.dataset.tags.toLowerCase()].some(contains_any_word);
        if(matched) {
            row.classList.remove("search-hidden");
        } else {
            row.classList.add("search-hidden");
        }
    }
}
function searchTermChanged() {
    search();
}
