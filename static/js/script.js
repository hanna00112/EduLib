
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
// Send the form data to Flask backend for login validation
const formData = new FormData();
formData.append("userType", userType);
formData.append("username", email);
formData.append("password", password);

fetch("/login", {
    method: "POST",
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Redirect based on the user type (Flask handled the logic)
        if (userType === "student") {
            window.location.href = "/student-home";  // Adjust path based on Flask routes
        } else if (userType === "admin") {
            window.location.href = "/admin-home";
        }
    } else {
        alert("Invalid login. Please try again.");
    }
})
.catch(error => {
    console.error("Error during login:", error);
    alert("An error occurred. Please try again.");
});
});