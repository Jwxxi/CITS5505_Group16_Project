document.addEventListener("DOMContentLoaded", function () {
  // Form elements
  const signupForm = document.getElementById("signupForm");
  const signInLink = document.getElementById("signInLink");

  /**
   * Form validation
   */
  if (signupForm) {
    signupForm.addEventListener("submit", function (event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        event.preventDefault();

        // Get form data
        const formData = new FormData(this);
        const userData = {
          name: formData.get("name"),
          email: formData.get("email"),
          password: formData.get("password"),
        };

        // Log the data
        console.log("User registration data:", userData);

        // Show success message
        alert("Registration successful! You can now sign in.");

        // Reset the form
        this.reset();
      }

      this.classList.add("was-validated");
    });
  }

  /**
   * Handle sign in link click
   */
  if (signInLink) {
    signInLink.addEventListener("click", function (e) {
      e.preventDefault();
      // navigate to the sign-in page
      alert("This would navigate to the Sign In page");
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
