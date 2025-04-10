class PlaceCardInteractions {
  constructor() {
    this.initializeCards();
  }

  initializeCards() {
    // Find all place cards on the page
    const cards = document.querySelectorAll('.place-card');

    cards.forEach(card => {
      const placeId = card.dataset.placeId;
      const heartIcon = card.querySelector('.heart-icon');
      const brokenHeartIcon = card.querySelector('.broken-heart-icon');

      // Set initial heart status
      this.checkFavoriteStatus(placeId, heartIcon);

      // Add event listeners
      if (heartIcon) {
        heartIcon.addEventListener('click', (e) => {
          e.stopPropagation();
          this.toggleFavorite(placeId, heartIcon);
        });
      }

      if (brokenHeartIcon) {
        brokenHeartIcon.addEventListener('click', (e) => {
          e.stopPropagation();
          this.blacklistPlace(placeId, card);
        });
      }

      // Add swipe functionality if needed
      this.addSwipeListeners(card, placeId);

      // Mark as shown immediately when the card is visible
      this.markAsShown(placeId);
    });
  }

  checkFavoriteStatus(placeId, heartIcon) {
    fetch(`/carousel/check-favorite/${placeId}/`)
      .then(response => response.json())
      .then(data => {
        if (data.is_favorite) {
          heartIcon.classList.add('active');
        }
      });
  }

  toggleFavorite(placeId, heartIcon) {
    fetch(`/carousel/favorite/${placeId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken'),
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        heartIcon.classList.toggle('active');
        const card = heartIcon.closest('.place-card');

        card.style.transition = 'opacity 0.4s ease';
        card.style.opacity = '0';

        setTimeout(() => card.remove(), 500);
        window.location.reload();
      } else if (data.error === 'Login required') {
        window.location.href = '/login/vk';
      }
    });
  }

  blacklistPlace(placeId, card) {
    fetch(`/carousel/blacklist/${placeId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken'),
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {

        card.style.transition = 'transform 0.5s ease-in, opacity 0.5s ease-in';
        card.style.transform = 'translateY(100vh)';
        card.style.opacity = '0';
        setTimeout(() => card.remove(), 500);
        window.location.reload();
      }
    });
  }

  markAsShown(placeId) {
    // Record that this place was shown to the user
    fetch(`/carousel/shown/${placeId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken'),
        'Content-Type': 'application/json'
      }
    });
  }

  addSwipeListeners(card, placeId) {
    let startX, startY, endX, endY;
    const threshold = 50;

    card.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    });

    card.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].clientX;
      endY = e.changedTouches[0].clientY;

      const deltaX = endX - startX;
      const deltaY = endY - startY;

      // Only register horizontal swipes where X movement > Y movement
      if (Math.abs(deltaX) > threshold && Math.abs(deltaX) > Math.abs(deltaY)) {
        if (deltaX > 0) {
          // Right swipe - interested
          this.markInterested(placeId, true, card);
        } else {
          // Left swipe - not interested
          this.markInterested(placeId, false, card);
        }
      }
    });

    // Mouse events for desktop testing
    let mouseDown = false;
    card.addEventListener('mousedown', (e) => {
      mouseDown = true;
      startX = e.clientX;
      startY = e.clientY;
    });

    document.addEventListener('mouseup', (e) => {
      if (mouseDown) {
        mouseDown = false;
        endX = e.clientX;
        endY = e.clientY;

        const deltaX = endX - startX;
        const deltaY = endY - startY;

        if (Math.abs(deltaX) > threshold && Math.abs(deltaX) > Math.abs(deltaY)) {
          if (deltaX > 0) {
            // Right swipe - interested
            this.markInterested(placeId, true, card);
          } else {
            // Left swipe - not interested
            this.markInterested(placeId, false, card);
          }
        }
      }
    });
  }

  markInterested(placeId, isInterested, card) {
    const endpoint = isInterested ? 'interested' : 'not-interested';

    fetch(`/carousel/${endpoint}/${placeId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken'),
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        card.classList.add(isInterested ? 'swiped-right' : 'swiped-left');
        setTimeout(() => card.remove(), 500);
        window.location.reload();
      }
    });
  }

  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
}


document.addEventListener('DOMContentLoaded', () => {
  new PlaceCardInteractions();
});