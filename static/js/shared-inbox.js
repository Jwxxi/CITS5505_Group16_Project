// Toggle "View"/"Hide" text for shared inbox
document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll('.toggle-view-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const targetId = btn.getAttribute('data-bs-target');
      const target = document.querySelector(targetId);
      setTimeout(() => {
        if (target.classList.contains('show')) {
          btn.textContent = 'Hide';
        } else {
          btn.textContent = 'View';
        }
      }, 350); // Wait for collapse animation
    });
  });
});