import React, { useEffect } from 'react';
import ChatWidget from '../components/ChatWidget/ChatWidget';

// Wrapper to ensure layout existence
export default function LayoutWrapper({ children }) {
    return (
        <>
            {children}
            <ChatWidget />
        </>
    );
}
