document.addEventListener("DOMContentLoaded", () => {
    const slidesContainer = document.querySelector(".slides");
    const cards = document.querySelectorAll(".card");
    let currentIndex = 0;
  
    function getVisibleItems() {
      return window.innerWidth <= 768 ? 3 : 4; // Number of visible items based on screen size
    }
  
    function updateSlideCount() {
      const visibleItems = getVisibleItems();
      const totalCards = cards.length;
      const slideCount = Math.ceil(totalCards / visibleItems);
  
      // Create slides dynamically if needed
      let slides = slidesContainer.querySelectorAll(".slide");
      if (slides.length !== slideCount) {
        slidesContainer.innerHTML = ''; // Clear existing slides
  
        for (let i = 0; i < slideCount; i++) {
          const slide = document.createElement("div");
          slide.classList.add("slide");
          slidesContainer.appendChild(slide);
  
          const start = i * visibleItems;
          const end = Math.min(start + visibleItems, totalCards);
  
          for (let j = start; j < end; j++) {
            slide.appendChild(cards[j].cloneNode(true)); // Append cloned card to slide
          }
        }
      }
  
      slides = slidesContainer.querySelectorAll(".slide");
      slidesContainer.style.width = `${slideCount * 100}%`;
      updateSlideWidth();
    }
  
    function updateSlideWidth() {
      const visibleItems = getVisibleItems();
      slidesContainer.querySelectorAll(".slide").forEach(slide => {
        slide.style.width = `${100 / slidesContainer.querySelectorAll(".slide").length}%`; // Each slide takes the correct width
      });
    }
  
    window.addEventListener("resize", updateSlideCount);
  
    updateSlideCount(); // Initial call
  
    setInterval(() => {
      const slideCount = slidesContainer.querySelectorAll(".slide").length;
      currentIndex = (currentIndex + 1) % slideCount;
      slidesContainer.style.transform = `translateX(${-currentIndex * 100 / slideCount}%)`;
    }, 2000);


//===========================SEARCH BAR=========================
const input = document.querySelector('input[type="text"]');
const searchWrapper = document.querySelector('.search-wrapper');

input.addEventListener('keyup', function() {
    const query = input.value;
    if (query.length > 2) { // Start searching after 3 characters
        fetch(`/suggestions/?term=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                // Handle displaying suggestions
                let suggestions = '';
                data.forEach(item => {
                    suggestions += `<div class="suggestion-item">${item.name}</div>`;
                });
                const suggestionsDiv = document.createElement('div');
                suggestionsDiv.classList.add('suggestions');
                suggestionsDiv.innerHTML = suggestions;
                searchWrapper.appendChild(suggestionsDiv);
            })
            .catch(error => console.error('Error fetching suggestions:', error));
    } else {
        removeSuggestions();  // Clear suggestions when query is too short
    }
});

// Hide suggestions when clicking outside the search box
document.addEventListener('click', function(e) {
    if (!searchWrapper.contains(e.target)) {
        removeSuggestions();
    }
});

function removeSuggestions() {
    const existingSuggestions = searchWrapper.querySelector('.suggestions');
    if (existingSuggestions) {
        searchWrapper.removeChild(existingSuggestions);
    }
}
function animate(element) {
  // Add the class to start the initial transition
  element.classList.add('animate-transform-background');

  // Set a timeout to apply the flip back and darkening effect after the initial transition
  setTimeout(() => {
    element.classList.add('flip-twice');
    
    // Set a timeout to darken the background color after the second flip
    setTimeout(() => {
      element.classList.add('darkening-background');
    }, 1000); // Delay for darkening should match the duration of the flip transition (1s in this case)
  }, 1000); // Delay for flip-back should match the duration of the initial transition (1s in this case)
}

function animate_(element) {
  // Add the class to start the initial transition
  element.classList.add('animate-transform-background_');

  // Set a timeout to apply the flip back and darkening effect after the initial transition
  setTimeout(() => {
    element.classList.add('flip-twice_');
    
    // Set a timeout to darken the background color after the second flip
    setTimeout(() => {
      element.classList.add('darkening-background');
    }, 1000); // Delay for darkening should match the duration of the flip transition (1s in this case)
  }, 1000); // Delay for flip-back should match the duration of the initial transition (1s in this case)
}

const allProductsButton = document.querySelector('.buttons .explore-btn');
const newestArrivalsButton = document.querySelector('.buttons .learn-more-btn');

animate(allProductsButton);
animate_(newestArrivalsButton);

  });
  