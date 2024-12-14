# EduLib
Final Project for CSC3323:  digital library management system that makes it easier for students to access academic materials

All users are first directed to a Log in. After logging in as a Student or Admin member, they will have different ways to use the site. 



To run the chat bot you need to install https://www.nomic.ai/gpt4all, run this and then install llama 3

to run the program enter python app.py on the terminal

 #Folders
    instance folder keeps the database file
    static folder holds:
        the css folder (styles.css was the main file used for our pages design)
        js folder holds the javascript files for the bot and the pages that used it for more interactivity
        photos folder holds the pictures we used
    templates folder holds:
        admin folder for html files for the admin pages
        non admin folder for html files for the non admin pages
        signup html 
        index html for the login
    the app.py is where our backend logic is.

database models for sqlite:
    User, Book, BookGenre, Userrole,Role,Genre, Bookcheckouthistory (to keep track of the borrowed books)

    




