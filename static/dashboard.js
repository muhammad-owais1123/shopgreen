// Function to handle tab switching
function openTab(tabName) {
    // Hide all tab contents
    var tabContents = document.getElementsByClassName("tab-content");
    for (var i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = "none";
    }

    // Remove active class from all menu items
    var menuItems = document.querySelectorAll(".menu ul li");
    for (var i = 0; i < menuItems.length; i++) {
        menuItems[i].classList.remove("active");
    }

    // Show the selected tab content
    document.getElementById(tabName).style.display = "block";

    // Add active class to the clicked menu item
    var clickedMenuItem = document.querySelector(`.menu ul li a[onclick="openTab('${tabName}')"]`).parentNode;
    clickedMenuItem.classList.add("active");
}



// Set the default tab to be opened
document.addEventListener("DOMContentLoaded", function() {
    openTab('dashboard');

    // Add hover functionality to menu items
    var menuLinks = document.querySelectorAll('.menu ul li a');

    menuLinks.forEach(function(link) {
        link.addEventListener('mouseenter', function() {
            // Remove 'active' class from all menu items
            menuLinks.forEach(function(item) {
                item.parentNode.classList.remove('active');
            });

            // Add 'active' class to the hovered menu item
            this.parentNode.classList.add('active');
        });

        link.addEventListener('mouseleave', function() {
            // Remove 'active' class when the mouse leaves
            this.parentNode.classList.remove('active');
        });
    });
});
