import React, { useState, useRef, useEffect } from 'react';
import "../css/internalStyles.css";
import axios from 'axios';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [sessionId, setSessionId] = useState(localStorage.getItem('chatbotSessionId') || '');
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const chatbotInputRef = useRef(null);
  const isChatbotOpenRef = useRef(isChatbotOpen);
  const chatbotButtonInputRef = useRef(null);
  
  const toggleChatbot = () => {
    setIsChatbotOpen(!isChatbotOpen);
    isChatbotOpenRef.current = !isChatbotOpen;
  };

  useEffect(() => {
    isChatbotOpenRef.current = isChatbotOpen;
    // Initialize or retrieve the session ID from local storage
    if (!sessionId) {
      /*axios.post('/api/startSession') // Replace with your backend API endpoint
        .then(response => {
          const newSessionId = response.data.sessionId;
          setSessionId(newSessionId);
          localStorage.setItem('chatbotSessionId', newSessionId);
        })
        .catch(error => {
          console.error('Error starting session:', error);
        });*/
        setSessionId('1');
    }
    document.addEventListener('keydown', handleKeyPress);

    // Clean up the event listener on component unmount
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [sessionId]);

  const sendMessage = () => {
    const headers = {
        Authorization: 'Bearer 1234567890',
        'Content-Type': 'application/json',
      };
    if (inputText.trim() === '') return;
    var messageToSend = {
        "input": inputText,
        "schema": ""
    }
    // Send the user's message to the backend
    axios.post('https://em69k83ho9.execute-api.us-east-1.amazonaws.com/prod/', {
      sessionId,
      message: messageToSend,
    }, headers)
    .then(response => {
      const botReply = response.data.query;
      setMessages([...messages, { text: inputText, isUser: true }, { text: botReply, isUser: false }]);
      setInputText('');
    })
    .catch(error => {
      console.error('Error sending message:', error);
    });
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && isChatbotOpenRef.current && document.activeElement === chatbotInputRef.current) {
        chatbotButtonInputRef.current.click();
        //sendMessage();
    }
  };

  /*const sendMessage = () => {
    if (inputText.trim() === '') return;

    // Simulate a response from the bot (replace with your own mock data)
    const botReply = `Mock Bot: You said "${inputText}"`;
    setMessages([...messages, { text: inputText, isUser: true }, { text: botReply, isUser: false }]);
    setInputText('');
  };*/

  return (
    <div>
    <div 
        className="chatbot-button" 
        onClick={toggleChatbot}
        hidden={isChatbotOpen}
    >
        Chatbot
    </div>
    <div className={`chatbot-container ${isChatbotOpen ? 'open' : ''}`}>
      <div className="chatbot">
        <div className="chatbot-header">
          Chatbot
          <button onClick={toggleChatbot} className="close-button">
            X
          </button>
        </div>
        <div className="chatbot-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.isUser ? 'user' : 'bot'}`}>
              {message.text}
            </div>
          ))}
        </div>
        <div className="chatbot-input">
          <input
            type="text"
            placeholder="Type your message..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            ref={chatbotInputRef}
          />
          <button ref={chatbotButtonInputRef} onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
    </div>
  );
};

export default Chatbot;
