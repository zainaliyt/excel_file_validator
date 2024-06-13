// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';
import FileUpload from './components/fileUploadComponent';
import HistoryComponent from './components/historyComponent';
import axios from 'axios';

function App() {
    const [historyData, setHistoryData] = useState([]);

    useEffect(() => {
        fetchHistoryData();
    }, []);

    const fetchHistoryData = async () => {
        try {
            const response = await axios.get('http://localhost:5000/history');
            setHistoryData(response.data);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
              <h1>Excel File Validator</h1>
                <div className="two-column-container">
                    <div className="column">
                        <FileUpload onUploadSuccess={fetchHistoryData} />
                    </div>
                    <div className="column">
                        <HistoryComponent historyData={historyData} />
                    </div>
                </div>
            </header>
        </div>
    );
}

export default App;
