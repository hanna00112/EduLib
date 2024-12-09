document.querySelector(".login-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form from submitting the default way

    // Get form values
    const userType = document.getElementById("userType").value;
    const email = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    // Check if all fields are filled
    if (!email || !password || !userType) {
        alert("Please fill in all fields!");
        return;
    }

    // Create the request payload
    const loginData = {
        email: email,
        password: password,
        userType: userType, // "student", "faculty", "admin"
    };

    // Send data to backend using fetch
    fetch("/", {
        method: "POST", 
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(loginData),  // Send the data as JSON
    })
    .then(response => response.json()) // Parse the response as JSON
    .then(data => {
        if (data.error) {
            alert(data.error);  // If there's an error, display it
        } else {
            alert(data.message);  // Show success message
            window.location.href = data.redirect; // Redirect based on backend response
        }
    })
    .catch(error => {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again.");
    });
});
