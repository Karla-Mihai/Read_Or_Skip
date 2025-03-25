document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.querySelector('input[name="rating"]'); // Assuming your form has an input named "rating"

    // Handle the mouseover effect to show the rating
    stars.forEach(star => {
        star.addEventListener('mouseover', function() {
            const value = parseInt(star.getAttribute('data-value'));
            updateStars(value);
        });
        star.addEventListener('mouseout', function() {
            updateStars(ratingInput.value); // Update the stars based on the current rating value
        });

        // Handle click to set the rating
        star.addEventListener('click', function() {
            const value = parseInt(star.getAttribute('data-value'));
            ratingInput.value = value; // Update the hidden input value
            updateStars(value); // Fill stars based on the clicked rating
        });
    });

    // Function to update the stars
    function updateStars(rating) {
        stars.forEach(star => {
            const value = parseInt(star.getAttribute('data-value'));
            if (value <= rating) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });
    }
});
