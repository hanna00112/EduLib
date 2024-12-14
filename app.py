import sqlite3
from flask import Flask, redirect, render_template, request, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os, re
from datetime import datetime



# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set secret key for sessions
app.secret_key = os.urandom(24)  
bcrypt = Bcrypt(app)



# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edulife.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask Migrate
migrate = Migrate(app, db)

# Define the Book model
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    isbn = db.Column(db.String(13), nullable=False)
    location = db.Column(db.String(255))
    copy_status = db.Column(db.String(50))
    borrowed_by = db.Column(
    db.Integer,
    db.ForeignKey('user.id', name='fk_book_borrowed_by'),
    nullable=True
    )
    
    returned = db.Column(db.Boolean, default=False)
    

    borrowed_user = db.relationship('User', backref='borrowed_books', foreign_keys=[borrowed_by])

    genres = db.relationship('Genre', secondary='book_genre', back_populates='books')
    

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Many-to-many relationship with Book 
    books = db.relationship('Book', secondary='book_genre', back_populates='genres')

class BookGenre(db.Model):
    __tablename__ = 'book_genre'
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), primary_key=True)

# Define the User model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Many-to-many relationship with Role
    roles = db.relationship('Role', secondary='user_role', back_populates='users')
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

# Define the Role model
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Many-to-many relationship with User
    users = db.relationship('User', secondary='user_role', back_populates='roles')

# Define UserRole model for many-to-many relationship
class UserRole(db.Model):
    __tablename__ = 'user_role'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)

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

# Migration set up
with app.app_context():
    db.create_all()

# Function to serialize books and convert ObjectId to string
def serialize_books(book):
    book['_id'] = str(book['_id'])  # Convert ObjectId to string
    return book


def get_book_by_id(book_id):
    book = Book.query.get(book_id)  # Fetch the book by ID
    
    if book:
        genres = [genre.name for genre in book.genres]  # Extract genre names from the relationship

        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "location": book.location,
            "copy_status": book.copy_status,
            "genres": genres,
        }

    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            # Handle submission from user
            if request.is_json:
                data = request.json
                email = data.get('email')
                password = data.get('password')
                user_type = data.get('userType')
            else:
                email = request.form.get('email')
                password = request.form.get('password')
                user_type = request.form.get('userType')

            # Validate 
            if not email or not password or not user_type:
                return jsonify({"error": "Please fill in all fields"}), 400

            # Validate user type
            if user_type == "admin":
                user_roles = ['admin']
            elif user_type == "non-admin":
                user_roles = ['faculty', 'student']
            else:
                return jsonify({"error": "Invalid user type"}), 400
            
            # Query the user by email
            user = User.query.filter_by(email=email).first()

            # Check user credentials
            if user and user.check_password(password):
                # Ensure the user has the correct role
                if user_type == "admin" and any(role.name == "admin" for role in user.roles):
                    session['user_id'] = user.id
                    session['user_role'] = 'admin'
                    return jsonify({"message": "Welcome Admin!", "redirect": url_for('Admin_home')}), 200
                elif user_type == "non-admin" and any(role.name in user_roles for role in user.roles):
                    session['user_id'] = user.id
                    session['user_role'] = 'non-admin'
                    return jsonify({"message": f"Welcome {user_type}!", "redirect": url_for('home')}), 200
                else:
                    return jsonify({"error": f"User does not have the {user_type} role"}), 403

            else:
                return jsonify({"error": "Invalid login credentials"}), 401
        
            # If GET request, render the login page
        return render_template('index.html')

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/myaccount')
def home():
    books = Book.query.all()
    return render_template('non-admin/student-home.html', books=books)


@app.route('/admin/add-book', methods=['GET', 'POST'])
def add_book():
    genres = Genre.query.all() 

    if request.method == 'POST':
        # Get form data
        selected_genres_ids = request.form.getlist('genres')
        # Fetch the genre objects based on the selected ids
        selected_genres = Genre.query.filter(Genre.id.in_(selected_genres_ids)).all()

        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        description = request.form.get('description')
        location = request.form.get('location')
        copy_status = request.form.get('copy_status')

        # Validate form inputs
        if not title or not author or not isbn:
            flash("Title, Author, and ISBN are required.", "danger")
            return redirect(url_for('add_book'))

        # Add the book to the database
        new_book = Book(
            title=title,
            author=author,
            isbn=isbn,
            description=description,
            location=location,
            copy_status=copy_status,
            genres=selected_genres  # directly assign the selected genres
        )

        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for('Admin_home'))
    
    return render_template('admin/admin-add.html', genres=genres)


# to access the admin home page
@app.route('/admin/home', methods=['GET','POST'])
def Admin_home():
    query = request.args.get('search', '')
    if query:
        books = search_books(query)  # Call the search_books function
    else:
        books = Book.query.all()  # If no search query, show all books
    return render_template('admin/admin-home.html', books=books, query=query)


# INDEX Page -- login
@app.route('/index')
def main():
    return render_template('index.html')

@app.route('/api/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()  
    return jsonify([role.name for role in roles])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
          # Handle submission from user
        if request.is_json:
            data = request.json
            # Get form data
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password = data.get('password')
            roles = data.get('roles', [])
        else:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            roles = request.form.getlist('roles')
        # Normalize roles to a list
        if isinstance(roles, str):  # If it's a single role wrap it in a list
            roles = [roles]

        print("Received data:", roles)
        # Validate input
        if not first_name or not last_name or not email or not password or not roles:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('register'))

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({"error": "Invalid email format"}), 400
        
        #valid role combinations
        valid_combinations = [
            {"admin"},                    # Admin alone
            {"admin", "faculty"},         # Admin and Faculty
            {"faculty"},                  # Faculty alone
            {"student"},                  # Student alone
            {"student", "admin"}          # Student and Admin
        ]

        # Convert user input into a set for easy comparison
        user_roles_set = set(roles)

        # Check if the provided roles match one of the valid combinations
        
        if user_roles_set not in valid_combinations:
           flash('Invalid role combination', 'error')
           return redirect(url_for('register'))
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        # Create new user and hash the password
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email

        )
        new_user.set_password(password)  # Hash the password

         # Add roles to the user
        db_roles = Role.query.filter(Role.name.in_(roles)).all()
        for role in db_roles:
            new_user.roles.append(role)
        

        # Add to the database
        db.session.add(new_user)
        print("Committing to the database...")
        db.session.commit()
        print("Commit successful.")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # If GET request, render the registration form
    return render_template('signup.html')

@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to be logged in to borrow a book.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    book = Book.query.get(book_id)

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('home'))

    # Check if the book is already borrowed
    if book.borrowed_by:
        flash(f"The book '{book.title}' is already borrowed.", "danger")
        return redirect(url_for('home'))

    # Borrow the book by updating the `borrowed_by` field in the `Book` model
    book.borrowed_by = user.id
    db.session.commit()

    # Create an entry in `BookCheckoutHistory` to record the borrowing
    checkout_history = BookCheckoutHistory(
        book_id=book.id,
        user_id=user.id,
        checkout_date=datetime.utcnow(),
        late_fine=0  # Set late fine to 0 initially
    )
    db.session.add(checkout_history)
    db.session.commit()

    flash(f"You have successfully borrowed '{book.title}'.", "success")
    return redirect(url_for('home'))

@app.route('/return_book/<int:book_id>', methods=['POST'])
def return_book(book_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to be logged in to return a book.", "danger")
        return redirect(url_for('login'))

    book = Book.query.get(book_id)
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('my_borrowed_books'))

    if book.borrowed_by != user_id:
        flash("You cannot return a book you haven't borrowed.", "danger")
        return redirect(url_for('my_borrowed_books'))

    # Update the book's borrowed_by field and returned flag
    book.borrowed_by = None
    book.returned = True
    db.session.commit()

    # Update the BookCheckoutHistory entry with the return date
    checkout_history = BookCheckoutHistory.query.filter_by(book_id=book.id, user_id=user_id, return_date=None).first()
    if checkout_history:
        checkout_history.return_date = datetime.utcnow()
        db.session.commit()

    flash(f"You have successfully returned '{book.title}'.", "success")
    return redirect(url_for('my_borrowed_books'))


@app.route('/remove_book/<int:book_id>', methods=['POST'])
def remove_book(book_id):
    # Logic to remove the book using book_id
    # Example:
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('Admin_home'))

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get(book_id)  # Get the book object
    if not book:
        return "Book not found", 404

    # Fetch all available genres from the database
    genres = Genre.query.all()

    # Get the IDs of the genres associated with the book for pre-selection
    book_genres = [genre.id for genre in book.genres]

    if request.method == 'POST':
        # Update the book data from the form
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        book.description = request.form['description']
        book.location = request.form['location']
        book.copy_status = request.form['copy_status']

        # Get selected genres from the form
        selected_genres = request.form.getlist('genres')

        # Update genres for the book (clear existing and add selected genres)
        book.genres.clear()  # This clears the existing relationships

        # Append new genres based on the selected ones
        for genre_id in selected_genres:
            genre = Genre.query.get(genre_id)
            if genre:
                book.genres.append(genre)

        db.session.commit()  # Commit changes to the database
        flash("Book details updated successfully.", "success")
        return redirect(url_for('Admin_home'))  # Redirect to the admin home

    # Return the template with the necessary data
    return render_template('admin/admin-edit.html', book=book, genres=genres, book_genres=book_genres)

@app.route('/my-borrowed-books', methods=['GET'])
def my_borrowed_books():
    if 'user_id' not in session:
        # User is not logged in
        flash("Please log in to view your borrowed books.", "danger")
        return redirect(url_for('login'))

    try:
        # Get the logged-in user's ID from the session
        user_id = session['user_id']

        # Query borrowed books and their checkout history
        borrowed_books = (
            db.session.query(Book, BookCheckoutHistory)
            .join(BookCheckoutHistory, Book.id == BookCheckoutHistory.book_id)
            .filter(BookCheckoutHistory.user_id == user_id)  # Filter based on user_id in BookCheckoutHistory
            .order_by(BookCheckoutHistory.checkout_date.desc())
            .all()
        )

        # Render the borrowed books page and pass the books data to the template
        return render_template('non-admin/student-history.html', borrowed_books=borrowed_books)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('home'))


#////////////////////////////////////////////////////////////////////////////////////
# For the bot in order to work, the hosting computet should gpt4all installed as well as one of llama 3 models :3
def search_books(query):
    """
    Search for books in the database based on title, author, or ISBN
    """
    try:
        query = query.lower()  # Convert query to lowercase for case-insensitive search
        
        books = Book.query.filter(
            db.or_(
                db.func.lower(Book.title).contains(query),
                db.func.lower(Book.author).contains(query),
                Book.isbn.contains(query)
            )
        ).all()

        # Format results
        results = []
        for book in books:
            results.append({
                'id': book.id,  # Add the 'id' attribute to each book's dictionary
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'status': book.copy_status,
                'location': book.location,
                'genres': [genre.name for genre in book.genres]  # Ensure genres are in list format
            })

        return results
    except Exception as e:
        return f"Error searching books: {str(e)}"

@app.route('/search', methods=['GET'])
def search_books_route():
    query = request.args.get('query', '')
    if query:
        results = search_books(query)  
    else:
        results = []

    return render_template('non-admin/student-home.html', books=results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
