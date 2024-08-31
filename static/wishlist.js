// Filename: script.js
document.addEventListener("DOMContentLoaded", function() {
  const buttons = document.querySelectorAll(".cart-button");

  buttons.forEach(button => {
      button.addEventListener("click", function() {
          alert("Item added to cart!");
      });
  });
    const urlParams = new URLSearchParams(window.location.search);
    const selectedColor = urlParams.get('color');
    const selectedGloss = urlParams.get('gloss');
    const selectedDrainage = urlParams.get('drainage');
  console.log(selectedColor);
  console.log(selectedGloss);
  console.log(selectedDrainage);
});
