import './App.css';

import React, { useState } from 'react';
import FileUploadComponent from './components/FileUploadComponent';
import DataTableComponent from './components/DataTableComponent';

function App() {
  const [processedData, setProcessedData] = useState([]);

  const handleUploadSuccess = async (data) => {
   
    console.log("plsss", data)
    console.log(data.processed_data[0])
    setProcessedData(data);
    console.log("again", processedData)
  };

  const handleOverrideSuccess = (newProcessedData, newColumnsWithTypes) => {
    setProcessedData(prevData => ({
      ...prevData,
      processed_data: newProcessedData,
      columns_with_types: newColumnsWithTypes,
    }));
  };

  return (
    <div>
      <h2>Upload a File</h2>
      <FileUploadComponent onUploadSuccess={handleUploadSuccess} />
      <DataTableComponent processedData={processedData} 
      onOverrideSuccess={handleOverrideSuccess} 
      />
    </div>
  );
}

export default App;
