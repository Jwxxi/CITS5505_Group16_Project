document.addEventListener("DOMContentLoaded", function () {
    // Animate input focus
    const inputs = document.querySelectorAll(".custom-input");
  
    inputs.forEach((input) => {
      input.addEventListener("focus", function () {
        this.parentElement.classList.add("input-focused");
      });
  
      input.addEventListener("blur", function () {
        if (!this.value) {
          this.parentElement.classList.remove("input-focused");
        }
      });
  
      // If value already filled (e.g., after back/forward nav)
      if (input.value) {
        input.parentElement.classList.add("input-focused");
      }
    });
  
    // Floating animation for background shapes
    const shapes = document.querySelectorAll(".shape");
  
    shapes.forEach((shape, index) => {
      const duration = 15 + index * 5;
      const delay = index * 2;
      shape.style.animation = `float ${duration}s ease-in-out ${delay}s infinite alternate`;
    });
  
    if (!document.getElementById("shape-animations")) {
      const styleSheet = document.createElement("style");
      styleSheet.id = "shape-animations";
      styleSheet.textContent = `
        @keyframes float {
          0% {
            transform: translate(0, 0) rotate(0deg);
          }
          50% {
            transform: translate(20px, 20px) rotate(5deg);
          }
          100% {
            transform: translate(-20px, -10px) rotate(-5deg);
          }
        }
      `;
      document.head.appendChild(styleSheet);
    }
  });
  