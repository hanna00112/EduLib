from flask import Flask, redirect, render_template, request, url_for, flash
from pymongo import MongoClient
import os

# Initialize Flask app
app = Flask(__name__)

# Set secret key for sessions
app.secret_key = os.urandom(24)  # You can replace this with a fixed key for production

# MongoDB connection
client = MongoClient('mongodb+srv://sT0PDURwIWyOaKhT:a1OwPIjYgUSNxKml@cluster0.nf7wc.mongodb.net/', tlsAllowInvalidCertificates=True)
db = client['edulife']  # Database name
collection = db['books']  # Collection name

# Function to serialize books and convert ObjectId to string
def serialize_books(book):
    book['_id'] = str(book['_id'])  # Convert ObjectId to string
    return book


@app.route('/aya')
def home():
    # Query the database for borrowed books data
    borrowed_books = collection.find()

    # Convert the data to a list of dictionaries
    books = list(borrowed_books)

    # Render the template and pass the books data
    return render_template('account.html', books=books)


@app.route('/nait')
def mohammed():
    return render_template('admin.html')


# Route to handle the form submission and add a book to the database
@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Get data from the form
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        location = request.form['location']
        copy_status = request.form['copy-status']
        
        # Insert into the MongoDB collection
        collection.insert_one({
            'title': title,
            'author': author,
            'description': description,
            'location': location,
            'copy_status': copy_status
        })
        
        # Flash success message and redirect to the add-book page
        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))  # Corrected the route name to 'add_book'
    
    # Render the form page
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
