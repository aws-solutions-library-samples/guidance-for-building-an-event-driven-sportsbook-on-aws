import React, { useState, useRef, useEffect } from 'react';
import "../css/internalStyles.css";
import {
    useSendChatbotMessage,
  } from "../hooks/useChatbot";

export const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [sessionId, setSessionId] = useState(localStorage.getItem('chatbotSessionId') || '');
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const { mutateAsync: sendChatbotMessage } = useSendChatbotMessage();
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
        setSessionId('1');
    }
    document.addEventListener('keydown', handleKeyPress);

    // Clean up the event listener on component unmount
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [sessionId]);

  const sendMessageLocalImplementation = () => {
    if (inputText.trim() === '') return;
    var messageToSend = {
        "prompt": inputText.trim()
      }
    setMessages([...messages, { text: inputText, isUser: true }, {text: "...", isUser: false}]);
    sendChatbotMessage( { data: messageToSend }).then((response) => {
        const botReply = response.data.sendChatbotMessage.completion;
        setMessages([...messages, { text: inputText, isUser: true }, { text: botReply, isUser: false }]);
        div.current.scrollIntoView({ behavior: "smooth", block: "end" });
        setInputText('');
      }).catch(()=> {
        console.error('Error sending message:', error);
      })
  }

  const sendMessage = () => {
    const headers = {
        Authorization: 'Bearer 1234567890',
        'Content-Type': 'application/json',
      };
    if (inputText.trim() === '') return;
    var messageToSend = {
        "modelId": "anthropic.claude-v2",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
          "prompt": "\n\nHuman: Hello world\n\nAssistant:",
          "max_tokens_to_sample": 300,
          "temperature": 0.5,
          "top_k": 250,
          "top_p": 1,
          "stop_sequences": [
            "\\n\\nHuman:"
          ],
          "anthropic_version": "bedrock-2023-05-31"
        }
      }
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
          <button ref={chatbotButtonInputRef} onClick={sendMessageLocalImplementation}>Send</button>
        </div>
      </div>
    </div>
    </div>
  );
};

export default Chatbot;
