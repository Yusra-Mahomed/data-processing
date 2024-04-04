import React, { useState } from 'react';

function DataTypeOverrideComponent({ columnsWithTypes, onSubmitOverride }) {
  const [selectedColumn, setSelectedColumn] = useState('');
  const [newDataType, setNewDataType] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Define the valid data types as an array
  const validDataTypes = ['Date', 'Integer', 'Time Duration', 'Boolean', 'Complex Number', 'Category', 'Text', 'Decimal']

 
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); 
    setSuccess(''); 
    if (!selectedColumn || !newDataType) {
      setError('Please select a column and enter a new data type.');
      return;
    }
  
    try {
      const response = await fetch('https://data-processing-backend.onrender.com/data/override/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ column: selectedColumn, new_type: newDataType }),
      });
  
      const data = await response.json();
      if (response.ok) {
        setSuccess(data.message || 'Data type overridden successfully.'); // Set success message
        onSubmitOverride(data);
      } else {
        setError(data.error || 'An error occurred.');
      }
    } catch (error) {
      setError('Error making the request: ' + error.message);
    }
  
    setSelectedColumn('');
    setNewDataType('');
  };

   
  return (
    <div>
      <h3>Override Column Data Types</h3>
      {success && <div className="success-message">{success}</div>}
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <label>
          Select Column: {}
          <select value={selectedColumn} onChange={e => setSelectedColumn(e.target.value)}>
            <option value="">Select Column</option>
            {columnsWithTypes.map((item, index) => (
              <option key={index} value={item.column}>{item.column}</option>
            ))}
          </select>
        </label>
        <label>
          Select Data Type: {}
          <select value={newDataType} onChange={e => setNewDataType(e.target.value)}>
            <option value="">Select Data Type</option>
            {validDataTypes.map((type, index) => (
              <option key={index} value={type}>{type}</option>
            ))}
          </select>
        </label>
        <button type="submit">Override</button>
      </form>
    </div>
  );

}

export default DataTypeOverrideComponent;
