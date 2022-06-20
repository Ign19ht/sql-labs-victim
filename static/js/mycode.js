var login = document.getElementById("loginButton");
var username_filed = document.getElementById("usernameField");
var password_filed = document.getElementById("passwordField");
var message = document.getElementById("message")

login.addEventListener("click", evt => {
    evt.preventDefault();
    if (username_filed.value.length == 0 || password_filed.value.length == 0) {
        return 0;
    }
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:8000/auth', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var body = 'username=' + encodeURIComponent(username_filed.value) +
        '&password=' + encodeURIComponent(password_filed.value);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            let response = xhr.response;
            if (response === "0") {
                message.textContent = "Wrong password"
            } else if (response === "1") {
                window.open("http://127.0.0.1:8000/","_self")
                alert("authentication complete")
            }
        }
    }
    xhr.send(body);
})



