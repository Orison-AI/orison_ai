"use client";

import React from 'react';

type ModalGIFProps = {
    gifSrc: string;
    width?: number;
    height?: number;
};

const ModalGIF: React.FC<ModalGIFProps> = ({ gifSrc, width = 1200, height = 550 }) => {
    return (
        <div
            style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                margin: '20px auto',
                width: '100%',
            }}
        >
            <div
                style={{
                    width: `${width}px`,
                    height: `${height}px`,
                    overflow: 'hidden',
                    border: '1px solid #ccc',
                    borderRadius: '10px',
                }}
            >
                <img
                    src={gifSrc}
                    alt="GIF"
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
            </div>
        </div>
    );
};

export default ModalGIF;
