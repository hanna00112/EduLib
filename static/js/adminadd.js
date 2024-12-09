document.querySelector(".submit-btn").addEventListener("click", (event) => {
  event.preventDefault(); // Prevent form submission

  const title = document.getElementById("book-title").value.trim();
  const author = document.getElementById("author-name").value.trim();
  const description = document.getElementById("description").value.trim();
  const isbn = document.getElementById("isbn").value.trim();
  const location = document.getElementById("location").value.trim();
  const status = document.getElementById("copy-status").value;

  // Get selected genres (checkboxes)
  const selectedGenres = [];
  document.querySelectorAll("input[name='genres']:checked").forEach(checkbox => {
      selectedGenres.push(checkbox.value);
  });

  // Check if all fields are filled
  if (title && author && description && isbn && location && selectedGenres.length > 0) {
      // Prepare the data to send
      const bookData = {
          title: title,
          author: author,
          description: description,
          isbn: isbn,
          location: location,
          status: status,
          genres: selectedGenres // Send the selected genre IDs
      };

      // Send the data to the backend using fetch
      fetch('/add-book', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(bookData) // Send the data as JSON
      })
      .then(response => response.json())
      .then(data => {
          if (data.message) {
              alert(data.message); // Show success message
              // Clear form fields
              document.getElementById("book-title").value = "";
              document.getElementById("author-name").value = "";
              document.getElementById("description").value = "";
              document.getElementById("isbn").value = "";
              document.getElementById("location").value = "";
              document.getElementById("copy-status").value = "available";
              // Uncheck all genre checkboxes
              document.querySelectorAll("input[name='genres']").forEach(checkbox => {
                  checkbox.checked = false;
              });
          } else if (data.error) {
              alert(data.error); // Show error message
          }
      })
      .catch(error => {
          console.error("Error during submission:", error);
          alert("An error occurred. Please try again.");
      });
  } else {
      alert("Please fill in all the fields and select at least one genre!");
  }
});
