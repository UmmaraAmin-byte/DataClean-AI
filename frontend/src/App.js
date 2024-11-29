import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Module9 from './module9';  // Corrected import path
import Module8 from './module8';  // Corrected import path

function App() {
  return (
    <Router>
      <div className="container">
        <nav className="navbar navbar-expand-lg navbar-light" style={{ backgroundColor: '#0c8f8f' }}>
          <a className="navbar-brand" href="#" style={{ color: 'white' }}>DataCleanAI</a>
          <div className="ml-auto">
            <button className="btn btn-light" onClick={() => window.location.href='/module9'}>
              Go to Module 9
            </button>
            <button className="btn btn-light" onClick={() => window.location.href='/module8'}>
              Go to Module 8
            </button>
          </div>
        </nav>

        <Routes>
          <Route path="/module9" element={<Module9 />} />
          <Route path="/module8" element={<Module8 />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
