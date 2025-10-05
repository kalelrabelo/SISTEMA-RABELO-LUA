import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import './LuaConversation.css';

const LuaConversation = () => {
  const [isConversationMode, setIsConversationMode] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [luaResponse, setLuaResponse] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  
  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'pt-BR';
      
      recognitionRef.current.onresult = (event) => {
        const current = event.resultIndex;
        const transcript = event.results[current][0].transcript;
        setTranscript(transcript);
        
        if (event.results[current].isFinal) {
          handleUserMessage(transcript);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setError(`Erro no reconhecimento de voz: ${event.error}`);
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
        if (isConversationMode && isListening) {
          // Restart recognition if still in conversation mode
          recognitionRef.current.start();
        }
      };
    } else {
      setError('Reconhecimento de voz não suportado neste navegador');
    }
    
    // Initialize Audio Context for visualization
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isConversationMode, isListening]);
  
  // Start conversation mode
  const startConversation = useCallback(() => {
    setIsConversationMode(true);
    setIsListening(true);
    setError(null);
    
    // Start speech recognition
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
    
    // Play entrance animation
    setTimeout(() => {
      if (videoRef.current) {
        videoRef.current.play();
      }
    }, 500);
    
    // Send initial greeting to Lua
    sendMessageToLua("Olá Lua, vamos conversar!");
  }, []);
  
  // Stop conversation mode
  const stopConversation = useCallback(() => {
    setIsConversationMode(false);
    setIsListening(false);
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  }, []);
  
  // Handle user message
  const handleUserMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add to conversation history
    setConversationHistory(prev => [...prev, { role: 'user', content: message }]);
    
    // Send to Lua
    await sendMessageToLua(message);
  };
  
  // Send message to Lua backend
  const sendMessageToLua = async (message) => {
    setIsSpeaking(true);
    
    try {
      // Get text response from Lua
      const chatResponse = await axios.post(`${API_URL}/api/chat`, {
        message: message,
        user_id: 'web-user',
        context: {
          mode: 'conversation',
          history: conversationHistory.slice(-5) // Send last 5 messages for context
        }
      });
      
      const luaText = chatResponse.data.response;
      setLuaResponse(luaText);
      
      // Add to conversation history
      setConversationHistory(prev => [...prev, { role: 'assistant', content: luaText }]);
      
      // Get TTS audio
      const ttsResponse = await axios.post(`${API_URL}/api/tts/generate`, {
        text: luaText,
        voice: 'luna',
        speed: 1.0
      }, {
        responseType: 'blob'
      });
      
      // Play audio
      const audioBlob = new Blob([ttsResponse.data], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        
        // Analyze audio for visualization
        analyzeAudio(audioRef.current);
      }
      
    } catch (error) {
      console.error('Error communicating with Lua:', error);
      setError('Erro ao comunicar com a Lua. Por favor, tente novamente.');
    } finally {
      setIsSpeaking(false);
    }
  };
  
  // Analyze audio for sphere pulsing effect
  const analyzeAudio = (audioElement) => {
    if (!audioContextRef.current) return;
    
    const source = audioContextRef.current.createMediaElementSource(audioElement);
    analyserRef.current = audioContextRef.current.createAnalyser();
    analyserRef.current.fftSize = 256;
    
    source.connect(analyserRef.current);
    analyserRef.current.connect(audioContextRef.current.destination);
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const updateLevel = () => {
      if (!analyserRef.current) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      
      // Calculate average volume
      const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
      const normalizedLevel = average / 255; // Normalize to 0-1
      
      setAudioLevel(normalizedLevel);
      
      if (isSpeaking) {
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      }
    };
    
    updateLevel();
  };
  
  // Check for wake word
  useEffect(() => {
    if (transcript.toLowerCase().includes('lua') && 
        (transcript.toLowerCase().includes('iniciar modo conversa') || 
         transcript.toLowerCase().includes('conversar'))) {
      startConversation();
      setTranscript('');
    }
  }, [transcript, startConversation]);
  
  // Calculate sphere scale based on audio level
  const sphereScale = 1 + (audioLevel * 0.3); // Scale from 1.0 to 1.3
  
  return (
    <div className={`lua-conversation-container ${isConversationMode ? 'active' : ''}`}>
      {/* Main content when not in conversation mode */}
      {!isConversationMode && (
        <div className="main-content">
          <h2>Assistente Lua</h2>
          <p>Diga "Lua, iniciar modo conversa" para começar</p>
          <button onClick={startConversation} className="start-button">
            Iniciar Conversa com a Lua
          </button>
        </div>
      )}
      
      {/* Conversation mode */}
      {isConversationMode && (
        <div className="conversation-mode">
          {/* Background fade */}
          <div className="fade-overlay"></div>
          
          {/* Energy sphere video */}
          <div className="sphere-container">
            <video
              ref={videoRef}
              className="energy-sphere"
              autoPlay
              loop
              muted
              playsInline
              style={{
                transform: `scale(${sphereScale})`,
                transition: 'transform 0.1s ease-out'
              }}
            >
              <source src="/videos/abstract-blue-looped-energy-sphere.mp4" type="video/mp4" />
              Seu navegador não suporta vídeos.
            </video>
            
            {/* Pulsing glow effect */}
            {isSpeaking && (
              <div 
                className="sphere-glow" 
                style={{
                  opacity: audioLevel * 0.8,
                  transform: `scale(${1 + audioLevel * 0.5})`
                }}
              />
            )}
          </div>
          
          {/* Status indicators */}
          <div className="status-container">
            {isListening && !isSpeaking && (
              <div className="status listening">
                <span className="pulse-dot"></span>
                Ouvindo...
              </div>
            )}
            
            {isSpeaking && (
              <div className="status speaking">
                <span className="pulse-dot"></span>
                Lua está falando...
              </div>
            )}
          </div>
          
          {/* Transcript display */}
          <div className="transcript-container">
            {transcript && (
              <div className="user-transcript">
                <strong>Você:</strong> {transcript}
              </div>
            )}
            
            {luaResponse && (
              <div className="lua-response">
                <strong>Lua:</strong> {luaResponse}
              </div>
            )}
          </div>
          
          {/* Error display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          {/* Exit button */}
          <button onClick={stopConversation} className="exit-button">
            Encerrar Conversa
          </button>
        </div>
      )}
      
      {/* Hidden audio element */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  );
};

export default LuaConversation;