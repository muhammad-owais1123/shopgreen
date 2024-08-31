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



});
