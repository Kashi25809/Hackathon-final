import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget/ChatWidget';

// Default implementation, that you can customize
export default function Root({ children }: { children: React.ReactNode }) {
    return (
        <>
            {children}
            <ChatWidget />
        </>
    );
}
