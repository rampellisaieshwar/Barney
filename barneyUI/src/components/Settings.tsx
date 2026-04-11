import React, { useState, useEffect } from 'react';
import { Key, Globe, Shield, Save, ArrowLeft, Cpu, Zap } from 'lucide-react';
import { cn } from '../lib/utils';
import { api } from '../services/api';

interface SettingsProps {
  theme: 'light' | 'dark';
  onBack: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ theme, onBack }) => {
  const [agentModeEnabled, setAgentModeEnabled] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAgentStatus();
  }, []);

  const fetchAgentStatus = async () => {
    try {
      const data = await api.getAgentModeStatus();
      setAgentModeEnabled(data.agent_mode === 'ON');
    } catch (e) {
      console.error("Failed to fetch agent mode status", e);
    }
  };

  const handleToggleAgentMode = async () => {
    setLoading(true);
    try {
      const data = await api.toggleAgentMode(!agentModeEnabled);
      setAgentModeEnabled(data.agent_mode === 'ON');
    } catch (e) {
      console.error("Failed to toggle agent mode", e);
    } finally {
      setLoading(false);
    }
  };

  const providers = [
    { name: 'Google Gemini', models: ['Gemini 1.5 Pro', 'Gemini 1.5 Flash'] },
    { name: 'Anthropic', models: ['Claude 3.5 Sonnet', 'Claude 3 Opus'] },
    { name: 'OpenAI', models: ['GPT-4o', 'GPT-4 Turbo'] },
    { name: 'Groq', models: ['Llama 3.1 70B', 'Mixtral 8x7B'] },
  ];

  return (
    <div className={cn(
      "flex-1 flex flex-col h-screen transition-colors duration-300",
      theme === 'light' ? "bg-white text-black" : "bg-[#090B1E] text-white"
    )}>
      <header className="h-20 px-10 flex items-center justify-between z-10">
        <div className="flex items-center gap-6">
          <button 
            onClick={onBack}
            className="opacity-30 hover:opacity-100 transition-opacity p-2 hover:bg-gray-500/10 rounded-full"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h2 className="text-lg font-bold tracking-tight">System Configuration</h2>
        </div>
        <button className="bg-azure-radiance text-white px-6 py-2 rounded-2xl text-xs font-bold flex items-center gap-2 hover:bg-azure-radiance/80 transition-colors shadow-lg shadow-azure-radiance/20">
          <Save className="w-3.5 h-3.5" />
          Apply Changes
        </button>
      </header>

      <main className="flex-1 p-10 overflow-y-auto custom-scrollbar">
        <div className="max-w-3xl mx-auto space-y-12 pb-20">
          
          {/* Agent Creation Mode */}
          <section>
            <div className="flex items-center gap-4 mb-8">
              <div className="p-3 bg-amber-500/10 rounded-2xl">
                <Zap className={cn("w-5 h-5 text-amber-500", agentModeEnabled && "animate-pulse")} />
              </div>
              <div>
                <h3 className="font-bold text-xl tracking-tight">Autonomous Agent Mode</h3>
                <p className="opacity-40 text-sm">Allow Barney to dynamically build and execute external API tools.</p>
              </div>
            </div>

            <div className={cn(
                  "border rounded-3xl p-8 transition-colors flex items-center justify-between",
                  theme === 'light' ? "bg-gray-50 border-gray-100" : "bg-white/5 border-white/5"
                )}>
              <div className="max-w-md">
                <h5 className="font-bold">Dynamic Tool Building</h5>
                <p className="opacity-40 text-xs mt-1">When enabled, Barney will request and store credentials to satisfy complex requests using external services (Weather, News, Finance).</p>
              </div>
              <div 
                onClick={!loading ? handleToggleAgentMode : undefined}
                className={cn(
                  "w-12 h-6 rounded-full relative transition-all duration-300 cursor-pointer",
                  agentModeEnabled ? "bg-amber-500" : "bg-gray-500/20",
                  loading && "opacity-50 cursor-not-allowed"
                )}
              >
                <div className={cn(
                  "absolute top-1 w-4 h-4 bg-white rounded-full transition-all duration-300",
                  agentModeEnabled ? "right-1" : "left-1"
                )} />
              </div>
            </div>
          </section>
          
          {/* Engine Config */}
          <section>
            <div className="flex items-center gap-4 mb-8">
              <div className="p-3 bg-azure-radiance/10 rounded-2xl">
                <Globe className="w-5 h-5 text-azure-radiance" />
              </div>
              <div>
                <h3 className="font-bold text-xl tracking-tight">Intelligence Engines</h3>
                <p className="opacity-40 text-sm">Configure primary LLM providers and model routing.</p>
              </div>
            </div>

            <div className="space-y-4">
              {providers.map((provider) => (
                <div key={provider.name} className={cn(
                  "border rounded-3xl p-8 transition-colors",
                  theme === 'light' ? "bg-gray-50 border-gray-100" : "bg-white/5 border-white/5"
                )}>
                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                       <Cpu className="w-4 h-4 opacity-40" />
                       <h4 className="font-bold text-lg">{provider.name}</h4>
                    </div>
                    <div className="flex items-center gap-2">
                       <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                       <span className="text-[10px] opacity-30 font-bold uppercase tracking-widest">Active</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-3">
                      <label className="text-[10px] opacity-40 font-bold uppercase tracking-widest ml-1">Authentication Key</label>
                      <div className="relative">
                        <Key className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 opacity-20" />
                        <input 
                          type="password" 
                          placeholder="••••••••••••••••"
                          className={cn(
                            "w-full border rounded-2xl pl-12 pr-4 py-3.5 text-sm outline-none transition-all",
                            theme === 'light' ? "bg-white border-gray-200 focus:border-azure-radiance" : "bg-black/40 border-white/10 focus:border-azure-radiance/50"
                          )}
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <label className="text-[10px] opacity-40 font-bold uppercase tracking-widest ml-1">Default Model Path</label>
                      <select className={cn(
                         "w-full border rounded-2xl px-5 py-3.5 text-sm outline-none transition-all appearance-none cursor-pointer",
                         theme === 'light' ? "bg-white border-gray-200 focus:border-azure-radiance" : "bg-black/40 border-white/10 focus:border-azure-radiance/50"
                      )}>
                        {provider.models.map(model => (
                          <option key={model} value={model}>{model}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Security */}
          <section>
            <div className="flex items-center gap-4 mb-8">
              <div className="p-3 bg-purple-500/10 rounded-2xl">
                <Shield className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h3 className="font-bold text-xl tracking-tight">Security & Governance</h3>
                <p className="opacity-40 text-sm">System-level isolation and execution protocols.</p>
              </div>
            </div>

            <div className={cn(
              "border rounded-3xl p-8 space-y-8",
              theme === 'light' ? "bg-gray-50 border-gray-100" : "bg-white/5 border-white/5"
            )}>
              <div className="flex items-center justify-between">
                <div>
                  <h5 className="font-bold">Python Sandboxing</h5>
                  <p className="opacity-40 text-xs mt-1">Isolate dynamic code execution in secure containers.</p>
                </div>
                <div className="w-12 h-6 bg-azure-radiance rounded-full relative cursor-pointer">
                  <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                </div>
              </div>
              <div className="flex items-center justify-between opacity-50">
                <div>
                  <h5 className="font-bold">Deep Grounding Enforcement</h5>
                  <p className="opacity-40 text-xs mt-1">Require multi-vector verification for all factual queries.</p>
                </div>
                <div className="w-12 h-6 bg-gray-500/20 rounded-full relative cursor-not-allowed">
                  <div className="absolute left-1 top-1 w-4 h-4 bg-gray-500 rounded-full" />
                </div>
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
};
