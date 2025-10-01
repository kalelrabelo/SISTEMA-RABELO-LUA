import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Gem, Menu, Search, Bell, User, Settings, DollarSign, Package, Users, FileText, LogOut, LayoutDashboard, Diamond, HandCoins, ShoppingBag, FolderOpen, ChevronDown, ChevronUp, AlertTriangle, Activity, Brain, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import axios from 'axios'
import './App.css'

// Importar componentes
import Login from './components/Login.jsx'
import NetflixLogin from './components/NetflixLogin.jsx'
import Clientes from './components/Clientes.jsx';
import Funcionarios from './components/Funcionarios.jsx';
import FuncionariosEnhanced from './components/FuncionariosEnhanced.jsx';
import Padroes from './components/Padroes.jsx';
import JoiasMaterial from './components/JoiasMaterial.jsx';
import JoiasEnhanced from './components/JoiasEnhanced.jsx';
import Materiais from './components/Materiais.jsx';
import JoiasMateriaisPedrasRel from './components/JoiasMateriaisPedrasRel.jsx';
import JoiasPedras from './components/JoiasPedras.jsx';
import JoiasTamanhos from './components/JoiasTamanhos.jsx';
import Caixa from './components/Caixa.jsx';
import Custos from './components/Custos.jsx';
import Descontos from './components/Descontos.jsx';
import Entradas from './components/Entradas.jsx';
import Impostos from './components/Impostos.jsx';
import Vales from './components/Vales.jsx';
import FolhaPagamento from './components/FolhaPagamento.jsx';
import Pagamentos from './components/Pagamentos.jsx';
import Prazos from './components/Prazos.jsx';
import Encomendas from './components/Encomendas.jsx';
import EncomendasJoias from './components/EncomendasJoias.jsx';
import Estoque from './components/Estoque.jsx';
import EstoqueFiltros from './components/EstoqueFiltros.jsx';
import Cartas from './components/Cartas.jsx';
import Notas from './components/Notas.jsx';
import ErrosAoColar from './components/ErrosAoColar.jsx';
import ErrorLogger from './components/ErrorLogger.jsx';
import errorLogger from './services/errorLogger.js';
import JarvisAI from './components/JarvisAI.jsx';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [expandedSections, setExpandedSections] = useState({
    administracao: false,
    catalogo: false,
    financeiro: false,
    vendas: false,
    outros: false
  })

  // Verificar autenticação ao carregar o app
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');

      if (storedToken && storedUser) {
        try {
          // Configurar axios com token padrão
          axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;

          // Verificar se o token ainda é válido
          const response = await fetch('http://localhost:5000/api/verify-token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${storedToken}`,
            },
            body: JSON.stringify({ token: storedToken }),
          });

          const data = await response.json();

          if (response.ok && data.valid) {
            setIsAuthenticated(true);
            setUser(JSON.parse(storedUser));
            setToken(storedToken);
          } else {
            // Token inválido, remover do localStorage
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setIsAuthenticated(false);
          }
        } catch (error) {
          console.error('Erro na verificação do token:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setIsAuthenticated(false);
        }
      }

      setLoading(false);
    };

    checkAuth();
  }, []);

  const handleLogin = (userData, token) => {
    setIsAuthenticated(true)
    setUser(userData)
    setToken(token)
    
    // Configurar axios com o token correto
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setIsAuthenticated(false)
    setUser(null)
    setToken(null)
    setCurrentPage('dashboard')
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    {
      id: 'administracao', 
      label: 'Administração', 
      icon: Users,
      children: [
        { id: 'clientes', label: 'Clientes', icon: Users },
        { id: 'funcionarios', label: 'Funcionários', icon: Users }
      ]
    },
    {
      id: 'catalogo',
      label: 'Catálogo',
      icon: Package,
      children: [
        { id: 'joias', label: 'Joias', icon: Diamond },
        { id: 'materiais', label: 'Materiais', icon: Package },
        { id: 'pedras', label: 'Pedras', icon: Gem },
        { id: 'tamanhos', label: 'Tamanhos', icon: Package },
        { id: 'padroes', label: 'Padrões', icon: Diamond },

      ]
    },
    {
      id: 'financeiro',
      label: 'Financeiro',
      icon: DollarSign,
      children: [
        { id: 'caixa', label: 'Caixa', icon: DollarSign },
        { id: 'custos', label: 'Custos', icon: HandCoins },

        { id: 'entradas', label: 'Entradas', icon: DollarSign },
        { id: 'impostos', label: 'Impostos', icon: FileText },
        { id: 'vales', label: 'Vales', icon: HandCoins },
        { id: 'folha-pagamento', label: 'Folha de Pagamento', icon: Users },
        { id: 'pagamentos', label: 'Pagamentos', icon: DollarSign },

      ]
    },
    {
      id: 'vendas',
      label: 'Vendas/Estoque',
      icon: ShoppingBag,
      children: [
        { id: 'encomendas', label: 'Encomendas', icon: ShoppingBag },
        { id: 'encomendas-joias', label: 'Encomendas de Joias', icon: Diamond },
        { id: 'estoque', label: 'Estoque', icon: Package },
        { id: 'estoque-filtros', label: 'Filtros de Estoque', icon: Settings }
      ]
    },
    {
      id: 'outros',
      label: 'Outros',
      icon: FolderOpen,
      children: [
        { id: 'cartas', label: 'Cartas', icon: FileText },
        { id: 'notas', label: 'Notas', icon: FileText },
        { id: 'erros', label: 'Erros ao Colar', icon: Settings },
        { id: 'log-erros', label: 'Log de Erros', icon: AlertTriangle }
      ]
    }
  ]

  const renderContent = () => {
    switch (currentPage) {
      case 'clientes':
        return <Clientes />
      case 'funcionarios':
        return <FuncionariosEnhanced />
      case 'padroes':
        return <Padroes />
      case 'joias':
        return <JoiasEnhanced />
      case 'materiais':
        return <Materiais />
      case 'pedras':
        return <JoiasPedras />
      case 'tamanhos':
        return <JoiasTamanhos />

      case 'caixa':
        return <Caixa />
      case 'custos':
        return <Custos />

      case 'entradas':
        return <Entradas />
      case 'impostos':
        return <Impostos />
      case 'vales':
        return <Vales />
      case 'folha-pagamento':
        return <FolhaPagamento />
      case 'pagamentos':
        return <Pagamentos />

      case 'encomendas':
        return <Encomendas />
      case 'encomendas-joias':
        return <EncomendasJoias />
      case 'estoque':
        return <Estoque />
      case 'estoque-filtros':
        return <EstoqueFiltros />
      case 'cartas':
        return <Cartas />
      case 'notas':
        return <Notas />
      case 'erros':
        return <ErrosAoColar />
      case 'log-erros':
        return <ErrorLogger />
      default:
        return <Dashboard />
    }
  }

  // Dashboard Component
  const Dashboard = () => {
    const dashboardData = {
      vendas: [
        { mes: 'Jan', valor: 65000 },
        { mes: 'Fev', valor: 59000 },
        { mes: 'Mar', valor: 80000 },
        { mes: 'Abr', valor: 81000 },
        { mes: 'Mai', valor: 56000 },
        { mes: 'Jun', valor: 75000 },
      ],
      categorias: [
        { nome: 'Anéis', valor: 35, cor: '#8884d8' },
        { nome: 'Colares', valor: 25, cor: '#82ca9d' },
        { nome: 'Brincos', valor: 20, cor: '#ffc658' },
        { nome: 'Pulseiras', valor: 20, cor: '#ff7300' },
      ]
    }

    return (
      <div className="p-6 space-y-6 relative">
        {/* Background futurista */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/5 via-purple-900/5 to-cyan-900/5 pointer-events-none"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/10 via-transparent to-transparent pointer-events-none"></div>
        
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Centro de Comando
              </h1>
              <p className="text-gray-300 text-lg mt-2">
                Bem-vindo, {user?.username || 'Usuário'}! 🚀
              </p>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-400">Sistema Online - LUA Disponível</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-mono text-cyan-400">
                {new Date().toLocaleTimeString('pt-BR')}
              </div>
              <div className="text-sm text-gray-400">
                {new Date().toLocaleDateString('pt-BR', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Cards de estatísticas futuristas */}
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 border border-green-500/30 backdrop-blur-sm hover:border-green-500/50 transition-all duration-300 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-400 text-sm flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    Vendas do Mês
                  </div>
                  <p className="text-2xl font-bold text-green-400 font-mono">R$ 75.000</p>
                  <p className="text-xs text-green-300/60 mt-1">↑ 12% vs mês anterior</p>
                </div>
                <div className="relative">
                  <div className="absolute inset-0 bg-green-500/20 rounded-full animate-ping"></div>
                  <DollarSign className="h-8 w-8 text-green-400 relative z-10 group-hover:scale-110 transition-transform" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 border border-blue-500/30 backdrop-blur-sm hover:border-blue-500/50 transition-all duration-300 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-400 text-sm flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                    Peças em Estoque
                  </div>
                  <p className="text-2xl font-bold text-blue-400 font-mono">1,234</p>
                  <p className="text-xs text-blue-300/60 mt-1">Crítico: 23 itens</p>
                </div>
                <div className="relative">
                  <div className="absolute inset-0 bg-blue-500/20 rounded-full animate-ping"></div>
                  <Package className="h-8 w-8 text-blue-400 relative z-10 group-hover:scale-110 transition-transform" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 border border-purple-500/30 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-400 text-sm flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                    Clientes Ativos
                  </div>
                  <p className="text-2xl font-bold text-purple-400 font-mono">89</p>
                  <p className="text-xs text-purple-300/60 mt-1">+5 novos hoje</p>
                </div>
                <div className="relative">
                  <div className="absolute inset-0 bg-purple-500/20 rounded-full animate-ping"></div>
                  <Users className="h-8 w-8 text-purple-400 relative z-10 group-hover:scale-110 transition-transform" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 border border-orange-500/30 backdrop-blur-sm hover:border-orange-500/50 transition-all duration-300 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-400 text-sm flex items-center gap-2">
                    <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                    Encomendas
                  </div>
                  <p className="text-2xl font-bold text-orange-400 font-mono">15</p>
                  <p className="text-xs text-orange-300/60 mt-1">3 urgentes</p>
                </div>
                <div className="relative">
                  <div className="absolute inset-0 bg-orange-500/20 rounded-full animate-ping"></div>
                  <ShoppingBag className="h-8 w-8 text-orange-400 relative z-10 group-hover:scale-110 transition-transform" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Painel de Análises Avançadas */}
        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-cyan-500/30 backdrop-blur-sm">
            <CardHeader className="border-b border-cyan-500/20">
              <CardTitle className="text-cyan-400 flex items-center gap-3">
                <Activity className="h-5 w-5 animate-pulse" />
                Análise de Performance - Vendas Mensais
              </CardTitle>
              <CardDescription className="text-gray-300">
                Monitoramento em tempo real dos indicadores de vendas
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dashboardData.vendas}>
                  <CartesianGrid strokeDasharray="1 1" stroke="#1F2937" opacity={0.3} />
                  <XAxis 
                    dataKey="mes" 
                    stroke="#22D3EE" 
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="#22D3EE" 
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `R$ ${(value/1000).toFixed(0)}k`}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(15, 23, 42, 0.95)', 
                      border: '1px solid rgba(34, 211, 238, 0.3)',
                      borderRadius: '12px',
                      backdropFilter: 'blur(8px)',
                      color: '#22D3EE'
                    }}
                    formatter={(value) => [`R$ ${value.toLocaleString('pt-BR')}`, 'Vendas']}
                  />
                  <Bar 
                    dataKey="valor" 
                    fill="url(#gradient1)" 
                    radius={[4, 4, 0, 0]}
                  />
                  <defs>
                    <linearGradient id="gradient1" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#22D3EE" />
                      <stop offset="100%" stopColor="#0891B2" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-purple-500/30 backdrop-blur-sm">
            <CardHeader className="border-b border-purple-500/20">
              <CardTitle className="text-purple-400 flex items-center gap-3">
                <Zap className="h-5 w-5 animate-pulse" />
                Distribuição de Categorias
              </CardTitle>
              <CardDescription className="text-gray-300">
                Análise da participação por tipo de produto
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={dashboardData.categorias}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="valor"
                    label={({ nome, valor }) => `${nome}: ${valor}%`}
                    labelLine={false}
                  >
                    {dashboardData.categorias.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={[
                          '#8B5CF6', // Roxo
                          '#22D3EE', // Ciano 
                          '#F59E0B', // Âmbar
                          '#EF4444'  // Vermelho
                        ][index]} 
                        stroke={[
                          '#8B5CF6', 
                          '#22D3EE', 
                          '#F59E0B', 
                          '#EF4444'
                        ][index]}
                        strokeWidth={2}
                      />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(15, 23, 42, 0.95)', 
                      border: '1px solid rgba(139, 92, 246, 0.3)',
                      borderRadius: '12px',
                      backdropFilter: 'blur(8px)',
                      color: '#A855F7'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
        
        {/* Painel de Comandos Rápidos */}
        <div className="relative z-10 mt-8">
          <Card className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-blue-500/30 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-blue-400 flex items-center gap-3">
                <Brain className="h-5 w-5 animate-pulse" />
                Centro de Comando LUA
              </CardTitle>
              <CardDescription className="text-gray-300">
                Diga "Lua" para ativar a assistente por voz ou clique nos atalhos abaixo
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {[
                  { id: 'clientes', label: 'Clientes', icon: Users, color: 'text-green-400 border-green-500/30 hover:border-green-500/50' },
                  { id: 'joias', label: 'Joias', icon: Diamond, color: 'text-blue-400 border-blue-500/30 hover:border-blue-500/50' },
                  { id: 'vales', label: 'Vales', icon: HandCoins, color: 'text-purple-400 border-purple-500/30 hover:border-purple-500/50' },
                  { id: 'estoque', label: 'Estoque', icon: Package, color: 'text-orange-400 border-orange-500/30 hover:border-orange-500/50' },
                  { id: 'caixa', label: 'Caixa', icon: DollarSign, color: 'text-cyan-400 border-cyan-500/30 hover:border-cyan-500/50' },
                  { id: 'funcionarios', label: 'Funcionários', icon: Users, color: 'text-pink-400 border-pink-500/30 hover:border-pink-500/50' },
                ].map((item) => {
                  const IconComponent = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setCurrentPage(item.id)}
                      className={`p-4 border rounded-xl backdrop-blur-sm transition-all duration-300 hover:scale-105 group ${item.color}`}
                    >
                      <IconComponent className="h-6 w-6 mx-auto mb-2 group-hover:scale-110 transition-transform" />
                      <div className="text-sm font-medium">{item.label}</div>
                    </button>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Gem className="h-16 w-16 text-purple-500 mx-auto animate-spin" />
          <p className="text-white mt-4">Carregando...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <NetflixLogin onLogin={handleLogin} />
  }

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gray-800 border-r border-gray-700 transition-all duration-300 flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
              <Gem className="h-6 w-6 text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-white font-bold">Antonio Rabelo</h1>
                <p className="text-gray-400 text-xs">ERP Joalheria</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {menuItems.map((item) => {
            if (item.children) {
              return (
                <div key={item.id}>
                  <button
                    onClick={() => toggleSection(item.id)}
                    className="w-full flex items-center justify-between p-3 text-gray-300 hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {(() => {
                        const ItemIconComponent = item.icon;
                        return <ItemIconComponent className="h-5 w-5" />;
                      })()}
                      {sidebarOpen && <span>{item.label}</span>}
                    </div>
                    {sidebarOpen && (
                      expandedSections[item.id] ? 
                        <ChevronUp className="h-4 w-4" /> : 
                        <ChevronDown className="h-4 w-4" />
                    )}
                  </button>

                  {expandedSections[item.id] && sidebarOpen && (
                    <div className="ml-6 space-y-1">
                      {item.children.map((child) => {
                        const ChildIconComponent = child.icon;
                        return (
                          <button
                            key={child.id}
                            onClick={() => setCurrentPage(child.id)}
                            className={`w-full flex items-center gap-3 p-2 text-sm rounded-lg transition-colors ${
                              currentPage === child.id 
                                ? 'bg-purple-600 text-white' 
                                : 'text-gray-300 hover:bg-gray-700'
                            }`}
                          >
                            <ChildIconComponent className="h-4 w-4" />
                            <span>{child.label}</span>
                          </button>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            }

            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                  currentPage === item.id 
                    ? 'bg-purple-600 text-white' 
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                {(() => {
                  const ItemIconComponent = item.icon;
                  return <ItemIconComponent className="h-5 w-5" />;
                })()}
                {sidebarOpen && <span>{item.label}</span>}
              </button>
            )
          })}
        </nav>

        {/* User Info */}
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-700 rounded-lg">
              <User className="h-4 w-4 text-gray-300" />
            </div>
            {sidebarOpen && (
              <div className="flex-1">
                <p className="text-white text-sm font-medium">{user?.username}</p>
                <p className="text-gray-400 text-xs">{user?.email}</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-red-400 transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleSidebar}
                className="text-gray-300 hover:text-white hover:bg-gray-700"
              >
                <Menu className="h-5 w-5" />
              </Button>

              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Pesquisar..."
                    className="pl-10 w-64 bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                className="text-gray-300 hover:text-white hover:bg-gray-700 relative"
              >
                <Bell className="h-5 w-5" />
                <Badge className="absolute -top-2 -right-2 h-5 w-5 rounded-full bg-red-500 text-xs">
                  3
                </Badge>
              </Button>

              <Button
                variant="ghost"
                size="sm"
                className="text-gray-300 hover:text-white hover:bg-gray-700"
              >
                <Settings className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto bg-gray-900">
          {renderContent()}
          
          {/* Jarvis AI Assistant */}
          <JarvisAI onCommand={(page) => setCurrentPage(page)} />
        </main>
      </div>
    </div>
  )
}

export default App
