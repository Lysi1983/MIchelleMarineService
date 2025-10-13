document.addEventListener('DOMContentLoaded', function() {
    // Get the current URL path
    const path = window.location.pathname;
    
    // Check if we're on the services page
    if (path.includes('/services') || path.includes('/yachtservice/services')) {
        document.body.classList.add('services-page');
    }
});