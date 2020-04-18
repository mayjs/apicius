function scaleIngredients() {
    let multiplier = parseFloat(document.getElementById("multiplier-input").value);
    let ingredients = document.getElementsByClassName("ingredient-number");
    for (let i of ingredients) {
        defaultAmount = parseFloat(i.dataset.defaultAmount);
        i.innerHTML = defaultAmount * multiplier;
    }
}
