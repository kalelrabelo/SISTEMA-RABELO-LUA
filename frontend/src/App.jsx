import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ChatInterface from './components/ChatInterface'
import VoiceControls from './components/VoiceControls'
import Header from './components/Header'
import LuaConversation from './components/LuaConversation'

// Configure axios
axios.defaults.baseURL = import.meta.env.DEV ? 'http://localhost:5000' : ''

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [selectedVoice, setSelectedVoice] = useState('luna')
  const [voices, setVoices] = useState([])
  const [speechSpeed, setSpeechSpeed] = useState(1.0)
  const [systemStatus, setSystemStatus] = useState(null)
  const [showLuaConversation, setShowLuaConversation] = useState(false)
  
  const audioRef = useRef(null)

  // Check system health on mount
  useEffect(() => {
    checkSystemHealth()
    loadVoices()
    
    // Welcome message
    const welcomeMsg = {
      id: Date.now(),
      role: 'assistant',
      content: 'Olá! Eu sou a Lua 🌙, sua assistente de IA. Como posso ajudar você hoje?',
      timestamp: new Date().toISOString()
    }
    setMessages([welcomeMsg])
    
    // Listen for keyboard shortcuts
    const handleKeyPress = (e) => {
      // Alt + L to activate Lua conversation mode
      if (e.altKey && e.key === 'l') {
        setShowLuaConversation(true)
      }
    }
    
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get('/health')
      setSystemStatus(response.data)
    } catch (error) {
      console.error('Health check failed:', error)
      setSystemStatus({ status: 'error', services: {} })
    }
  }

  const loadVoices = async () => {
    try {
      const response = await axios.get('/api/voice/voices')
      if (response.data.success) {
        const voiceList = Object.entries(response.data.voices).map(([id, name]) => ({
          id,
          name
        }))
        setVoices(voiceList)
      }
    } catch (error) {
      console.error('Failed to load voices:', error)
    }
  }

  const sendMessage = async (text) => {
    // Create user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Send to backend
      const response = await axios.post('/api/chat', {
        message: text,
        user_id: 'web-user',
        voice_response: true
      })

      // Create assistant message
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString()
      }
      
      setMessages(prev => [...prev, assistantMessage])

      // Generate TTS if needed
      if (response.data.response) {
        await generateSpeech(response.data.response)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
        timestamp: new Date().toISOString(),
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const generateSpeech = async (text) => {
    try {
      const response = await axios.post('/api/tts/generate', {
        text,
        voice: selectedVoice,
        speed: speechSpeed
      }, {
        responseType: 'blob'
      })

      // Create audio URL
      const audioBlob = new Blob([response.data], { type: 'audio/wav' })
      const audioUrl = URL.createObjectURL(audioBlob)
      
      // Play audio
      if (audioRef.current) {
        audioRef.current.src = audioUrl
        audioRef.current.play()
      }
    } catch (error) {
      console.error('Error generating speech:', error)
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // Implement voice recording logic here
  }

  const clearMessages = () => {
    setMessages([{
      id: Date.now(),
      role: 'assistant',
      content: 'Histórico limpo! Como posso ajudar você?',
      timestamp: new Date().toISOString()
    }])
  }

  // Show Lua conversation mode if activated
  if (showLuaConversation) {
    return <LuaConversation onExit={() => setShowLuaConversation(false)} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900">
      <div className="container mx-auto px-4 py-8">
        <Header systemStatus={systemStatus} />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          {/* Main Chat Interface */}
          <div className="lg:col-span-2">
            <ChatInterface
              messages={messages}
              onSendMessage={sendMessage}
              isLoading={isLoading}
              onClearMessages={clearMessages}
            />
          </div>
          
          {/* Voice Controls */}
          <div className="lg:col-span-1">
            <VoiceControls
              voices={voices}
              selectedVoice={selectedVoice}
              onVoiceChange={setSelectedVoice}
              speechSpeed={speechSpeed}
              onSpeedChange={setSpeechSpeed}
              isRecording={isRecording}
              onToggleRecording={toggleRecording}
            />
            
            {/* Lua Conversation Button */}
            <div className="mt-6 bg-white/10 backdrop-blur-md rounded-lg p-6">
              <h3 className="text-white text-lg font-semibold mb-4">
                Modo Conversa da Lua
              </h3>
              <p className="text-white/70 text-sm mb-4">
                Entre em uma experiência imersiva de conversa com a Lua
              </p>
              <button
                onClick={() => setShowLuaConversation(true)}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-300"
              >
                Iniciar Modo Conversa 🌙
              </button>
              <p className="text-white/50 text-xs mt-2">
                Ou pressione Alt + L
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Hidden audio element */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  )
}

export default App