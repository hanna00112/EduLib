
// Selecting all the Removing buttons 
document.querySelectorAll('.remove-button').forEach(button => {
    button.addEventListener('click', function () {
        const bookCard = this.closest('.book-card') // finding the parent book card
        bookCard.remove(); //remove the book card from the DOM
        alert("Book has been removed sucessfully!");
    })
})