document.addEventListener("DOMContentLoaded", function () {
  // Form elements
  const signupForm = document.getElementById("signupForm");
  const signInLink = document.getElementById("signInLink");
  const errorElement = document.getElementById("error-message");
  const successElement = document.getElementById("success-message");

  /**
   * Form validation and submission
   */
  if (signupForm) {
    signupForm.addEventListener("submit", function (event) {
      event.preventDefault();

      // Clear previous messages
      errorElement.style.display = "none";
      successElement.style.display = "none";

      // Get form data
      const formData = new FormData(this);

      // Send data to server
      fetch("/sign-up", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((data) => {
              throw new Error(data.error);
            });
          }
          return response.json();
        })
        .then((data) => {
          // Show success message
          successElement.textContent = data.success;
          successElement.style.display = "block";

          // Redirect to Sign-In page after 3 seconds
          setTimeout(() => {
            window.location.href = "/sign-in";
          }, 3000);
        })
        .catch((error) => {
          // Show error message
          errorElement.textContent = error.message;
          errorElement.style.display = "block";
        });
    });
  }

  

  /**
   * Add animation effects
   */
  const formInputs = document.querySelectorAll(".custom-input");

  formInputs.forEach((input) => {
    // Add focus effect
    input.addEventListener("focus", function () {
      this.parentElement.classList.add("input-focused");
    });

    // Remove focus effect
    input.addEventListener("blur", function () {
      if (!this.value) {
        this.parentElement.classList.remove("input-focused");
      }
    });

    // Check if input already has value on page load
    if (input.value) {
      input.parentElement.classList.add("input-focused");
    }
  });

  /**
   * Animate background shapes
   */
  const shapes = document.querySelectorAll(".shape");

  // Add subtle animation to shapes
  shapes.forEach((shape, index) => {
    // Set different animation for each shape
    const duration = 15 + index * 5;
    const delay = index * 2;

    shape.style.animation = `float ${duration}s ease-in-out ${delay}s infinite alternate`;
  });

  // Add keyframes for floating animation
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
