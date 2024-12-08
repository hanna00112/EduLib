from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set secret key for sessions
app.secret_key = os.urandom(24)  # You can replace this with a fixed key for production


app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'mydatabase.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

#initialise the database
db = SQLAlchemy(app)
#Define the book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    location = db.Column(db.String(100))
    copy_status = db.Column(db.String(20))

    def __repr__(self):
        return f'<Book {self.title}>'
#Route to my account info
@app.route('/myaccount')
def home():
    # Query the database for borrowed books data
    borrowed_books = Book.query.all()

    # Pass the books to the template
    return render_template('non-admin/account.html', books=borrowed_books)


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
        new_book = Book(
            title=title,
            author=author,
            description=description,
            location=location,
            copy_status=copy_status
        )
        db.session.add(new_book)
        db.session.commit()  # Save the book to the database
        
        # Flash success message and redirect to the add-book page
        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))
    
    # Render the form page
    return render_template('admin/admin-add.html')

# Entry point
if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5001)