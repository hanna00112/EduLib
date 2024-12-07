from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set secret key for sessions
app.secret_key = os.urandom(24)  # You can replace this with a fixed key for production

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edulife.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
# MongoDB connection
#client = MongoClient('mongodb+srv://sT0PDURwIWyOaKhT:a1OwPIjYgUSNxKml@cluster0.nf7wc.mongodb.net/', tlsAllowInvalidCertificates=True)
#db = client['edulife']  # Database name
#collection = db['books']  # Collection name

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    copy_status = db.Column(db.String(50))

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'admin'
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

# Define the BookCheckoutHistory model
class BookCheckoutHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    late_fine = db.Column(db.Integer, nullable=False)
    # Relationships
    book = db.relationship('Book', backref='checkouts')
    user = db.relationship('User', backref='checkouts')


# Function to serialize books and convert ObjectId to string
def serialize_books(book):
    book['_id'] = str(book['_id'])  # Convert ObjectId to string
    return book


@app.route('/myaccount')
def home():
      # Query the database for borrowed books data
    books = Book.query.all()
    return render_template('non-admin/account.html', books=books)


@app.route('/nait')
def mohammed():
    return render_template('admin/admin-add.html')


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
        
        # Insert into the SQLite database
        new_book = Book(title=title, author=author, description=description, location=location, copy_status=copy_status)
        db.session.add(new_book)
        db.session.commit()
        
        # Flash success message and redirect to the add-book page
        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))
    
    # Render the form page
    return render_template('admin/admin-add.html')
if __name__ == '__main__':
    app.run(debug=True, port=5001)
