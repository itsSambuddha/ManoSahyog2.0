// Common JavaScript functions for the website

// Function to handle navigation menu toggle (if needed)
function toggleMenu(menuId) {
  const menu = document.getElementById(menuId);
  if (menu) {
    menu.classList.toggle('hidden');
  }
}

// Utility to get query parameters from URL
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

// Function to navigate to a page with optional query parameters
function navigateTo(page, params = {}) {
  let url = page;
  const query = new URLSearchParams(params).toString();
  if (query) {
    url += '?' + query;
  }
  window.location.href = url;
}

// Add more common JS utilities as needed
