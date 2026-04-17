function loginUser() {
  const formData = new FormData();
  formData.append("username", document.getElementById("username").value);
  formData.append("password", document.getElementById("password").value);

  fetch("http://localhost:8000/api/posts/token", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    console.log("TOKEN:", data.access_token);
    localStorage.setItem("token", data.access_token);
  })
  .catch(err => console.log(err));
}