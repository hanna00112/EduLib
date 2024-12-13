document.addEventListener("DOMContentLoaded", () => {
    // Fetch roles and create checkboxes dynamically
    fetch('/api/roles')
        .then(response => response.json())
        .then(roles => {
            const roleSelectionDiv = document.querySelector('.role-selection');
            roleSelectionDiv.innerHTML = ''; // Clear existing roles
            
            roles.forEach(role => {
                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.name = 'roles';
                checkbox.value = role;

                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(role));
                roleSelectionDiv.appendChild(label);
            });
        })
        .catch(error => console.error('Error fetching roles:', error));

    // Handle form submission
    const form = document.getElementById('register-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault(); // Prevent the default form submission

        // Collect form data
        const firstName = document.getElementById('first_name').value;
        const lastName = document.getElementById('last_name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Collect selected roles
        const roles = Array.from(document.querySelectorAll('input[name="roles"]:checked'))
            .map(checkbox => checkbox.value);

        // Create the payload object
        const data = {
            first_name: firstName,
            last_name: lastName,
            email: email,
            password: password,
            roles: roles
        };

        // Send the data via a POST request
        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Ensure the Content-Type is set correctly
            },
            body: JSON.stringify(data) // Convert the data to JSON
        })
        .then(response => response.json())
        .then(data => {
            console.log('Registration successful:', data);
            // Optionally redirect or show a success message
        })
        .catch(error => {
            console.error('Error during registration:', error);
        });
    });
});
