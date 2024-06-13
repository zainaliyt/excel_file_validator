// src/components/FileUploadComponent.js
import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState('');
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');
    const [criteriaMet, setCriteriaMet] = useState([]);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setResult('');
        setStatus('');
        setError('');
        setCriteriaMet([]);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:5000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.status === 200) {
                console.log(response.data);
                setResult(response.data.message); // Display success message
                setStatus(response.data.status);
                if (response.data.message) {
                    const criteriaMetArray = Object.keys(response.data.message).map(key => ({
                        key: response.data.message[key].message,
                        result: response.data.message[key].result
                    }));
                    setCriteriaMet(criteriaMetArray);
                }
                // Trigger history update
                onUploadSuccess();
            } else {
                setError(response.data.error); // Display specific error message from API
            }
        } catch (error) {
            setError('Error: ' + error.response.data.message); // Handle network or other errors
            console.error('Error: ', error);
        }
    };

    return (
        <div>
            <h2>File Upload</h2>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} />
                <button type="submit">Upload</button>
            </form>
            {status === true && <p style={{ color:'green'}} >Uploaded File is Correct</p>}
            {status === false && <p style={{ color:'red'}}>Not meeting criteria:</p>}
            {criteriaMet.length > 0 && (
                <div>
                    <ul>
                        {criteriaMet.map(item => (
                            !item.result && ( // Render only if result is false
                                <li key={item.key}>
                                    <span style={{ marginLeft: '5px' }}>{`${item.key}`}</span>
                                </li>
                            )
                        ))}
                    </ul>
                </div>
            )}
            {error && <p style={{ color: 'red' }}>{error}</p>} {/* Display error if there's an error */}
        </div>
    );
};

export default FileUpload;
