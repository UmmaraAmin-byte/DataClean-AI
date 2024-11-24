import React, { useEffect, useState } from "react";

const App = () => {
  const [users, setUsers] = useState([]); // State to store users
  const [error, setError] = useState(null); // State to handle errors

  useEffect(() => {
    // Fetch users from the backend
    fetch("http://127.0.0.1:5000/api/users") // Ensure this matches your backend URL
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        setUsers(data.users); // Set users in state
      })
      .catch((err) => {
        setError(err.message); // Handle fetch errors
      });
  }, []);

  return (
    <div>
      <h1>Welcome to DataClean AI</h1>
      <h2>User List</h2>
      {error ? (
        <p style={{ color: "red" }}>Error: {error}</p>
      ) : (
        <ul>
          {users.map((user, index) => (
            <li key={index}>
              {user.name} - {user.email}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default App;
