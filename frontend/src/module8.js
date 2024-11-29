import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

const Module8=()=> {
  const [importProgress, setImportProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState("");
  const [importedFiles, setImportedFiles] = useState([]);
  const [scheduleTime, setScheduleTime] = useState("");
  const [dbStatus, setDbStatus] = useState("");
  const [importFailure, setImportFailure] = useState("");

  const fetchImportProgress = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/data/import-progress");
      if (!response.ok) throw new Error("Failed to fetch import progress.");
      const data = await response.json();

      if (data.status === "success" && data.data) {
        setImportProgress(data.data.total_files * 20 || 0); // Example scaling factor
      } else {
        console.warn("Import progress data is not available.");
        setImportProgress(0);
      }
    } catch (error) {
      console.error("Error fetching import progress:", error.message);
      setImportProgress(0);
    }
  };

  const fetchImportedFiles = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/data/view-imported");
      if (!response.ok) throw new Error("Failed to fetch imported files.");
      const data = await response.json();

      setImportedFiles(data.data || []);
    } catch (error) {
      console.error("Error fetching imported files:", error.message);
      setImportedFiles([]);
    }
  };

  const testDatabaseConnection = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/database/connect");
      if (!response.ok) throw new Error("Failed to connect to database.");
      const data = await response.json();

      setDbStatus(data.message || "Database connection failed.");
    } catch (error) {
      console.error("Error testing database connection:", error.message);
      setDbStatus("Database connection failed.");
    }
  };

  const handleFileUpload = async (event) => {
    try {
      const file = event.target.files[0];
      if (!file) throw new Error("No file selected.");

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:5000/api/data/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus(result.message);
        fetchImportProgress();
        fetchImportedFiles();
      } else {
        throw new Error(result.message || "Unknown error during file upload.");
      }
    } catch (error) {
      console.error("File upload failed:", error.message);
      setImportFailure(error.message);
    }
  };

  const handleScheduleImport = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/data/schedule-import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ time: scheduleTime }),
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      console.error("Error scheduling import:", error.message);
      alert("Failed to schedule import.");
    }
  };

  useEffect(() => {
    fetchImportProgress();
    fetchImportedFiles();
    testDatabaseConnection();
  }, []);

  return (
    <div className="container mt-5">
      {/* Header */}
      <header className="header mb-4">
        <h2 className="text-white">Data Import Module</h2>
      </header>

      {/* Database Status */}
      <div className="card p-3 mb-4 shadow-sm">
        <h5 className="card-title">Database Status</h5>
        <p className="text-muted">{dbStatus}</p>
      </div>

      {/* File Upload Section */}
      <div className="card p-3 mb-4 shadow-sm">
        <h5 className="card-title">File Upload</h5>
        <p className="text-muted">CSV format supported</p>
        <div className="d-flex align-items-center">
          <input
            type="file"
            className="form-control me-3"
            onChange={handleFileUpload}
            style={{ maxWidth: "70%" }}
          />
          <button className="btn btn-success">Upload</button>
        </div>
        {uploadStatus && <p className="text-success mt-2">{uploadStatus}</p>}
        {importFailure && <p className="text-danger mt-2">{importFailure}</p>}
      </div>

      {/* Import Progress Section */}
      <div className="card p-3 mb-4 shadow-sm">
        <h5 className="card-title">Import Progress</h5>
        <div className="progress">
          <div
            className="progress-bar progress-bar-striped progress-bar-animated bg-success"
            role="progressbar"
            style={{ width: `${importProgress}%` }}
          >
            {importProgress}%
          </div>
        </div>
        <small className="text-muted">
          The import is currently in progress. Please wait...
        </small>
      </div>

      {/* View Imports Section */}
      <div className="card p-3 mb-4 shadow-sm">
        <h5 className="card-title">View Imports</h5>
        <table className="table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {importedFiles.map((file) => (
              <tr key={file._id}>
                <td>{file.filename}</td>
                <td className="text-success">Completed</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Schedule Imports Section */}
      <div className="card p-3 shadow-sm">
        <h5 className="card-title">Schedule Imports</h5>
        <div className="d-flex align-items-center">
          <input
            type="datetime-local"
            className="form-control me-3"
            value={scheduleTime}
            onChange={(e) => setScheduleTime(e.target.value)}
            style={{ maxWidth: "70%" }}
          />
          <button className="btn btn-secondary" onClick={handleScheduleImport}>
            Schedule
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer mt-5">
        <p className="text-center text-white py-2">
          Data Import Module © 2024
        </p>
      </footer>
    </div>
  );
};

export default Module8;
