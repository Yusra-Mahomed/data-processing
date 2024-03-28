import React, { useState } from 'react';
import axios from 'axios';

function FileUploadComponent({ onUploadSuccess }) {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleUploadClick = async (e) => {
    e.preventDefault();
    if (!file) {
      console.error('No file selected');
      return;
    }
    const formData = new FormData();
    formData.append('datafile', file);

    try {
      const response = await axios.post('http://127.0.0.1:8000/data/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onUploadSuccess(response.data);
      console.log(response.data)
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <form>
      <input type="file" name="datafile" accept=".csv, .xlsx" onChange={handleFileChange} />
      <button type="button" onClick={handleUploadClick}>Upload</button>
    </form>
  );
}

export default FileUploadComponent;
