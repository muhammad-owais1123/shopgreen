document.addEventListener("DOMContentLoaded", function() {
    const prodnameElement = document.getElementById("name");
    const prodname = prodnameElement.textContent;

    let selectedColor = null;
    let selectedGloss = null;
    let selectedDrainage = null;
    let selectedQuantity = null;

    const mainImage = document.getElementById('mainImage');
    const priceElement = document.getElementById('price');
    const quantityInput = document.getElementById('quantity');
    const wishlistButton = document.querySelector('.wishlist-btn');
    const cartButton = document.getElementById('add-to-cart-link');
    const glossOptions = document.getElementById('gloss-options');

    quantityInput.addEventListener('input', function() {
        selectedQuantity = quantityInput.value;
        console.log('Updated Quantity:', selectedQuantity);
    });

    function handleSelection(event, options, category) {
        options.forEach(option => option.classList.remove('selected'));
        event.target.classList.add('selected');
    
        const value = event.target.getAttribute('data-value');
    
        if (category === 'color') {
            selectedColor = value;
            console.log('Selected Color:', selectedColor);
            fetch(`/getGlossOptions/${encodeURIComponent(prodname)}?color=${encodeURIComponent(selectedColor)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.glossOptions && data.glossOptions.length > 0) {
                        updateGlossOptions(data.glossOptions);
                        // Automatically select the first gloss option if available
                        const defaultGloss = data.glossOptions[0];
                        handleSelection({ target: document.querySelector(`.gloss-option[data-value="${defaultGloss}"]`) }, document.querySelectorAll('.gloss-option'), 'gloss');
                    } else {
                        // Handle cases where no gloss options are available
                        updateGlossOptions([]);
                    }
                })
                .catch(error => {
                    console.error('Error fetching gloss options:', error);
                });
        } else if (category === 'gloss') {
            selectedGloss = value;
            console.log('Selected Gloss:', selectedGloss);
            fetch(`/getPrice/${encodeURIComponent(prodname)}?color=${encodeURIComponent(selectedColor)}&gloss=${encodeURIComponent(selectedGloss)}`)
            .then(response => response.json())
                .then(data => {
                    if (data.price) {
                        priceElement.textContent = `Rs. ${data.price}`; // Format price with currency symbol
                        console.log('Price updated to:', data.price);
                    } else {
                        console.error('Price not found in response', data);
                    }
                })
                .catch(error => {
                    console.error('Error fetching price:', error);
                });
        } else if (category === 'drainage') {
            selectedDrainage = value;
            console.log('Selected Drainage:', selectedDrainage);
        }
    
        const newImageSrc = event.target.getAttribute('data-image');
        if (newImageSrc) {
            mainImage.src = newImageSrc;
        }
    
        console.log('Current Selections:', {
            selectedColor,
            selectedGloss,
            selectedDrainage,
            selectedQuantity
        });
    }
    
    function updateGlossOptions(glossOptionsData) {
        const buttons = Array.from(glossOptions.querySelectorAll('.gloss-option'));
    
        buttons.forEach(button => {
            const glossValue = button.getAttribute('data-value');
            if (glossOptionsData.includes(glossValue)) {
                button.style.display = 'inline-block';
            } else {
                button.style.display = 'none';
            }
        });
    
        const isAnyButtonVisible = buttons.some(button => button.style.display === 'inline-block');
        glossOptions.style.display = isAnyButtonVisible ? 'block' : 'none';
    }

    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', event => handleSelection(event, document.querySelectorAll('.color-option'), 'color'));
    });

    document.querySelectorAll('.gloss-option').forEach(option => {
        option.addEventListener('click', event => handleSelection(event, document.querySelectorAll('.gloss-option'), 'gloss'));
    });

    document.querySelectorAll('.drainage-option').forEach(option => {
        option.addEventListener('click', event => handleSelection(event, document.querySelectorAll('.drainage-option'), 'drainage'));
    });

    wishlistButton.addEventListener('click', function(event) {
        event.preventDefault();
        if (!selectedColor || !selectedGloss || !selectedDrainage || !selectedQuantity) {
            alert('Please select all options before adding to wishlist.');
            return;
        }

        fetch('/addtowishlist/' + prodname, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'color': selectedColor,
                'gloss': selectedGloss,
                'drainage': selectedDrainage,
                'quantity': selectedQuantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Item successfully added to wishlist!');
                window.location.href = '/wishlistparam';
            } else {
                alert('Failed to add item to wishlist: ' + data.reason);
            }
        });
    });

    cartButton.addEventListener('click', function(event) {
        event.preventDefault();
        if (!selectedColor || !selectedGloss || !selectedDrainage || !selectedQuantity) {
            alert('Please select all options before adding to cart.');
            return;
        }

        fetch('/addtocart/' + prodname, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'color': selectedColor,
                'gloss': selectedGloss,
                'drainage': selectedDrainage,
                'quantity': selectedQuantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Item successfully added to cart!');
                window.location.href = '/cartpage';
            } else {
                alert('Failed to add item to cart: ' + data.reason);
            }
        });
    });

    document.querySelectorAll('.accordion').forEach(button => {
        button.addEventListener('click', () => {
            button.classList.toggle('active');
            const panel = button.nextElementSibling;
            panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
        });
    });
});
