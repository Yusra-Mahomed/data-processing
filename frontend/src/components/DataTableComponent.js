import React, { useState } from 'react';
import DataTypeOverrideComponent from './DataTypeOverrideComponent';

function DataTableComponent({ processedData, onOverrideSuccess }) {
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(8); // Or any other number

  if (!processedData || processedData.length === 0) return null;

  // Calculate the indices of the first and last items on the current page
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;

  // Slice the data to only include the items for the current page
  const currentItems = processedData.processed_data.slice(indexOfFirstItem, indexOfLastItem);

  // Calculate total number of pages
  const totalPages = Math.ceil(processedData.processed_data.length / itemsPerPage);

  const handleOverride = (response) => {
    onOverrideSuccess(response.processed_data, response.columns_with_types);
  };

  // Function to change page
  const paginate = pageNumber => setCurrentPage(pageNumber);

  return (
    <div>
      <h2>Processed Data Results</h2>
      <table>
        <thead>
          <tr>
            {processedData.columns_with_types.map((item, index) => (
              <th key={index}>{item.column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {currentItems.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {processedData.columns_with_types.map((item, colIndex) => (
                <td key={colIndex}>
                  {typeof row[item.column] === 'boolean' ? row[item.column].toString() : row[item.column]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pagination-controls">
        <button onClick={() => paginate(1)} disabled={currentPage === 1}>
          First
        </button>
        <button onClick={() => paginate(currentPage - 1)} disabled={currentPage === 1}>
          Previous
        </button>
        <span>Page {currentPage} of {totalPages}</span>
        <button onClick={() => paginate(currentPage + 1)} disabled={currentPage === totalPages}>
          Next
        </button>
        <button onClick={() => paginate(totalPages)} disabled={currentPage === totalPages}>
          Last
        </button>
      </div>
      <div className="datatype-info">
        <h3>Data Types for Each Column</h3>
        <ul>
          {processedData.columns_with_types.map((item, index) => (
            <li key={index}>
              <strong>{item.column}</strong>: {item.data_type}
            </li>
          ))}
        </ul>
      </div>
      
      <DataTypeOverrideComponent columnsWithTypes={processedData.columns_with_types} onSubmitOverride={handleOverride} />
    </div>
    
  );
}

export default DataTableComponent;
