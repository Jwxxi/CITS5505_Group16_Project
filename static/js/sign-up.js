document.addEventListener("DOMContentLoaded", function () {
<<<<<<< HEAD
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
=======
  const form = document.getElementById("signupForm");

  if (form) {
    form.addEventListener("submit", function (event) {
      const password = form.querySelector('input[name="password"]').value;
      const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;

      if (!passwordRegex.test(password)) {
        event.preventDefault();
        alert("Password must be at least 8 characters long and include letters and numbers.");
        return;
      }

      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }

      form.classList.add("was-validated");
    });
  }

  // Animate input fields
  const inputs = document.querySelectorAll(".custom-input");
  inputs.forEach((input) => {
    input.addEventListener("focus", () => {
      input.parentElement.classList.add("input-focused");
>>>>>>> main
    });

    input.addEventListener("blur", () => {
      if (!input.value) {
        input.parentElement.classList.remove("input-focused");
      }
    });

    if (input.value) {
      input.parentElement.classList.add("input-focused");
    }
  });

  // Animate background shapes
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
        0% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(20px, 20px) rotate(5deg); }
        100% { transform: translate(-20px, -10px) rotate(-5deg); }
      }
    `;
    document.head.appendChild(styleSheet);
  }
});
