// JavaScript for the EduLife Page

// Sample data for books (replace with dynamic data if needed)
const books = [
    {
      title: "Example Book 1",
      author: "Author Name",
      dueDate: "2024-12-01",
      status: "Overdue"
    },
    {
      title: "Example Book 2",
      author: "Author Name",
      dueDate: "2024-12-15",
      status: "Not Due Yet"
    }
  ];
  
  // Render the book list dynamically
  function renderBooks(bookList) {
    const bookContainer = document.querySelector(".borrowed-books");
    bookContainer.innerHTML = `<h2>List of Borrowed Books</h2>`;
    
    bookList.forEach(book => {
      const bookCard = document.createElement("div");
      bookCard.classList.add("book-card");
  
      bookCard.innerHTML = `
        <img src="book-placeholder.png" alt="Book Image" class="book-image">
        <div class="book-details">
          <p><strong>Title:</strong> ${book.title}</p>
          <p><strong>Author:</strong> ${book.author}</p>
          <p><strong>Due Date:</strong> ${book.dueDate}</p>
          <p><strong>Status:</strong> <span class="status ${book.status.toLowerCase().replace(" ", "-")}">${book.status}</span></p>
        </div>
        <button class="renew-btn">Renew</button>
      `;
  
      // Add event listener to the renew button
      bookCard.querySelector(".renew-btn").addEventListener("click", () => renewBook(book));
      bookContainer.appendChild(bookCard);
    });
  }
  
  // Search functionality
  const searchBar = document.querySelector(".search-bar");
  searchBar.addEventListener("input", (e) => {
    const searchValue = e.target.value.toLowerCase();
    const filteredBooks = books.filter(book =>
      book.title.toLowerCase().includes(searchValue) ||
      book.author.toLowerCase().includes(searchValue)
    );
    renderBooks(filteredBooks);
  });
  
  // Simulate renewing a book
  function renewBook(book) {
    alert(`Renewing "${book.title}"...`);
    
    // Update due date (add 15 days to current due date)
    const newDueDate = new Date(book.dueDate);
    newDueDate.setDate(newDueDate.getDate() + 15);
    book.dueDate = newDueDate.toISOString().split('T')[0];
    book.status = "Not Due Yet";
    
    renderBooks(books);
  }
  
  // Initial render of books
  renderBooks(books);
  