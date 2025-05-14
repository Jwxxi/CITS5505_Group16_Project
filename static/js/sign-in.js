<<<<<<< HEAD
document.addEventListener("DOMContentLoaded", () => {
  const signinForm = document.getElementById("signinForm");

  if (signinForm) {
    signinForm.addEventListener("submit", (event) => {
      event.preventDefault(); // Prevent default form submission

      // Clear previous validation state
      signinForm.classList.remove("was-validated");

      // Check form validity
      if (!signinForm.checkValidity()) {
        signinForm.classList.add("was-validated");
        return;
      }

      // Send data to the server
      fetch("/sign-in", {
        method: "POST",
        body: new FormData(signinForm),
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
          // Redirect to transactions page on success
          window.location.href = "/transactions";
        })
        .catch((error) => {
          alert(error.message); // Show error message
        });
    });
  }
});
=======
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("signinForm");
  
    if (form) {
      form.addEventListener("submit", function (event) {
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
  
>>>>>>> main
