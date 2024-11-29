// src/components/Module9.js
import React, { useState } from 'react';
import axios from 'axios';

const Module9 = () => {
  const [fileId, setFileId] = useState('');
  const [status, setStatus] = useState('');
  const [message, setMessage] = useState('');
  
  const handleFileIdChange = (e) => setFileId(e.target.value);

  // Function to trigger the file import
  const importData = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('file', e.target.files[0]);
      
      const response = await axios.post('http://localhost:5000/api/module9/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      setStatus(response.data.status);
      setMessage(response.data.file_id);
    } catch (error) {
      setStatus('error');
      setMessage(error.message);
    }
  };

  const removeDuplicates = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/module9/remove_duplicates', { file_id: fileId });
      setStatus(response.data.status);
      setMessage(`Duplicates removed: ${response.data.duplicates_removed}`);
    } catch (error) {
      setStatus('error');
      setMessage(error.message);
    }
  };

  const fillMissingData = async (strategy) => {
    try {
      const response = await axios.post('http://localhost:5000/api/module9/fill_missing', {
        file_id: fileId,
        strategy,
      });
      setStatus(response.data.status);
      setMessage(response.data.message);
    } catch (error) {
      setStatus('error');
      setMessage(error.message);
    }
  };

  const normalizeData = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/module9/normalize', { file_id: fileId });
      setStatus(response.data.status);
      setMessage(`Normalized columns: ${response.data.normalized_columns.join(', ')}`);
    } catch (error) {
      setStatus('error');
      setMessage(error.message);
    }
  };

  const detectOutliers = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/module9/detect_outliers', { file_id: fileId });
      setStatus(response.data.status);
      setMessage(`Outliers detected: ${JSON.stringify(response.data.outliers_detected)}`);
    } catch (error) {
      setStatus('error');
      setMessage(error.message);
    }
  };

  const trackProgress = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/module9/progress?file_id=${fileId}`);
      setStatus(response.data.status);
      setMessage(`Progress: ${JSON.stringify(response.data.progress)}`);
    } catch (error) {
      setStatus('error');
      setMessage(error.message);
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="text-center">Module 9: Data Cleaning Operations</h2>
      <form>
        <div className="mb-3">
          <label htmlFor="fileId" className="form-label">File ID</label>
          <input
            type="text"
            className="form-control"
            id="fileId"
            value={fileId}
            onChange={handleFileIdChange}
            placeholder="Enter File ID"
          />
        </div>
        <div className="mb-3">
          <label htmlFor="fileInput" className="form-label">Import File</label>
          <input
            type="file"
            className="form-control"
            id="fileInput"
            onChange={importData}
          />
        </div>

        {/* Action Buttons */}
        <div className="d-flex justify-content-between">
          <button type="button" className="btn btn-primary" onClick={removeDuplicates}>
            Remove Duplicates
          </button>
          <button type="button" className="btn btn-warning" onClick={() => fillMissingData('mean')}>
            Fill Missing Data (Mean)
          </button>
          <button type="button" className="btn btn-info" onClick={normalizeData}>
            Normalize Data
          </button>
          <button type="button" className="btn btn-danger" onClick={detectOutliers}>
            Detect Outliers
          </button>
          <button type="button" className="btn btn-secondary" onClick={trackProgress}>
            Track Progress
          </button>
        </div>

        {/* Status and Message */}
        {status && (
          <div className={`alert alert-${status === 'error' ? 'danger' : 'success'} mt-4`}>
            <strong>{status === 'error' ? 'Error:' : 'Success:'}</strong> {message}
          </div>
        )}
      </form>
    </div>
  );
};

export default Module9;
