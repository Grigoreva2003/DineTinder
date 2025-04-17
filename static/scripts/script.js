document.addEventListener('DOMContentLoaded', function () {
    const favouriteBtn = document.querySelector('.filter-favourite');
    const interestedBtn = document.querySelector('.filter-interested');

    const searchInput = document.querySelector('.search-field .text-input');
    const searchButton = document.querySelector('.search-field .search-button');

    const cardsContainer = document.querySelector('.cards-row');

    let currentFilter = 'favourite';
    if (favouriteBtn == null && interestedBtn == null) {
        currentFilter = 'blacklist';
    }

    const placesPerPage = 8;
    let currentPage = 1;
    let isLoading = false;
    let allPlacesLoaded = false;

    function showFavourites() {
        favouriteBtn.classList.add('active');
        interestedBtn.classList.remove('active');
        currentFilter = 'favourite';

        currentPage = 1;
        allPlacesLoaded = false;

        if (searchInput.value.trim() === '') {
            loadFilteredPlaces();
        } else {
            performSearch();
        }
    }

    function showInterested() {
        interestedBtn.classList.add('active');
        favouriteBtn.classList.remove('active');
        currentFilter = 'interested';

        currentPage = 1;
        allPlacesLoaded = false;

        if (searchInput.value.trim() === '') {
            loadFilteredPlaces();
        } else {
            performSearch();
        }
    }

    function showBlacklist() {
        currentFilter = 'blacklist';

        currentPage = 1;
        allPlacesLoaded = false;

        if (searchInput.value.trim() === '') {
            loadFilteredPlaces();
        } else {
            performSearch();
        }
    }

    function loadFilteredPlaces() {
        if (isLoading) return;
        isLoading = true;

        // Prepare the URL for the AJAX request
        const url = `/api/places/?filter=${currentFilter}&page=${currentPage}&limit=${placesPerPage}`;

        // Make AJAX request
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Process the data
                if (currentPage === 1) {
                    // Replace all cards if it's the first page
                    cardsContainer.innerHTML = '';
                }

                // Append new cards
                appendPlaceCards(data.places);

                // Check if there are more pages
                if (data.has_more === false) {
                    allPlacesLoaded = true;
                }

                isLoading = false;
                showLoadingState(false);
            })
            .catch(error => {
                console.error('Error fetching places:', error);
                isLoading = false;
                showLoadingState(false);
            });
    }

    // Function to perform search with current filter
    function performSearch() {
        if (isLoading) return;

        const searchTerm = searchInput.value.trim();
        if (searchTerm === '') {
            loadFilteredPlaces();
            return;
        }

        isLoading = true;
        showLoadingState(true);

        // Reset pagination
        currentPage = 1;
        allPlacesLoaded = false;

        // Prepare the URL for the search request
        const url = `/api/search/?query=${encodeURIComponent(searchTerm.toLowerCase())}&page=${currentPage}&limit=${placesPerPage}`;

        // Make AJAX request
        fetch(url)
            .then(response => {
                console.log(response)
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear the container and add new results
                cardsContainer.innerHTML = '';


                // Append new cards
                appendPlaceCards(data.places);

                // Check if there are more pages
                if (data.has_more === false) {
                    allPlacesLoaded = true;
                }

                isLoading = false;
                showLoadingState(false);
            })
            .catch(error => {
                console.error('Error searching places:', error);
                isLoading = false;
                showLoadingState(false);
            });
    }

    // Function to load more places (next page)
    function loadMorePlaces() {
        if (isLoading || allPlacesLoaded) return;

        currentPage++;

        const searchTerm = searchInput.value.trim();
        if (searchTerm === '') {
            loadFilteredPlaces();
        } else {
            performSearch();
        }
    }

    // Function to append place cards to the container
    function appendPlaceCards(places) {
        // Create an array of promises for fetching favorite and blacklist status
        const fetchPromises = places.map(place => {
            return Promise.all([
                fetch(`/carousel/check-favorite/${place.id}/`).then(response => response.json()),
                fetch(`/carousel/check-blacklist/${place.id}/`).then(response => response.json())
            ]).then(([favoriteData, blacklistData]) => {
                return {
                    place: place,
                    isFavourite: favoriteData.is_favorite,
                    isBlacklist: blacklistData.is_blacklist
                };
            });
        });

        // Wait for all fetches to complete
        Promise.all(fetchPromises)
            .then(results => {
                results.forEach(result => {
                    const place = result.place;
                    const isFavourite = result.isFavourite;
                    const isBlacklist = result.isBlacklist;

                    // Create the place card element
                    const placeCard = document.createElement('div');
                    placeCard.className = 'place-card place-card-small';
                    placeCard.setAttribute('data-place-id', place.id);
                    placeCard.setAttribute('data-place-type', currentFilter);

                    // Create card content
                    placeCard.innerHTML = `
                    <div class="card-image">
                        <img src="${place.photo_link}" alt="${place.name}">
                    </div>
                    <div class="card-info">
                        <div class="place-name">${place.name}</div>
                        <div class="place-category">${place.category}</div>
                    </div>
                    <div class="card-footer">
                        <div class="heart-icon ${isFavourite === true ? 'active' : ''}"></div>
                        <div class="broken-heart-icon ${isBlacklist === true ? 'active' : ''}"></div>
                    </div>
                `;

                    // Add the card to the container
                    cardsContainer.appendChild(placeCard);
                });
                new PlaceCardInteractions();
            })
            .catch(error => {
                console.error('Error fetching place statuses:', error);
            });
    }

    // Function to show/hide loading state
    function showLoadingState(isLoading) {
        if (isLoading) {
            // You could add a loading spinner here
            const loadingElement = document.createElement('div');
            loadingElement.className = 'loading-spinner';
            loadingElement.innerHTML = 'Loading...';
            cardsContainer.appendChild(loadingElement);
        } else {
            // Remove loading spinner if it exists
            const loadingElement = document.querySelector('.loading-spinner');
            if (loadingElement) {
                loadingElement.remove();
            }
        }
    }

    function isScrolledToBottom() {
        const scrollPosition = window.innerHeight + window.scrollY;
        const bodyHeight = document.querySelector(".cards-table-container").offsetHeight;

        return (scrollPosition >= bodyHeight);
    }

    // Scroll event listener for infinite scrolling
    window.addEventListener('scroll', function () {
        if (isScrolledToBottom()) {
            loadMorePlaces();
        }
    });

    // Set up event listeners for the filter buttons
    if (currentFilter !== "blacklist") {
        favouriteBtn.addEventListener('click', showFavourites);
        interestedBtn.addEventListener('click', showInterested);
    } else {
        showBlacklist();
    }

    // Set up event listeners for search
    let searchTimeout;
    searchInput.addEventListener('input', function () {
        // Use debounce to prevent too many requests
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 500);
    });

    searchButton.addEventListener('click', performSearch);

    // Also trigger search on Enter key
    searchInput.addEventListener('keyup', function (event) {
        if (event.key === 'Enter') {
            clearTimeout(searchTimeout);
            performSearch();
        }
    });

    // Initialize with favourites showing by default
    showFavourites();
});