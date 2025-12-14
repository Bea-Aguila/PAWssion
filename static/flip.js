document.addEventListener('DOMContentLoaded', () => {
    const pages = document.querySelectorAll('.page');
    const bookWrapper = document.querySelector('.book-wrapper');
    const leftZone = document.querySelector('.left-zone');
    const rightZone = document.querySelector('.right-zone');
    const searchInput = document.querySelector('#breedSearch');
    const flipSound = document.getElementById('flipSound');

    function playFlipSound() {
        if (flipSound) {
            flipSound.currentTime = 0;
            flipSound.play();
        }
    }

    let currentPageIndex = 0;
    const totalPages = pages.length;

    function updateZIndex() {
        pages.forEach((page, index) => {
            page.style.zIndex = index >= currentPageIndex ? totalPages - index : index + 1;
        });
    }

    function updateClickZones() {
        leftZone.style.display = currentPageIndex === 0 ? 'none' : 'block';
        rightZone.style.display = currentPageIndex >= totalPages - 1 ? 'none' : 'block';
    }

    // Navigation, skip filtered pages (animals only)
    window.navigateBook = function(direction) {
        let nextIndex = currentPageIndex;
        let oldPageIndex = currentPageIndex; // Store the index before the change

        if (direction === 'next') {
            do { nextIndex++; } 
            while(nextIndex < totalPages && pages[nextIndex].classList.contains('filtered'));

            if (nextIndex < totalPages) {
                playFlipSound();
                
                // 1. Give the page a high z-index immediately before flipping
                pages[oldPageIndex].style.zIndex = totalPages + 1; 
                pages[oldPageIndex].classList.add('flipped');
                
                currentPageIndex = nextIndex;
                
                // 2. Schedule the z-index reset *after* the 600ms transition
                setTimeout(updateZIndex, 650); // Wait 650ms (0.6s transition + buffer)
            }
        } else if (direction === 'prev') {
            do { nextIndex--; } 
            while(nextIndex >= 0 && pages[nextIndex].classList.contains('filtered'));

            if (nextIndex >= 0) {
                playFlipSound();
                
                currentPageIndex = nextIndex;
                
                // 1. Remove flipped class and give it a high z-index (for un-flipping)
                pages[nextIndex].style.zIndex = totalPages + 1;
                pages[nextIndex].classList.remove('flipped');
                
                // 2. Schedule the z-index reset *after* the 600ms transition
                setTimeout(updateZIndex, 650); // Wait 650ms (0.6s transition + buffer)
            }
        }

        if (bookWrapper) bookWrapper.classList.toggle('is-open', currentPageIndex > 0);
        // REMOVED: updateZIndex() call here. It is now handled by setTimeout.
        updateClickZones();
    };

    // Search Functionality
    searchInput.addEventListener('input', () => {
    const term = searchInput.value.toLowerCase().trim();
    const animalPages = Array.from(pages).slice(2); // skip cover & welcome page

    // Reset all pages
    pages.forEach(p => {
        p.classList.remove('filtered');
        p.style.display = 'block';
    });

    // Apply filtering when search is NOT empty
    if (term !== "") {
        animalPages.forEach(p => {
            const breed = p.dataset.breed || "";
            if (!breed.includes(term)) {
                p.classList.add('filtered');
                p.style.display = 'none';
            }
        });
    }

    // Rebuild visible pages list for correct flipping
    const visiblePages = Array.from(pages).filter(p => p.style.display !== 'none');

    // Reset page states
    pages.forEach(p => p.classList.remove('flipped'));

    currentPageIndex = 0;

    // Reassign z-index based only on visible pages
    visiblePages.forEach((page, i) => {
        page.style.zIndex = visiblePages.length - i;
    });

    // Update open/close state
    if (bookWrapper) bookWrapper.classList.remove('is-open');

    // Update click zones
    updateClickZones();
});


    // Initial Setup
    updateZIndex();
    updateClickZones();
});

