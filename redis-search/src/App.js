import React, { useState, useEffect } from 'react';
import './App.css';
import ResultList from './ResultList';
import ReactSlider from 'react-slider';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [sliderValue, setSliderValue] = useState(100)
  const [responseTime, setResponseTime] = useState('')
  const [responseLength, setResponseLength] = useState(0)
  const [checkboxes, setCheckboxes] = useState([
    { id: 1, option: "name", checked: true},
    { id: 2, option: "type", checked: false},
    { id: 3, option: "description", checked: false},
    { id: 4, option: "rarity", checked: false},
    { id: 5, option: "details_type", checked: false},
    { id: 6, option: "damage_type", checked: false}
  ]);

  // Function to fetch data from the server
  const fetchData = async (query) => {
    try {
      let searchFields = ''
      for (const field of checkboxes) {
        if (field.checked) {
          searchFields += (field.option + ',')
        }
      }
      searchFields = searchFields.slice(0,-1)
      let params = `?query=${query}&limit=${sliderValue}`
      if (searchFields !== '') {
        params += `&attributes=${searchFields}`
      }
      const response = await fetch(`http://127.0.0.1:8000/search` + params);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // console.log('Data:')
      // console.log(data)
      setResults(data.items);
      setResponseTime(data.metadata.time)
      setResponseLength(data.items.length)
    } catch (error) {
      console.error('Error fetching data:', error);
      setResults(null);
    }
  };

  // Trigger fetchData whenever the query changes
  useEffect(() => {
    if (query.trim() !== '') {
      fetchData(query.trim());
    } else {
      setResults(null); // Clear results if the query is empty
    }
  }, [query, checkboxes]);

  // Update query as user types
  const handleInputChange = (event) => {
    setQuery(event.target.value);
  };

  const handleCheckboxChange = (id) => {
    setCheckboxes(prevOptions =>
      prevOptions.map(option =>
        option.id === id ? { ...option, checked: !option.checked } : option
      )
    );
  };

  const createSearchFieldsOptions = (searchOption) => {
    return (
      checkboxes.map(field => (
        <label key={field.id}>
          <input
            type='checkbox'
            checked={field.checked}
            onChange={() => handleCheckboxChange(field.id)}
          />
          {field.option}
        </label>
    ))
    )
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>GW2 API Search</h1>

        {/* Search Bar */}
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          placeholder="Type to search..."
          className="search-input"
        />
          {/* Collapsible box for slider */}
          <details className="slider-container">
          <summary>Advanced Search Options</summary>
          <div className="slider-content">
            <p>Search Limit: {sliderValue} items</p>

        {/* Slider for limit */}
          <ReactSlider
          className="horizontal-slider"
          thumbClassName="example-thumb"
          trackClassName="example-track"
          onChange={(value) => setSliderValue(value)}
          defaultValue={sliderValue}
          min={1}
          max={5000}
          />
          </div>
          <p>Search fields:</p>
          <div className="checkbox-container">
          {createSearchFieldsOptions()}
          </div>
        </details>

        {/* Display Results */}
        {results ? (
          <div className="results">
            <h2>Results: {responseLength} items in {responseTime} seconds</h2>
            <ResultList items={results} />
          </div>
        ) : (
          <p>No results to display.</p>
        )}
      </header>
    </div>
  );
}

export default App;
