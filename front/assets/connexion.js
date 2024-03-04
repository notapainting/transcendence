
document.getElementById("loginForm").addEventListener("submit", function(event){
	event.preventDefault(); 
	
	var login = document.getElementById("login").value;
	var email = document.getElementById("email").value;
	var password = document.getElementById("password").value;
	
	var formData = {
		"username": login,
		"email": email,
		"password": password
	};
	
	var formDataJSON = JSON.stringify(formData);
	
	// console.log(formDataJSON); // test, a supprimer

	fetch('https://localhost:8443/api/signup/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: formDataJSON
        })
		.then(response => {
            if (!response.ok)
                throw new Error('Error : Bad Network response :(');
            return response.json();
        })
		.then(data => console.log(data))
		.catch(error => console.error(error));
});