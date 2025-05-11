document.addEventListener("DOMContentLoaded", function () {
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
