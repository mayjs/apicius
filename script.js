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

/* Slideshow logic strongly inspired from https://www.w3schools.com/howto/howto_js_slideshow.asp */
var slideIndex = null;
function slideshowShow(img_idx, slideshow_idx) {
  slideshows = document.getElementsByClassName("slideshow-container");

  selectedSlideshow = slideshows[slideshow_idx];
  images = selectedSlideshow.getElementsByClassName("slideshow-card");
  if(img_idx > images.length) {
    slideIndex[slideshow_idx] = 1;
  } else if(img_idx < 1) {
    slideIndex[slideshow_idx] = images.length;
  } else {
    slideIndex[slideshow_idx] = img_idx;
  }
  for(let i = 0; i < images.length; i++) {
    images[i].style.display = "none";
  }
  images[slideIndex[slideshow_idx]-1].style.display = "block";

  dots = document.getElementsByClassName("slideshow-dots")[slideshow_idx].getElementsByClassName("slideshow-dot");
  for (let i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" slideshow-dot-active", "");
  }
  dots[slideIndex[slideshow_idx]-1].className += " slideshow-dot-active";
}

function slideshowInit() {
  slideshows = document.getElementsByClassName("slideshow-container").length;
  slideIndex = new Array(slideshows).fill(1);

  for(let si = 0; si < slideshows; si++) {
    console.log(si + " from " + slideshows);
    slideshowShow(1, si);
  }
}

function slideshowJump(jump, slideshow) {
  slideshowShow(slideIndex[slideshow] + jump, slideshow);
}

window.onload = function() {
  slideshowInit();
}
