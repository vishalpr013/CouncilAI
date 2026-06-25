import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import Chart from 'react-apexcharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const getWsUrl = () => {
  if (API_URL.startsWith('https://')) {
    return API_URL.replace('https://', 'wss://') + '/ws';
  } else if (API_URL.startsWith('http://')) {
    return API_URL.replace('http://', 'ws://') + '/ws';
  }
  return 'ws://localhost:8000/ws';
};
import { 
  Search, 
  TrendingUp, 
  ShieldAlert, 
  HelpCircle, 
  Play, 
  RefreshCw, 
  ChevronRight, 
  DollarSign,
  Briefcase,
  Layers,
  FileText
} from 'lucide-react';

export default function App() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [activeNode, setActiveNode] = useState('system'); // system | researcher | analyst | critic | reporter
  
  const [nodes, setNodes] = useState({
    researcher: 'pending',
    analyst: 'pending',
    critic: 'pending',
    reporter: 'pending'
  });

  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('executive');

  const [sliders, setSliders] = useState({
    revenue_growth: 0.10,
    discount_rate: 0.09,
    terminal_multiple: 15.0,
    margin_of_safety: 0.20
  });

  const [recalcResult, setRecalcResult] = useState(null);
  const [recalcLoading, setRecalcLoading] = useState(false);
  const socketRef = useRef(null);
  const [chatMessages, setChatMessages] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  useEffect(() => {
    marked.setOptions({
      gfm: true,
      breaks: true
    });
  }, []);

  const handleRecalculate = async (currentSliders = sliders) => {
    if (!result?.ticker) return;
    setRecalcLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/dcf-recalculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker: result.ticker,
          revenue_growth: parseFloat(currentSliders.revenue_growth),
          discount_rate: parseFloat(currentSliders.discount_rate),
          terminal_multiple: parseFloat(currentSliders.terminal_multiple),
          margin_of_safety: parseFloat(currentSliders.margin_of_safety)
        })
      });
      const data = await response.json();
      if (response.ok) {
        setRecalcResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setRecalcLoading(false);
    }
  };

  useEffect(() => {
    if (result?.dcf_valuation) {
      setSliders({
        revenue_growth: 0.10,
        discount_rate: 0.09,
        terminal_multiple: 15.0,
        margin_of_safety: 0.20
      });
      setRecalcResult(result.dcf_valuation);
    }
  }, [result]);

  const runInvestmentCommittee = (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setResult(null);
    setRecalcResult(null);
    setStatusMessage('Initiating Connection...');
    setActiveNode('system');
    setNodes({
      researcher: 'pending',
      analyst: 'pending',
      critic: 'pending',
      reporter: 'pending'
    });
    setChatMessages([
      {
        id: 'init',
        sender: 'system',
        role: 'System Coordinator',
        text: `Investment Committee session initialized for question: "${question}"`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      }
    ]);

    if (socketRef.current) {
      socketRef.current.close();
    }

    const ws = new WebSocket(getWsUrl());
    socketRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ question }));
    };

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);

      if (payload.type === 'status') {
        setStatusMessage(payload.message);
        setChatMessages(prev => [
          ...prev,
          {
            id: `status-${Date.now()}-${Math.random()}`,
            sender: 'system',
            role: 'System Coordinator',
            text: payload.message,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          }
        ]);
      } else if (payload.type === 'node_update') {
        const { node, output } = payload;
        setActiveNode(node);

        setNodes(prev => ({
          ...prev,
          [node]: 'completed'
        }));

        let role = '';
        let text = '';

        if (node === 'researcher') {
          setNodes(prev => ({ ...prev, analyst: 'active' }));
          setStatusMessage('Analysis node processing financials...');
          if (output.research) {
            role = 'Senior Investment Researcher';
            text = output.research;
          }
        } else if (node === 'analyst') {
          setNodes(prev => ({ ...prev, critic: 'active' }));
          setStatusMessage('Critic node auditing valuation models...');
          if (output.analysis) {
            role = 'Valuation Analyst';
            text = output.analysis;
          }
        } else if (node === 'critic') {
          setNodes(prev => ({ ...prev, reporter: 'active' }));
          setStatusMessage('Synthesizing report...');
          if (output.critique) {
            role = 'Moat & Risk Critic';
            text = output.critique;
          }
        } else if (node === 'reporter') {
          if (output.final_answer) {
            role = 'Committee Chairperson';
            text = output.final_answer;
          }
        }

        if (text) {
          setChatMessages(prev => {
            const filtered = prev.filter(m => m.id !== node);
            return [
              ...filtered,
              {
                id: node,
                sender: node,
                role,
                text,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
              }
            ];
          });
        }

        setResult(prev => ({
          ...prev,
          ...output
        }));
      } else if (payload.type === 'complete') {
        setStatusMessage(payload.message);
        setChatMessages(prev => [
          ...prev,
          {
            id: `complete-${Date.now()}`,
            sender: 'system',
            role: 'System Coordinator',
            text: `Consensus reached: Final report synthesized successfully.`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          }
        ]);
        setLoading(false);
        setActiveNode('system');
        setActiveTab('executive');
        ws.close();
      } else if (payload.type === 'error') {
        setStatusMessage(`Error: ${payload.message}`);
        setChatMessages(prev => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            sender: 'error',
            role: 'System Coordinator',
            text: `Error: ${payload.message}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          }
        ]);
        setLoading(false);
        ws.close();
      }
    };

    ws.onerror = () => {
      setStatusMessage('WebSocket error.');
      setChatMessages(prev => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          sender: 'error',
          role: 'System Coordinator',
          text: 'WebSocket connection error.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        }
      ]);
      setLoading(false);
    };

    ws.onclose = () => {
      setLoading(false);
    };
  };

  const handleSliderChange = (name, val) => {
    const nextSliders = { ...sliders, [name]: parseFloat(val) };
    setSliders(nextSliders);
    handleRecalculate(nextSliders);
  };

  const getChartData = () => {
    if (!result?.raw_financials?.years) return null;
    const fin = result.raw_financials;
    const formatValue = (arr) => arr.map(val => parseFloat((val / 1000000000).toFixed(2)));

    return {
      series: [
        { name: 'Revenue ($B)', data: formatValue(fin.revenue) },
        { name: 'Net Income ($B)', data: formatValue(fin.net_income) },
        { name: 'Free Cash Flow ($B)', data: formatValue(fin.free_cash_flow) }
      ],
      options: {
        chart: {
          type: 'bar',
          background: 'transparent',
          toolbar: { show: false }
        },
        theme: { mode: 'dark' },
        colors: ['#d97736', '#737373', '#a3a3a3'], // Copper, neutral gray, lighter gray
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '50%',
            borderRadius: 2
          }
        },
        dataLabels: { enabled: false },
        stroke: { show: true, width: 2, colors: ['transparent'] },
        xaxis: {
          categories: fin.years,
          labels: { style: { colors: '#737373', fontFamily: 'Outfit' } },
          axisBorder: { show: false },
          axisTicks: { show: false }
        },
        yaxis: {
          labels: { style: { colors: '#737373', fontFamily: 'Outfit' } }
        },
        fill: { opacity: 0.9 },
        tooltip: {
          theme: 'dark',
          y: { formatter: (val) => `$${val}B` }
        },
        grid: {
          borderColor: '#1f1f1f',
          strokeDashArray: 4
        },
        legend: {
          position: 'top',
          horizontalAlign: 'right',
          labels: { colors: '#eaeaea', fontFamily: 'Outfit' }
        }
      }
    };
  };

  const chartData = getChartData();

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 font-sans min-h-screen text-[#eaeaea]">
      
      {/* Dynamic Header Badge detail */}
      <div className="flex justify-between items-center text-[10px] text-neutral-600 uppercase tracking-widest border-b border-neutral-900 pb-4 mb-12">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#d97736]"></span>
          AHMEDABAD, INDIA • 23.0225° N
        </div>
        <div className="font-semibold text-neutral-500">Folio • Index 2026</div>
      </div>

      {/* Main Title branding matching portfolio styling */}
      <header className="mb-14 text-left">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-white mb-4">
          Council<span className="font-serif italic font-normal text-[#d97736]">AI.</span>
        </h1>
        <p className="text-neutral-400 font-light text-base sm:text-lg max-w-2xl leading-relaxed">
          An adversarial investment committee orchestrating <span className="font-serif italic text-white">strategic intelligence</span>, DCF valuations, and independent moat audits.
        </p>
      </header>

      {/* Query/Search Form Area */}
      <section className="border border-neutral-900 bg-neutral-950/20 rounded-xl p-6 sm:p-8 mb-10">
        <form onSubmit={runInvestmentCommittee} className="flex flex-col gap-3">
          <label className="text-[10px] font-semibold text-[#d97736] uppercase tracking-widest flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-[#d97736]"></span>
            Ask the Committee
          </label>
          <div className="flex flex-col sm:flex-row gap-3 w-full">
            <input 
              type="text" 
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              required
              placeholder="e.g., Should Nvidia be a long term investment?" 
              className="flex-1 bg-transparent border border-neutral-800 rounded-lg px-4 py-3.5 text-white placeholder-neutral-600 focus:outline-none focus:border-[#d97736] transition-all text-sm"
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={loading}
              className="px-6 py-3.5 bg-[#d97736] text-black font-semibold rounded-lg hover:bg-[#c25e28] transition-all flex items-center justify-center gap-2 text-sm shrink-0"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-black" />
                  <span className="text-black">Analyzing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-black text-black" />
                  <span className="text-black">Run Committee</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Dynamic visual graph pipeline tracker */}
        {loading && (
          <div className="mt-8 border-t border-neutral-900/60 pt-6">
            <div className="h-1 bg-neutral-900 rounded-full overflow-hidden mb-6">
              <div className="h-full bg-gradient-to-r from-[#d97736] to-[#a3a3a3] w-1/3 animate-[shimmer_1.5s_infinite_linear]" style={{ animation: 'shimmer 1.5s infinite linear' }}></div>
            </div>
            <style>{`
              @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(300%); }
              }
            `}</style>
            
            <div className="flex flex-wrap justify-between items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${activeNode === 'researcher' ? 'bg-[#d97736] animate-pulse' : nodes.researcher === 'completed' ? 'bg-emerald-500' : 'bg-neutral-800'}`}></div>
                <span className={`text-[11px] uppercase tracking-wider ${activeNode === 'researcher' ? 'text-[#d97736] font-semibold' : 'text-neutral-500'}`}>Researcher</span>
              </div>
              <ChevronRight className="w-3 h-3 text-neutral-800 hidden sm:block" />

              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${activeNode === 'analyst' ? 'bg-[#d97736] animate-pulse' : nodes.analyst === 'completed' ? 'bg-emerald-500' : 'bg-neutral-800'}`}></div>
                <span className={`text-[11px] uppercase tracking-wider ${activeNode === 'analyst' ? 'text-[#d97736] font-semibold' : 'text-neutral-500'}`}>Analyst</span>
              </div>
              <ChevronRight className="w-3 h-3 text-neutral-800 hidden sm:block" />

              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${activeNode === 'critic' ? 'bg-[#d97736] animate-pulse' : nodes.critic === 'completed' ? 'bg-emerald-500' : 'bg-neutral-800'}`}></div>
                <span className={`text-[11px] uppercase tracking-wider ${activeNode === 'critic' ? 'text-[#d97736] font-semibold' : 'text-neutral-500'}`}>Critic</span>
              </div>
              <ChevronRight className="w-3 h-3 text-neutral-800 hidden sm:block" />

              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${activeNode === 'reporter' ? 'bg-[#d97736] animate-pulse' : nodes.reporter === 'completed' ? 'bg-emerald-500' : 'bg-neutral-800'}`}></div>
                <span className={`text-[11px] uppercase tracking-wider ${activeNode === 'reporter' ? 'text-[#d97736] font-semibold' : 'text-neutral-500'}`}>Chairperson</span>
              </div>
            </div>
            
            <p className="text-center text-xs text-neutral-400 mt-6 mb-4 italic font-light animate-pulse">{statusMessage}</p>

            {chatMessages.length > 0 && (
              <div className="mt-8 border-t border-neutral-900/60 pt-6">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-[10px] font-semibold text-[#d97736] uppercase tracking-widest flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#d97736] animate-ping"></span>
                    Committee Chat Log (Live)
                  </h4>
                  <span className="text-[9px] text-neutral-600 uppercase tracking-wider">Scroll for updates</span>
                </div>
                <div className="max-h-80 overflow-y-auto space-y-4 pr-2 rounded-lg border border-neutral-900 bg-neutral-950/40 p-4 scrollbar-thin scrollbar-thumb-neutral-800 scrollbar-track-transparent">
                  {chatMessages.map((msg) => (
                    <div key={msg.id} className={`flex gap-3 text-sm leading-relaxed p-3 rounded-lg border ${
                      msg.sender === 'system' ? 'bg-neutral-950/60 border-neutral-900/40' :
                      msg.sender === 'error' ? 'bg-rose-950/10 border-rose-900/20' :
                      'bg-neutral-900/20 border-neutral-900/60'
                    }`}>
                      <div className="flex-1 space-y-1">
                        <div className="flex justify-between items-center border-b border-neutral-900/40 pb-1 mb-2">
                          <div className="flex items-center gap-2">
                            <span className={`font-semibold text-[10px] px-2 py-0.5 rounded uppercase tracking-wider ${
                              msg.sender === 'system' ? 'bg-neutral-900 text-neutral-400' :
                              msg.sender === 'error' ? 'bg-rose-950 text-rose-400' :
                              msg.sender === 'researcher' ? 'bg-amber-950 text-amber-400' :
                              msg.sender === 'analyst' ? 'bg-blue-950 text-blue-400' :
                              msg.sender === 'critic' ? 'bg-rose-950 text-rose-400' :
                              msg.sender === 'reporter' ? 'bg-emerald-950 text-emerald-400' :
                              'bg-neutral-800 text-neutral-300'
                            }`}>
                              {msg.role}
                            </span>
                            <span className="text-[9px] text-neutral-600">{msg.timestamp}</span>
                          </div>
                        </div>
                        {msg.sender === 'system' || msg.sender === 'error' ? (
                          <p className="text-neutral-400 text-xs italic">{msg.text}</p>
                        ) : (
                          <div className="prose prose-sm max-w-none text-neutral-300 text-xs text-left" dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }} />
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Committee Outputs Dashboard Grid */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          
          {/* Detailed Reports (Left 2 columns) */}
          <div className="lg:col-span-2 border border-neutral-900 rounded-xl p-6 sm:p-8 bg-neutral-950/10">
            {/* Minimal tab navigation */}
            <div className="flex gap-1 border-b border-neutral-900 pb-px mb-8 overflow-x-auto scrollbar-none">
              <button 
                onClick={() => setActiveTab('executive')}
                className={`pb-3 px-4 text-xs font-semibold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'executive' ? 'border-[#d97736] text-white' : 'border-transparent text-neutral-500 hover:text-neutral-300'
                }`}
              >
                Executive Consensus
              </button>
              <button 
                onClick={() => setActiveTab('debate')}
                className={`pb-3 px-4 text-xs font-semibold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'debate' ? 'border-[#d97736] text-white' : 'border-transparent text-neutral-500 hover:text-neutral-300'
                }`}
              >
                Committee Chat
              </button>
              <button 
                onClick={() => setActiveTab('research')}
                className={`pb-3 px-4 text-xs font-semibold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'research' ? 'border-[#d97736] text-white' : 'border-transparent text-neutral-500 hover:text-neutral-300'
                }`}
              >
                Researcher Memo
              </button>
              <button 
                onClick={() => setActiveTab('valuation')}
                className={`pb-3 px-4 text-xs font-semibold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'valuation' ? 'border-[#d97736] text-white' : 'border-transparent text-neutral-500 hover:text-neutral-300'
                }`}
              >
                Analyst Thesis
              </button>
              <button 
                onClick={() => setActiveTab('risk')}
                className={`pb-3 px-4 text-xs font-semibold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'risk' ? 'border-[#d97736] text-white' : 'border-transparent text-neutral-500 hover:text-neutral-300'
                }`}
              >
                Risk Critique
              </button>
            </div>

            {/* Markdown Report Render */}
            <div className="prose max-w-none">
              {activeTab === 'executive' && result.final_answer && (
                <div dangerouslySetInnerHTML={{ __html: marked.parse(result.final_answer) }} />
              )}
              {activeTab === 'debate' && (
                <div className="space-y-6 text-left">
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-[#d97736] mb-6 border-b border-neutral-900 pb-3 flex items-center gap-1.5">
                    <FileText className="w-4 h-4" />
                    Committee Debate Transcript
                  </h3>
                  <div className="space-y-4">
                    {chatMessages.map((msg) => (
                      <div key={msg.id} className={`flex gap-3 text-sm leading-relaxed p-4 rounded-lg border ${
                        msg.sender === 'system' ? 'bg-neutral-950/40 border-neutral-900/40' :
                        msg.sender === 'error' ? 'bg-rose-950/10 border-rose-900/20' :
                        'bg-neutral-900/10 border-neutral-900/60'
                      }`}>
                        <div className="flex-1 space-y-1">
                          <div className="flex justify-between items-center border-b border-neutral-900/60 pb-1 mb-3">
                            <div className="flex items-center gap-2">
                              <span className={`font-semibold text-xs px-2.5 py-0.5 rounded uppercase tracking-wider ${
                                msg.sender === 'system' ? 'bg-neutral-900 text-neutral-400' :
                                msg.sender === 'error' ? 'bg-rose-950 text-rose-400' :
                                msg.sender === 'researcher' ? 'bg-amber-950 text-amber-400' :
                                msg.sender === 'analyst' ? 'bg-blue-950 text-blue-400' :
                                msg.sender === 'critic' ? 'bg-rose-950 text-rose-400' :
                                msg.sender === 'reporter' ? 'bg-emerald-950 text-emerald-400' :
                                'bg-neutral-800 text-neutral-300'
                              }`}>
                                {msg.role}
                              </span>
                              <span className="text-[10px] text-neutral-500">{msg.timestamp}</span>
                            </div>
                          </div>
                          {msg.sender === 'system' || msg.sender === 'error' ? (
                            <p className="text-neutral-400 text-xs italic">{msg.text}</p>
                          ) : (
                            <div className="prose max-w-none text-neutral-300 text-xs mt-3" dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }} />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {activeTab === 'research' && result.research && (
                <div dangerouslySetInnerHTML={{ __html: marked.parse(result.research) }} />
              )}
              {activeTab === 'valuation' && result.analysis && (
                <div dangerouslySetInnerHTML={{ __html: marked.parse(result.analysis) }} />
              )}
              {activeTab === 'risk' && result.critique && (
                <div dangerouslySetInnerHTML={{ __html: marked.parse(result.critique) }} />
              )}
            </div>
          </div>

          {/* Interactive Widgets & Charting (Right 1 column) */}
          <div className="space-y-6">
            
            {/* Deterministic DCF Calculator Box */}
            <div className="border border-neutral-900 rounded-xl p-6 bg-neutral-950/20">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-[#d97736] mb-6 flex items-center gap-1.5 border-b border-neutral-900 pb-3">
                <DollarSign className="w-4 h-4" />
                Valuation Engine
              </h3>
              
              <div className="space-y-5">
                <div>
                  <div className="flex justify-between text-xs text-neutral-500 mb-1.5 font-medium">
                    <span>Revenue Growth Rate</span>
                    <span className="text-[#d97736]">{(sliders.revenue_growth * 100).toFixed(0)}%</span>
                  </div>
                  <input 
                    type="range" 
                    min="0.00" 
                    max="0.50" 
                    step="0.01" 
                    value={sliders.revenue_growth} 
                    onChange={(e) => handleSliderChange('revenue_growth', e.target.value)}
                    className="w-full h-1 bg-neutral-900 rounded-lg appearance-none cursor-pointer accent-[#d97736]"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs text-neutral-500 mb-1.5 font-medium">
                    <span>Discount Rate (WACC)</span>
                    <span className="text-[#d97736]">{(sliders.discount_rate * 100).toFixed(0)}%</span>
                  </div>
                  <input 
                    type="range" 
                    min="0.05" 
                    max="0.20" 
                    step="0.01" 
                    value={sliders.discount_rate} 
                    onChange={(e) => handleSliderChange('discount_rate', e.target.value)}
                    className="w-full h-1 bg-neutral-900 rounded-lg appearance-none cursor-pointer accent-[#d97736]"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs text-neutral-500 mb-1.5 font-medium">
                    <span>Terminal FCF Multiple</span>
                    <span className="text-[#d97736]">{sliders.terminal_multiple}x</span>
                  </div>
                  <input 
                    type="range" 
                    min="5.0" 
                    max="30.0" 
                    step="0.5" 
                    value={sliders.terminal_multiple} 
                    onChange={(e) => handleSliderChange('terminal_multiple', e.target.value)}
                    className="w-full h-1 bg-neutral-900 rounded-lg appearance-none cursor-pointer accent-[#d97736]"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs text-neutral-500 mb-1.5 font-medium">
                    <span>Margin of Safety</span>
                    <span className="text-[#d97736]">{(sliders.margin_of_safety * 100).toFixed(0)}%</span>
                  </div>
                  <input 
                    type="range" 
                    min="0.05" 
                    max="0.50" 
                    step="0.05" 
                    value={sliders.margin_of_safety} 
                    onChange={(e) => handleSliderChange('margin_of_safety', e.target.value)}
                    className="w-full h-1 bg-neutral-900 rounded-lg appearance-none cursor-pointer accent-[#d97736]"
                  />
                </div>
              </div>

              {/* DCF Recalc outputs */}
              {recalcResult && (
                <div className="bg-neutral-950 border border-neutral-900/60 mt-6 p-4 rounded-lg space-y-3.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-neutral-500">Current Market Price</span>
                    <span className="font-semibold text-white">${recalcResult.current_price?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-neutral-500">Intrinsic Value Target</span>
                    <span className="font-semibold text-[#eaeaea]">${recalcResult.intrinsic_value?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-neutral-500">Safe Buying Price</span>
                    <span className="font-semibold text-[#d97736]">${recalcResult.buy_price_target?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-xs border-t border-neutral-900/80 pt-3">
                    <span className="text-neutral-500">Committee Signal</span>
                    <span className={`font-semibold uppercase tracking-wider ${
                      recalcResult.valuation_status === 'UNDERVALUED' ? 'text-emerald-500' : 
                      recalcResult.valuation_status === 'OVERVALUED' ? 'text-rose-500' : 'text-amber-500'
                    }`}>
                      {recalcResult.valuation_status}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Historical Ingestion Chart Card */}
            {chartData && (
              <div className="border border-neutral-900 rounded-xl p-6 bg-neutral-950/20">
                <h3 className="text-xs font-semibold uppercase tracking-widest text-[#d97736] mb-6 flex items-center gap-1.5 border-b border-neutral-900 pb-3">
                  <TrendingUp className="w-4 h-4" />
                  Ingested Financials
                </h3>
                <div className="h-64">
                  <Chart 
                    options={chartData.options} 
                    series={chartData.series} 
                    type="bar" 
                    height="100%" 
                  />
                </div>
              </div>
            )}
            
          </div>
        </div>
      )}
    </div>
  );
}
