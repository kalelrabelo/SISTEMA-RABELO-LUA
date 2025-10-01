import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Sparkles, Brain, Zap, Activity, X } from 'lucide-react';
import axios from 'axios';

const JarvisAI = ({ onCommand, onModalOpen }) => {
  const [isListening, setIsListening] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [status, setStatus] = useState('Aguardando comando "Lua"...');
  const [particles, setParticles] = useState([]);
  const [pulseAnimation, setPulseAnimation] = useState(false);
  const [isMinimized, setIsMinimized] = useState(true);
  const [commandHistory, setCommandHistory] = useState([]);
  const [speechSupported, setSpeechSupported] = useState(false);
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const timeoutRef = useRef(null);
  const isProcessingRef = useRef(false);

  // Verificar suporte a Speech API
  useEffect(() => {
    const checkSpeechSupport = () => {
      const hasRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
      const hasSynthesis = 'speechSynthesis' in window;
      setSpeechSupported(hasRecognition && hasSynthesis);
      
      if (!hasRecognition) {
        console.warn('Reconhecimento de voz não suportado neste navegador');
        setStatus('Reconhecimento de voz não disponível');
      }
      if (!hasSynthesis) {
        console.warn('Síntese de voz não suportada neste navegador');
      }
    };
    
    checkSpeechSupport();
  }, []);

  // Inicializar reconhecimento de voz com tratamento de erros melhorado
  useEffect(() => {
    if (!speechSupported) return;

    try {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'pt-BR';
      recognitionRef.current.maxAlternatives = 3;
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setStatus(isActive ? 'Escutando comandos...' : 'Aguardando ativação...');
        console.log('Reconhecimento de voz iniciado');
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        console.log('Reconhecimento de voz encerrado');
        
        // Reiniciar apenas se não estivermos processando
        if (!isProcessingRef.current && speechSupported) {
          setTimeout(() => {
            if (recognitionRef.current && !isListening) {
              startListening();
            }
          }, 500);
        }
      };
      
      recognitionRef.current.onresult = (event) => {
        try {
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
          
          const fullTranscript = (finalTranscript || interimTranscript).trim();
          if (fullTranscript) {
            setTranscript(fullTranscript);
            
            // Verificar ativação com mais variações
            const activationWords = ['lua', 'lúa', 'lia', 'luá', 'luar'];
            const transcriptLower = fullTranscript.toLowerCase();
            
            if (!isActive && activationWords.some(word => transcriptLower.includes(word))) {
              activateJarvis();
            } else if (isActive && finalTranscript) {
              processCommand(finalTranscript);
            }
          }
        } catch (error) {
          console.error('Erro ao processar resultado de voz:', error);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error);
        
        // Tratar erros específicos
        switch(event.error) {
          case 'network':
            setStatus('Erro de rede - verifique sua conexão');
            break;
          case 'not-allowed':
            setStatus('Permissão de microfone negada');
            setSpeechSupported(false);
            break;
          case 'no-speech':
            setStatus('Nenhuma fala detectada');
            break;
          case 'aborted':
            setStatus('Reconhecimento cancelado');
            break;
          default:
            setStatus(`Erro: ${event.error}`);
        }
        
        // Tentar reiniciar após erro (exceto permissão negada)
        if (event.error !== 'not-allowed' && speechSupported) {
          setTimeout(() => startListening(), 2000);
        }
      };
      
      // Iniciar escuta automática
      startListening();
    } catch (error) {
      console.error('Erro ao configurar reconhecimento de voz:', error);
      setSpeechSupported(false);
      setStatus('Erro ao inicializar reconhecimento de voz');
    }
    
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.error('Erro ao parar reconhecimento:', error);
        }
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isActive, speechSupported]);

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
    for (let i = 0; i < 30; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * 300,
        y: Math.random() * 300,
        size: Math.random() * 2 + 1,
        speed: Math.random() * 1.5 + 0.5,
        angle: Math.random() * Math.PI * 2,
        opacity: Math.random() * 0.6 + 0.2,
        color: `hsl(${190 + Math.random() * 40}, 100%, ${50 + Math.random() * 30}%)`
      });
    }
    setParticles(newParticles);
  };

  const startAnimation = () => {
    const animate = () => {
      setParticles(prev => prev.map(particle => ({
        ...particle,
        x: (particle.x + Math.cos(particle.angle) * particle.speed) % 300,
        y: (particle.y + Math.sin(particle.angle) * particle.speed) % 300,
        angle: particle.angle + 0.01,
        opacity: Math.max(0.1, particle.opacity * 0.998)
      })));
      
      animationRef.current = requestAnimationFrame(animate);
    };
    animate();
  };

  const startListening = () => {
    if (!speechSupported || !recognitionRef.current || isListening) return;
    
    try {
      recognitionRef.current.start();
      console.log('Tentando iniciar reconhecimento de voz');
    } catch (error) {
      if (error.message && error.message.includes('already started')) {
        console.log('Reconhecimento já está em execução');
      } else {
        console.error('Erro ao iniciar reconhecimento:', error);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
        console.log('Parando reconhecimento de voz');
      } catch (error) {
        console.error('Erro ao parar reconhecimento:', error);
      }
    }
  };

  const activateJarvis = () => {
    setIsActive(true);
    setPulseAnimation(true);
    setIsMinimized(false);
    setStatus('LUA ativada - Pronta para servir');
    speak('Olá senhor. Sou a LUA, sua assistente virtual. Como posso ajudá-lo hoje?');
    
    // Adicionar ao histórico
    addToHistory('Sistema', 'LUA ativada');
    
    setTimeout(() => setPulseAnimation(false), 2000);
    
    // Auto-desativar após 60 segundos de inatividade
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      if (isActive) {
        deactivateJarvis();
      }
    }, 60000);
  };

  const deactivateJarvis = () => {
    setIsActive(false);
    setStatus('Sistema em standby');
    speak('Estarei aqui quando precisar, senhor. Até logo.');
    setIsMinimized(true);
    
    // Adicionar ao histórico
    addToHistory('Sistema', 'LUA desativada');
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  const speak = (text) => {
    if (!audioEnabled || !synthRef.current) return;
    
    try {
      // Cancelar falas anteriores
      synthRef.current.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'pt-BR';
      utterance.rate = 0.95;
      utterance.pitch = 0.9;
      utterance.volume = 0.9;
      
      // Buscar voz feminina brasileira
      const voices = synthRef.current.getVoices();
      const brazilianVoice = voices.find(voice => 
        voice.lang.includes('pt-BR') && 
        (voice.name.toLowerCase().includes('female') || 
         voice.name.toLowerCase().includes('feminina') ||
         voice.name.includes('Microsoft Maria') ||
         voice.name.includes('Google português do Brasil'))
      );
      
      if (brazilianVoice) {
        utterance.voice = brazilianVoice;
      }
      
      utterance.onstart = () => {
        isProcessingRef.current = true;
      };
      
      utterance.onend = () => {
        isProcessingRef.current = false;
        if (isActive && !isListening && speechSupported) {
          setTimeout(() => startListening(), 500);
        }
      };
      
      utterance.onerror = (event) => {
        console.error('Erro na síntese de voz:', event);
        isProcessingRef.current = false;
      };
      
      synthRef.current.speak(utterance);
    } catch (error) {
      console.error('Erro ao falar:', error);
      isProcessingRef.current = false;
    }
  };

  const addToHistory = (type, message) => {
    setCommandHistory(prev => [...prev.slice(-4), { type, message, timestamp: new Date() }]);
  };

  const processCommand = async (command) => {
    const lowerCommand = command.toLowerCase();
    isProcessingRef.current = true;
    
    // Adicionar ao histórico
    addToHistory('Usuário', command);
    
    // Resetar timeout de inatividade
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      if (isActive) deactivateJarvis();
    }, 60000);
    
    try {
      // Comandos do sistema
      if (lowerCommand.includes('sair') || lowerCommand.includes('tchau') || lowerCommand.includes('desativar')) {
        deactivateJarvis();
        return;
      }
      
      if (lowerCommand.includes('obrigado') || lowerCommand.includes('obrigada')) {
        speak('Sempre às ordens, senhor. Posso ajudá-lo em algo mais?');
        addToHistory('LUA', 'Sempre às ordens');
        setStatus('Aguardando próximo comando...');
        return;
      }

      // Comandos de navegação com abertura de modais
      const navigationCommands = [
        { keywords: ['dashboard', 'painel', 'início'], module: 'dashboard', message: 'Acessando o painel principal' },
        { keywords: ['cliente'], module: 'clientes', message: 'Abrindo gestão de clientes' },
        { keywords: ['funcionário', 'funcionario', 'colaborador'], module: 'funcionarios', message: 'Abrindo gestão de funcionários' },
        { keywords: ['joia', 'joias', 'catálogo'], module: 'joias', message: 'Acessando catálogo de joias' },
        { keywords: ['material', 'materiais'], module: 'materiais', message: 'Abrindo gestão de materiais' },
        { keywords: ['pedra', 'pedras'], module: 'pedras', message: 'Acessando catálogo de pedras' },
        { keywords: ['vale', 'vales', 'adiantamento'], module: 'vales', message: 'Abrindo sistema de vales' },
        { keywords: ['caixa', 'financeiro'], module: 'caixa', message: 'Acessando controle de caixa' },
        { keywords: ['custo', 'custos'], module: 'custos', message: 'Abrindo gestão de custos' },
        { keywords: ['estoque', 'inventário'], module: 'estoque', message: 'Acessando controle de estoque' },
        { keywords: ['encomenda', 'pedido'], module: 'encomendas', message: 'Abrindo gestão de encomendas' },
        { keywords: ['folha', 'pagamento', 'salário'], module: 'folha-pagamento', message: 'Acessando folha de pagamento' },
        { keywords: ['nota', 'notas', 'anotação'], module: 'notas', message: 'Abrindo sistema de notas' },
        { keywords: ['imposto', 'impostos', 'fiscal'], module: 'impostos', message: 'Acessando gestão fiscal' },
        { keywords: ['entrada', 'entradas'], module: 'entradas', message: 'Abrindo controle de entradas' }
      ];

      // Verificar comandos de navegação
      for (const navCmd of navigationCommands) {
        if (navCmd.keywords.some(keyword => lowerCommand.includes(keyword))) {
          speak(`Sim senhor, ${navCmd.message.toLowerCase()}.`);
          addToHistory('LUA', navCmd.message);
          
          // Chamar callback de navegação
          if (onCommand) {
            onCommand(navCmd.module);
          }
          
          // Chamar callback de abertura de modal se disponível
          if (onModalOpen) {
            // Processar filtros específicos do comando
            const filters = extractFilters(command, navCmd.module);
            onModalOpen(navCmd.module, filters);
          }
          
          setStatus(`${navCmd.message}...`);
          return;
        }
      }

      // Comandos específicos com ações
      if (lowerCommand.includes('criar') || lowerCommand.includes('cadastrar') || lowerCommand.includes('novo')) {
        // Detectar o que criar
        if (lowerCommand.includes('vale')) {
          const employeeName = extractEmployeeName(command);
          const amount = extractAmount(command);
          
          if (employeeName || amount) {
            await createVale(employeeName, amount, command);
          } else {
            speak('Para criar um vale, preciso saber o nome do funcionário e o valor. Por exemplo: "Criar vale de 200 reais para Josemir"');
            addToHistory('LUA', 'Solicitando informações para criar vale');
          }
        } else if (lowerCommand.includes('cliente')) {
          speak('Para cadastrar um cliente, vou abrir o formulário de cadastro.');
          if (onModalOpen) {
            onModalOpen('clientes', { action: 'create' });
          }
        } else if (lowerCommand.includes('funcionário') || lowerCommand.includes('funcionario')) {
          speak('Abrindo formulário de cadastro de funcionário.');
          if (onModalOpen) {
            onModalOpen('funcionarios', { action: 'create' });
          }
        } else if (lowerCommand.includes('encomenda')) {
          speak('Iniciando nova encomenda no sistema.');
          if (onModalOpen) {
            onModalOpen('encomendas', { action: 'create' });
          }
        } else {
          speak('O que o senhor gostaria de criar? Cliente, funcionário, vale ou encomenda?');
        }
        return;
      }

      // Comandos de busca e filtro
      if (lowerCommand.includes('buscar') || lowerCommand.includes('procurar') || lowerCommand.includes('mostrar')) {
        await processSearchCommand(command);
        return;
      }

      // Comandos de relatório
      if (lowerCommand.includes('relatório') || lowerCommand.includes('relatorio')) {
        await generateReport(command);
        return;
      }

      // Se nenhum comando foi reconhecido, tentar processar via API
      const apiResponse = await processViaAPI(command);
      if (apiResponse) {
        speak(apiResponse.message);
        addToHistory('LUA', apiResponse.message);
        
        // Se a API retornou uma ação, executá-la
        if (apiResponse.action && onModalOpen) {
          onModalOpen(apiResponse.module, apiResponse.data);
        }
      } else {
        speak('Desculpe senhor, não compreendi o comando. Poderia reformular?');
        addToHistory('LUA', 'Comando não compreendido');
      }
      
    } catch (error) {
      console.error('Erro ao processar comando:', error);
      speak('Ocorreu um erro ao processar o comando. Por favor, tente novamente.');
      addToHistory('LUA', 'Erro ao processar comando');
    } finally {
      isProcessingRef.current = false;
      setTranscript('');
    }
  };

  // Funções auxiliares para processar comandos específicos
  const extractFilters = (command, module) => {
    const filters = {};
    const lowerCommand = command.toLowerCase();
    
    // Extrair nomes de pessoas
    if (module === 'vales') {
      const nameMatch = command.match(/(?:de |para |do |da )([\w\s]+?)(?:\s|$)/i);
      if (nameMatch) {
        filters.employee = nameMatch[1].trim();
      }
    }
    
    // Extrair datas
    if (lowerCommand.includes('hoje')) {
      filters.date = new Date().toISOString().split('T')[0];
    } else if (lowerCommand.includes('ontem')) {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      filters.date = yesterday.toISOString().split('T')[0];
    } else if (lowerCommand.includes('semana')) {
      filters.period = 'week';
    } else if (lowerCommand.includes('mês') || lowerCommand.includes('mes')) {
      filters.period = 'month';
    }
    
    // Extrair status
    if (lowerCommand.includes('pendente')) {
      filters.status = 'pending';
    } else if (lowerCommand.includes('aprovado')) {
      filters.status = 'approved';
    } else if (lowerCommand.includes('pago')) {
      filters.status = 'paid';
    }
    
    return filters;
  };

  const extractEmployeeName = (command) => {
    const nameMatch = command.match(/(?:para |de |do funcionário |da funcionária )([\w\s]+?)(?:\s|,|$)/i);
    return nameMatch ? nameMatch[1].trim() : null;
  };

  const extractAmount = (command) => {
    const amountMatch = command.match(/(?:de |valor de |no valor de )?\s*(?:R\$)?\s*(\d+(?:[.,]\d{1,2})?)/i);
    if (amountMatch) {
      return parseFloat(amountMatch[1].replace(',', '.'));
    }
    return null;
  };

  const createVale = async (employeeName, amount, originalCommand) => {
    try {
      const reason = originalCommand.includes('almoço') ? 'Vale almoço' :
                      originalCommand.includes('transporte') ? 'Vale transporte' :
                      originalCommand.includes('emergência') || originalCommand.includes('emergencia') ? 'Vale emergencial' :
                      'Vale solicitado via IA';
      
      const response = await axios.post('/api/vales/create-via-ai', {
        employee_name: employeeName,
        amount: amount,
        reason: reason
      });
      
      if (response.data.success) {
        speak(`Vale criado com sucesso. ${employeeName || 'Funcionário'} receberá ${amount ? `${amount} reais` : 'o valor solicitado'}.`);
        addToHistory('LUA', `Vale criado: ${employeeName} - R$ ${amount}`);
        
        if (onModalOpen) {
          onModalOpen('vales', { refresh: true });
        }
      } else {
        speak('Não foi possível criar o vale. Verifique os dados e tente novamente.');
        addToHistory('LUA', 'Erro ao criar vale');
      }
    } catch (error) {
      console.error('Erro ao criar vale:', error);
      speak('Ocorreu um erro ao criar o vale. Por favor, tente novamente.');
    }
  };

  const processSearchCommand = async (command) => {
    const lowerCommand = command.toLowerCase();
    
    try {
      if (lowerCommand.includes('vale')) {
        const employeeName = extractEmployeeName(command);
        if (employeeName) {
          const response = await axios.get(`/api/vales/search?employee=${employeeName}`);
          if (response.data.vales && response.data.vales.length > 0) {
            const total = response.data.vales.reduce((sum, v) => sum + v.amount, 0);
            speak(`Encontrei ${response.data.vales.length} vales para ${employeeName}, totalizando ${total} reais.`);
            
            if (onModalOpen) {
              onModalOpen('vales', { employee: employeeName });
            }
          } else {
            speak(`Não encontrei vales para ${employeeName}.`);
          }
        } else {
          speak('De qual funcionário o senhor gostaria de ver os vales?');
        }
      } else if (lowerCommand.includes('cliente')) {
        const nameMatch = command.match(/cliente\s+([\w\s]+?)(?:\s|$)/i);
        if (nameMatch) {
          if (onModalOpen) {
            onModalOpen('clientes', { search: nameMatch[1].trim() });
          }
          speak(`Buscando cliente ${nameMatch[1].trim()}.`);
        }
      } else if (lowerCommand.includes('encomenda') || lowerCommand.includes('pedido')) {
        if (onModalOpen) {
          const filters = extractFilters(command, 'encomendas');
          onModalOpen('encomendas', filters);
        }
        speak('Abrindo encomendas com os filtros solicitados.');
      }
    } catch (error) {
      console.error('Erro na busca:', error);
      speak('Ocorreu um erro durante a busca. Por favor, tente novamente.');
    }
  };

  const generateReport = async (command) => {
    const lowerCommand = command.toLowerCase();
    
    try {
      let reportType = '';
      let period = 'today';
      
      if (lowerCommand.includes('venda')) {
        reportType = 'sales';
      } else if (lowerCommand.includes('estoque')) {
        reportType = 'inventory';
      } else if (lowerCommand.includes('financeiro')) {
        reportType = 'financial';
      } else if (lowerCommand.includes('funcionário') || lowerCommand.includes('funcionario')) {
        reportType = 'employees';
      }
      
      if (lowerCommand.includes('hoje')) {
        period = 'today';
      } else if (lowerCommand.includes('semana')) {
        period = 'week';
      } else if (lowerCommand.includes('mês') || lowerCommand.includes('mes')) {
        period = 'month';
      }
      
      const response = await axios.get(`/api/reports/${reportType}?period=${period}`);
      
      if (response.data.success) {
        speak(`Relatório gerado. ${response.data.summary}`);
        addToHistory('LUA', `Relatório ${reportType} - ${period}`);
        
        if (onModalOpen) {
          onModalOpen('reports', { type: reportType, data: response.data });
        }
      }
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      speak('Não foi possível gerar o relatório no momento.');
    }
  };

  const processViaAPI = async (command) => {
    try {
      const response = await axios.post('/api/lua', {
        message: command,
        context: {
          user: JSON.parse(localStorage.getItem('user') || '{}'),
          timestamp: new Date().toISOString()
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Erro na API da LUA:', error);
      return null;
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Interface compacta/expandida */}
      <div className={`transition-all duration-500 ${!isMinimized ? 'mb-3' : ''}`}>
        {!isMinimized && (
          <div className="bg-gray-800/95 backdrop-blur-lg border border-blue-500/30 rounded-xl p-4 w-80 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-400' : 'bg-gray-400'} animate-pulse`}></div>
                <span className="text-blue-300 font-semibold text-sm">LUA - Assistente IA</span>
              </div>
              <div className="flex gap-1">
                <button
                  onClick={() => setAudioEnabled(!audioEnabled)}
                  className="p-1 text-gray-400 hover:text-white transition-colors"
                  title={audioEnabled ? "Desativar áudio" : "Ativar áudio"}
                >
                  {audioEnabled ? <Volume2 size={14} /> : <VolumeX size={14} />}
                </button>
                <button
                  onClick={() => setIsMinimized(true)}
                  className="p-1 text-gray-400 hover:text-white transition-colors"
                  title="Minimizar"
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Canvas de visualização */}
            <div className="relative w-full h-32 bg-gray-900/50 rounded-lg mb-3 overflow-hidden">
              <canvas 
                ref={canvasRef} 
                className="absolute inset-0 w-full h-full"
                style={{ background: 'radial-gradient(circle at center, rgba(59, 130, 246, 0.1), transparent)' }}
              />
              {particles.map(particle => (
                <div
                  key={particle.id}
                  className="absolute rounded-full animate-pulse"
                  style={{
                    left: `${particle.x}px`,
                    top: `${particle.y}px`,
                    width: `${particle.size}px`,
                    height: `${particle.size}px`,
                    backgroundColor: particle.color,
                    opacity: particle.opacity,
                    transform: 'translate(-50%, -50%)',
                    transition: 'all 0.3s ease-out'
                  }}
                />
              ))}
              
              {/* Indicador central */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className={`relative ${pulseAnimation ? 'animate-ping' : ''}`}>
                  {isActive ? (
                    <Brain className="w-12 h-12 text-blue-400 animate-pulse" />
                  ) : (
                    <Sparkles className="w-12 h-12 text-gray-500" />
                  )}
                </div>
              </div>
              
              {/* Visualizador de áudio */}
              {isListening && (
                <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className="w-1 bg-blue-400 rounded animate-pulse"
                      style={{
                        height: `${Math.random() * 20 + 10}px`,
                        animationDelay: `${i * 0.1}s`
                      }}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Status e transcrição */}
            <div className="space-y-2">
              <div className="text-xs text-gray-400">
                Status: <span className="text-blue-300">{status}</span>
              </div>
              {transcript && (
                <div className="text-xs text-gray-300 bg-gray-900/50 rounded p-2">
                  <span className="text-gray-500">Você disse:</span> {transcript}
                </div>
              )}
            </div>

            {/* Histórico de comandos */}
            {commandHistory.length > 0 && (
              <div className="mt-3 space-y-1 max-h-24 overflow-y-auto">
                {commandHistory.map((item, index) => (
                  <div key={index} className="text-xs text-gray-400">
                    <span className={item.type === 'LUA' ? 'text-blue-400' : 'text-green-400'}>
                      {item.type}:
                    </span> {item.message}
                  </div>
                ))}
              </div>
            )}

            {/* Controles de voz */}
            <div className="mt-3 flex justify-center gap-2">
              <button
                onClick={toggleListening}
                className={`p-2 rounded-full transition-all ${
                  isListening 
                    ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' 
                    : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
                }`}
                disabled={!speechSupported}
                title={isListening ? "Parar escuta" : "Iniciar escuta"}
              >
                {isListening ? <MicOff size={18} /> : <Mic size={18} />}
              </button>
            </div>

            {/* Mensagem de erro se não houver suporte */}
            {!speechSupported && (
              <div className="mt-2 text-xs text-red-400 text-center">
                Reconhecimento de voz não disponível neste navegador.
                Use Chrome, Edge ou Safari.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Botão flutuante compacto */}
      <button
        onClick={() => {
          setIsMinimized(!isMinimized);
          if (isMinimized && !isActive && speechSupported) {
            activateJarvis();
          }
        }}
        className={`
          relative group p-4 rounded-full shadow-lg transition-all duration-300
          ${isActive 
            ? 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600' 
            : 'bg-gray-800 hover:bg-gray-700'
          }
          ${isMinimized ? 'scale-100' : 'scale-90'}
          hover:scale-110
        `}
        title={isMinimized ? "Ativar LUA" : "Minimizar LUA"}
      >
        <div className="relative">
          {isActive ? (
            <Activity className="w-6 h-6 text-white animate-pulse" />
          ) : (
            <Sparkles className="w-6 h-6 text-gray-300 group-hover:text-white" />
          )}
          
          {/* Indicador de status */}
          <div className={`
            absolute -top-1 -right-1 w-3 h-3 rounded-full
            ${isActive ? 'bg-green-400' : 'bg-gray-400'}
            ${isListening ? 'animate-pulse' : ''}
          `} />
        </div>
        
        {/* Tooltip */}
        <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <div className="bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap">
            {isMinimized ? 'Clique para ativar LUA' : 'Assistente ativa'}
          </div>
        </div>
      </button>
    </div>
  );
};

export default JarvisAI;