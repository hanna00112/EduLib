//Fake User Data
const validUser = {
    student: {
        email: "student@aui.ma",
        password: "student123",
    },
    faculty: {
        email: "faculty@aui.ma",
        password: "faculty123",
    },
    admin: {
        email: "admin@aui.ma",
        password: "admin123",
    },
};
// class=.login-form
document.querySelector(".login-form").addEventListener("submit", function(event) {
    event.preventDefault(); //preventing form from refreshing the page

    // getting form values 
    const userType = document.getElementById("userType").value; //retrieves value from
    const email = document.getElementById("username").value.trim(); // trims down white space
    const password = document.getElementById("password").value.trim();

    // checking all fields filled
    if (!email || !password) {
        alert("Please fill in all fields!");
        return
    }

    //making sure user info is correct 
    // validUser: object to simulate student, faculty & admin login. Array at the top of page
    if (
        validUser[userType] &&
        validUser[userType].email === email &&
        validUser[userType].password === password
    ) {
        alert(`Welcome ${userType.charAt(0).toUpperCase() + userType.slice(1)}!`)
            // directing the use based on usertype
        if (userType === "student") {
            window.location.href = "student/student-home.html";
        } else if (userType == "admin") {
            window.location.href = "admin/admin-home.html";
        }
    } else {
        // if login is incorrect direct to an alert
        alert("Invalid login. Please try again");
    }
});