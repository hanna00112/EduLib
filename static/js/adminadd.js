document.querySelector(".submit-btn").addEventListener("click", () => {
    const title = document.getElementById("book-title").value.trim();
    const author = document.getElementById("author-name").value.trim();
    const description = document.getElementById("description").value.trim();
    const location = document.getElementById("location").value.trim();
    const status = document.getElementById("copy-status").value;
  
    if (title && author && description && location) {
      alert(`Book "${title}" by ${author} added successfully!`);
      // Clear form fields
      document.getElementById("book-title").value = "";
      document.getElementById("author-name").value = "";
      document.getElementById("description").value = "";
      document.getElementById("location").value = "";
      document.getElementById("copy-status").value = "available";
    } else {
      alert("Please fill in all the fields!");
    }
  });
  