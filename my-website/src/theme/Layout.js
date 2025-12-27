import React from 'react';
// Import the original Layout
import Layout from '@theme-original/Layout';
import ChatWidget from '@site/src/components/ChatWidget/ChatWidget';

export default function LayoutWrapped(props) {
    return (
        <>
            <Layout {...props} />
            <div id="z-chat-container" style={{ position: 'fixed', bottom: 10, right: 10, zIndex: 9999999 }}>
                <ChatWidget apiUrl="https://kashi25809-hackathon.hf.space" />
            </div>
        </>
    );
}
