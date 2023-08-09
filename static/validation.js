function validateLoginForm() {
    const username_email = document.forms["loginForm"]["username_email"].value;
    const password = document.forms["loginForm"]["password"].value;

    // Check if any field is empty
    if (username_email === "" || password === "") {
        alert("Please fill in all the fields.");
        return false;
    }

    return true;
}

function validateSignupForm() {
    const email = document.forms["registerForm"]["email"].value;
    const username = document.forms["registerForm"]["username"].value;
    const password = document.forms["registerForm"]["password"].value;
    const confirmPassword = document.forms["registerForm"]["confirmPassword"].value;

    // Check if any field is empty
    if (email === "" || username === "" || password === "" || confirmPassword === "") {
        alert("Please fill in all the fields.");
        return false;
    }

    // Check if the passwords match
    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return false;
    }

    if (password.length < 8) {
        alert("Password must be at least 8 characters long.");
        return false;
    }

    return true;
}
