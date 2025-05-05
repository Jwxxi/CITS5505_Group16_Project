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
