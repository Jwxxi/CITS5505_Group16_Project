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
        event.preventDefault(); // Prevent actual form submission for demo

        // Get form data
        const formData = new FormData(this);
        const userData = {
          name: formData.get("name"),
          email: formData.get("email"),
          password: formData.get("password"),
        };

        // Log the data (in a real app, you would send this to a server)
        console.log("User registration data:", userData);

        // Show success message
        alert("Registration successful! You can now sign in.");

        // Reset the form
        this.reset();
      }

      this.classList.add("was-validated");
    });
  }
});
