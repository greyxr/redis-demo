import React from 'react';

const ResultList = ({ items }) => {
    return (
        <div style={{ fontFamily: 'Arial, sans-serif', margin: '20px' }}>
            {items.map((item) => (
                <div
                    key={item.id}
                    style={{
                        border: '1px solid #ccc',
                        borderRadius: '8px',
                        padding: '16px',
                        marginBottom: '16px',
                        display: 'flex',
                        alignItems: 'flex-start',
                        backgroundColor: '#f9f9f9',
                    }}
                >
                    <img
                        src={item.icon}
                        alt={item.name}
                        style={{
                            width: '64px',
                            height: '64px',
                            marginRight: '16px',
                            borderRadius: '4px',
                        }}
                    />
                    <div>
                        <h3 style={{ margin: '0 0 8px', color: '#333' }}>
                            {item.name}
                        </h3>
                        {item.description ? (<p
                            style={{
                                margin: '0 0 8px',
                                color: '#555',
                                fontStyle: 'italic',
                            }}
                            dangerouslySetInnerHTML={{ __html: item.description }}
                        />) : ''}
                        {item?.type && (
                        <p style={{ margin: '0 0 8px', color: '#666' }}>
                            <strong>Type:</strong> {item.type} - {item.details?.type}
                        </p>
                        )}
                        <p style={{ margin: '0', color: '#666' }}>
                            <strong>Rarity:</strong> {item.rarity}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ResultList;
