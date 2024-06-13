// src/components/HistoryComponent.js
import React from 'react';

const HistoryComponent = ({ historyData }) => {
    return (
        <div>
            <h2>History</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid black' }}>
                        <th style={{ padding: '8px', textAlign: 'left' }}>File Name</th>
                        <th style={{ padding: '8px', textAlign: 'left' }}>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {historyData.map(item => (
                        <tr key={item.id} style={{ borderBottom: '1px solid #ddd' }}>
                            <td style={{ padding: '8px', textAlign: 'left' }}>{item.filename}</td>
                            <td style={{ padding: '8px', textAlign: 'left',color: item.valid ? 'green' : 'red'}}>
                                {item.valid ? 'Valid File' : 'Not Valid'}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default HistoryComponent;
