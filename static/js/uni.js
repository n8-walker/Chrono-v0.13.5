
document.addEventListener('DOMContentLoaded', function() {
  function checkScreenWidth() {
    var mainContent = document.getElementById('main-content');
    var blockMessage = document.getElementById('mobile-block-message');
    if (window.innerWidth < 768) { // You can set the width threshold as needed
      mainContent.style.display = 'none';
      blockMessage.style.display = 'block';
    } else {
      mainContent.style.display = 'block';
      blockMessage.style.display = 'none';
    }
  }

  // Check on initial load
  checkScreenWidth();

  // Check on window resize
  window.addEventListener('resize', checkScreenWidth);
});

