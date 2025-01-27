import React, { useState, useEffect } from "react";

function App() {
  const [movie, setMovie] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState("");
  const [availableMovies, setAvailableMovies] = useState([]); // Holds all available movie names
  const [suggestions, setSuggestions] = useState([]); // Holds filtered suggestions

  // Fetch all available movies from the backend
  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch("http://localhost:5000/movies");
        const data = await response.json();
        setAvailableMovies(data.movies); // Set all movies in state
      } catch (err) {
        console.error("Error fetching available movies:", err);
      }
    };
    fetchMovies();
  }, []);

  // Handle search input changes and generate suggestions
  const handleInputChange = (e) => {
    const query = e.target.value;
    setMovie(query);
    if (query.length > 0) {
      const filtered = availableMovies.filter((m) =>
        m.toLowerCase().includes(query.toLowerCase()) // Match input with available movie names
      );
      setSuggestions(filtered.slice(0, 5)); // Limit suggestions to top 5
    } else {
      setSuggestions([]);
    }
  };

  // Handle the recommendation search
  const handleSearch = async () => {
    try {
      const response = await fetch("http://localhost:5000/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ movie }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error);
        setRecommendations([]);
        return;
      }

      const data = await response.json();
      setRecommendations(data.recommendations);
      setError("");
    } catch (err) {
      setError("An error occurred. Please try again.");
    }
  };

  return (
    <div className="min-h-screen">
      <h1 className="movie-title">ML Movie Recommendations</h1>
      <div className="input-container">
        <input
          type="text"
          value={movie}
          onChange={handleInputChange} // Use updated function
          placeholder="Enter a movie name"
          className="movie-input"
        />
        <button onClick={handleSearch} className="movie-button">
          Get Recommendations
        </button>
      </div>
      {/* Display autocomplete suggestions */}
      {suggestions.length > 0 && (
        <ul className="suggestion-list">
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              className="suggestion-item"
              onClick={() => {
                setMovie(suggestion); // Update input when clicked
                setSuggestions([]); // Clear suggestions
              }}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
      {/* Display error message */}
      {error && <p className="error-message">{error}</p>}
      {/* Display recommendations */}
      <ul className="recommendation-list">
        {recommendations.map((rec, index) => (
          <li key={index} className="recommendation-item">
            {rec}
          </li>
        ))}
      </ul>
      
      <div className="movie-list-container">
        <h2>All Movies</h2>
        <div className="scrollable-box">
          <ul className="movie-list">
            {availableMovies.map((movie, index) => (
              <li key={index} className="movie-item">
                {movie}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
