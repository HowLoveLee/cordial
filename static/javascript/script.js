function login() {
    const loginDiv = document.getElementById('login-form');
    const registerDiv = document.getElementById('register-form');
    const wrapper = document.getElementById('wrapper');

    wrapper.style.height = "500px"
    registerDiv.style.display = "none";
    loginDiv.style.display = "block";
}
function createAccount() {
    const loginDiv = document.getElementById('login-form');
    const registerDiv = document.getElementById('register-form');
    const wrapper = document.getElementById('wrapper');

    wrapper.style.height = "650px";
    registerDiv.style.display = "block";
    loginDiv.style.display = "none";
}

/* password validator */
function matchingPass() {
    const repeatPass = document.getElementById('r-password2');

    if (repeatPass.value != document.getElementById('r-password').value) {
        repeatPass.setCustomValidity('Password does not match');
    } else {
        repeatPass.setCustomValidity('');
    }
}

document.getElementById('studentID').innerHTML = document.getElementById('studentPassword').value;