function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const content = document.querySelector('.content');
  const fadeIns = document.querySelectorAll('.fade-in');

  if (sidebar.classList.contains('collapsed')) {
    sidebar.classList.remove('collapsed');
    content.classList.remove('collapsed');

    // Show the text after sidebar is fully expanded
    setTimeout(() => {
      fadeIns.forEach(span => span.classList.add('show-text'));
    }, 300); // Wait for the sidebar to fully expand
  } else {
    fadeIns.forEach(span => span.classList.remove('show-text')); // Hide text immediately
    sidebar.classList.add('collapsed');
    content.classList.add('collapsed');
  }
}

// Ensure the text is visible when the page first loads
window.onload = function () {
  const fadeIns = document.querySelectorAll('.fade-in');
  fadeIns.forEach(span => span.classList.add('show-text'));
};