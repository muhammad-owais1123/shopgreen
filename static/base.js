document.addEventListener("DOMContentLoaded", function() {
    document.querySelector(".about").addEventListener("click", function(event) {
        event.preventDefault(); // Prevents the default action of the link
        document.querySelector("footer").scrollIntoView({ 
            behavior: 'smooth' 
        });
    });
});