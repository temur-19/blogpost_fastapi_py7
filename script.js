fetch("http://localhost:8000/api/posts/register", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    username,
    password,
    first_name,
    last_name
  })
})