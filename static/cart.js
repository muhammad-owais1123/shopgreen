// Filename: script.js
document.addEventListener("DOMContentLoaded", function() {
  const buttons = document.querySelectorAll(".cart-button");

  buttons.forEach(button => {
      button.addEventListener("click", function() {
          alert("Item added to cart!");
      });
  });
});
