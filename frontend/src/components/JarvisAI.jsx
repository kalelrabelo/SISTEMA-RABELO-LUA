import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Sparkles, Brain, Zap, Activity } from 'lucide-react';

const JarvisAI = ({ onCommand }) => {
  const [isListening, setIsListening] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [status, setStatus] = useState('Aguardando comando "Lua"...');
  const [particles, setParticles] = useState([]);
  const [pulseAnimation, setPulseAnimation] = useState(false);
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  // Inicializar reconhecimento de voz
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'pt-BR';
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setStatus('Ouvindo...');
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        if (isActive) {
          // Reiniciar se ainda estiver ativo
          setTimeout(() => startListening(), 100);
        } else {
          setStatus('Aguardando comando "Lua"...');
        }
      };
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          } else {
            interimTranscript += result[0].transcript;
          }
        }
        
        const fullTranscript = finalTranscript || interimTranscript;
        setTranscript(fullTranscript);
        
        // Verificar palavra de ativação "Lua"
        if (fullTranscript.toLowerCase().includes('lua') && !isActive) {
          activateJarvis();
        }
        
        // Processar comandos se estiver ativo
        if (isActive && finalTranscript) {
          processCommand(finalTranscript);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error);
        setStatus(`Erro: ${event.error}`);
      };
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isActive]);

  // Animação das partículas
  useEffect(() => {
    generateParticles();
    startAnimation();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  const generateParticles = () => {
    const newParticles = [];
    for (let i = 0; i < 50; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * 400,
        y: Math.random() * 400,
        size: Math.random() * 3 + 1,
        speed: Math.random() * 2 + 1,
        angle: Math.random() * Math.PI * 2,
        opacity: Math.random() * 0.8 + 0.2,
        color: `hsl(${190 + Math.random() * 40}, 100%, ${50 + Math.random() * 30}%)`
      });
    }
    setParticles(newParticles);
  };

  const startAnimation = () => {
    const animate = () => {
      setParticles(prev => prev.map(particle => ({
        ...particle,
        x: particle.x + Math.cos(particle.angle) * particle.speed,
        y: particle.y + Math.sin(particle.angle) * particle.speed,
        angle: particle.angle + 0.02,
        opacity: particle.opacity * 0.995
      })).filter(p => p.opacity > 0.1));
      
      animationRef.current = requestAnimationFrame(animate);
    };
    animate();
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Erro ao iniciar reconhecimento:', error);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const activateJarvis = () => {
    setIsActive(true);
    setPulseAnimation(true);
    setStatus('Lua ativada! Como posso ajudar?');
    speak('Lua ativada! Como posso ajudar você hoje?');
    
    setTimeout(() => setPulseAnimation(false), 2000);
    
    // Auto-desativar após 30 segundos de inatividade
    setTimeout(() => {
      if (isActive) {
        deactivateJarvis();
      }
    }, 30000);
  };

  const deactivateJarvis = () => {
    setIsActive(false);
    setStatus('Aguardando comando "Lua"...');
    speak('Até logo!');
    stopListening();
  };

  const speak = (text) => {
    if (audioEnabled && synthRef.current) {
      synthRef.current.cancel(); // Cancelar falas anteriores
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'pt-BR';
      utterance.rate = 1;
      utterance.pitch = 1;
      synthRef.current.speak(utterance);
    }
  };

  const processCommand = (command) => {
    const lowerCommand = command.toLowerCase();
    
    // Comandos de navegação
    if (lowerCommand.includes('dashboard') || lowerCommand.includes('painel')) {
      onCommand('dashboard');
      speak('Abrindo dashboard');
    }
    else if (lowerCommand.includes('cliente')) {
      onCommand('clientes');
      speak('Abrindo gestão de clientes');
    }
    else if (lowerCommand.includes('funcionário') || lowerCommand.includes('funcionario')) {
      onCommand('funcionarios');
      speak('Abrindo gestão de funcionários');
    }
    else if (lowerCommand.includes('joia') || lowerCommand.includes('joias')) {
      onCommand('joias');
      speak('Abrindo catálogo de joias');
    }
    else if (lowerCommand.includes('material') || lowerCommand.includes('materiais')) {
      onCommand('materiais');
      speak('Abrindo gestão de materiais');
    }
    else if (lowerCommand.includes('pedra') || lowerCommand.includes('pedras')) {
      onCommand('pedras');
      speak('Abrindo catálogo de pedras');
    }
    else if (lowerCommand.includes('vale') || lowerCommand.includes('vales')) {
      onCommand('vales');
      speak('Abrindo gestão de vales');
    }
    else if (lowerCommand.includes('caixa')) {
      onCommand('caixa');
      speak('Abrindo controle de caixa');
    }
    else if (lowerCommand.includes('custo') || lowerCommand.includes('custos')) {
      onCommand('custos');
      speak('Abrindo gestão de custos');
    }
    else if (lowerCommand.includes('estoque')) {
      onCommand('estoque');
      speak('Abrindo controle de estoque');
    }
    else if (lowerCommand.includes('encomenda')) {
      onCommand('encomendas');
      speak('Abrindo gestão de encomendas');
    }
    else if (lowerCommand.includes('folha') || lowerCommand.includes('pagamento')) {
      onCommand('folha-pagamento');
      speak('Abrindo folha de pagamento');
    }
    else if (lowerCommand.includes('sair') || lowerCommand.includes('tchau') || lowerCommand.includes('desativar')) {
      deactivateJarvis();
    }
    else {
      speak('Comando não reconhecido. Tente novamente.');
      setStatus('Comando não reconhecido');
    }
    
    setTranscript('');
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Iniciar escuta automática
  useEffect(() => {
    startListening();
  }, []);

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Área de visualização da IA */}
      <div className={`mb-4 transition-all duration-500 ${isActive ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'}`}>
        <div className="bg-gray-800/90 backdrop-blur-md border border-blue-500/30 rounded-2xl p-4 w-80 shadow-2xl">
          {/* Header */}
          <div className="flex items-center gap-3 mb-3">
            <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-400' : 'bg-gray-400'} animate-pulse`}></div>
            <span className="text-blue-300 font-semibold">LUA - Assistente IA</span>
            <div className="ml-auto flex gap-2">
              <button
                onClick={() => setAudioEnabled(!audioEnabled)}
                className="p-1 text-gray-400 hover:text-white transition-colors"
              >
                {audioEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
              </button>
            </div>
          </div>
          
          {/* Status */}
          <div className="text-sm text-gray-300 mb-2">{status}</div>
          
          {/* Transcrição */}
          {transcript && (
            <div className="text-sm text-blue-200 bg-blue-900/30 rounded-lg p-2 mb-3">
              "{transcript}"
            </div>
          )}
          
          {/* Comandos disponíveis */}
          <div className="text-xs text-gray-400">
            <div>Comandos: "dashboard", "clientes", "funcionários", "joias", "materiais", "vales", "estoque"...</div>
            <div className="mt-1">Diga "sair" para desativar</div>
          </div>
        </div>
      </div>

      {/* Orb principal */}
      <div className="relative">
        {/* Partículas de fundo */}
        <div className="absolute inset-0 w-20 h-20 rounded-full overflow-hidden">
          {particles.map(particle => (
            <div
              key={particle.id}
              className="absolute w-1 h-1 rounded-full"
              style={{
                left: `${(particle.x / 400) * 100}%`,
                top: `${(particle.y / 400) * 100}%`,
                backgroundColor: particle.color,
                opacity: particle.opacity,
                boxShadow: `0 0 ${particle.size * 2}px ${particle.color}`
              }}
            />
          ))}
        </div>

        {/* Orb principal */}
        <div 
          className={`
            relative w-20 h-20 rounded-full cursor-pointer transition-all duration-300
            ${isActive 
              ? 'bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 shadow-2xl shadow-blue-500/50' 
              : 'bg-gradient-to-r from-gray-600 to-gray-700 shadow-lg'
            }
            ${pulseAnimation ? 'animate-ping' : ''}
            ${isListening ? 'scale-110 shadow-2xl shadow-green-500/50' : 'scale-100'}
          `}
          onClick={toggleListening}
        >
          {/* Anéis de energia */}
          <div className={`absolute inset-0 rounded-full border-2 ${isActive ? 'border-blue-400' : 'border-gray-500'} animate-pulse`}></div>
          <div className={`absolute inset-2 rounded-full border ${isActive ? 'border-purple-400' : 'border-gray-600'} animate-pulse`} style={{animationDelay: '0.5s'}}></div>
          
          {/* Ícone central */}
          <div className="absolute inset-0 flex items-center justify-center">
            {isListening ? (
              <div className="flex items-center gap-1">
                <div className="w-1 h-4 bg-white rounded animate-pulse"></div>
                <div className="w-1 h-6 bg-white rounded animate-pulse" style={{animationDelay: '0.1s'}}></div>
                <div className="w-1 h-3 bg-white rounded animate-pulse" style={{animationDelay: '0.2s'}}></div>
              </div>
            ) : isActive ? (
              <Brain className="w-8 h-8 text-white animate-pulse" />
            ) : (
              <Sparkles className="w-8 h-8 text-gray-300" />
            )}
          </div>
        </div>

        {/* Indicador de estado */}
        <div className="absolute -bottom-2 -right-2">
          {isListening && (
            <div className="w-4 h-4 bg-green-500 rounded-full animate-ping"></div>
          )}
          {isActive && !isListening && (
            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
          )}
        </div>
      </div>

      {/* Efeitos visuais adicionais */}
      {isActive && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute w-32 h-32 -top-6 -left-6 border border-blue-500/20 rounded-full animate-spin" style={{animationDuration: '10s'}}></div>
          <div className="absolute w-28 h-28 -top-4 -left-4 border border-purple-500/20 rounded-full animate-spin" style={{animationDuration: '8s', animationDirection: 'reverse'}}></div>
        </div>
      )}
    </div>
  );
};

export default JarvisAI;