import React from 'react';
import { Settings as SettingsIcon, Key, Globe, Shield, Save, RefreshCw } from 'lucide-react';

export const Settings: React.FC = () => {
  const providers = [
    { name: 'Google Gemini', models: ['Gemini 1.5 Pro', 'Gemini 1.5 Flash', 'Gemini 1.0 Pro'] },
    { name: 'Anthropic', models: ['Claude 3.5 Sonnet', 'Claude 3 Opus', 'Claude 3 Haiku'] },
    { name: 'OpenAI', models: ['GPT-4o', 'GPT-4 Turbo', 'GPT-3.5 Turbo'] },
    { name: 'Groq', models: ['Llama 3.1 70B', 'Mixtral 8x7B'] },
  ];

  return (
    <div className="flex-1 flex flex-col h-screen bg-[#050506] overflow-hidden">
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-black/20 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <SettingsIcon className="w-5 h-5 text-yellow-400" />
          <h2 className="text-white font-semibold tracking-tight">System Settings</h2>
        </div>
        <button className="bg-yellow-400 text-black px-6 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 hover:bg-yellow-300 transition-colors">
          <Save className="w-3.5 h-3.5" />
          Save Changes
        </button>
      </header>

      <main className="flex-1 p-8 overflow-y-auto custom-scrollbar">
        <div className="max-w-3xl mx-auto space-y-10">
          {/* Provider Config */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <Globe className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <h3 className="text-white font-bold">Multi-Model Engine</h3>
                <p className="text-white/40 text-xs">Configure LLM providers and API credentials.</p>
              </div>
            </div>

            <div className="space-y-4">
              {providers.map((provider) => (
                <div key={provider.name} className="bg-[#0d0d0f] border border-white/5 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h4 className="text-white font-bold">{provider.name}</h4>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-white/30 font-bold uppercase tracking-widest">Status</span>
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-[10px] text-white/40 font-bold uppercase tracking-widest ml-1">API Key</label>
                      <div className="relative">
                        <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" />
                        <input 
                          type="password" 
                          placeholder="••••••••••••••••"
                          className="w-full bg-black/40 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white outline-none focus:border-yellow-400/50 transition-colors"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[10px] text-white/40 font-bold uppercase tracking-widest ml-1">Default Model</label>
                      <select className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white outline-none focus:border-yellow-400/50 transition-colors appearance-none">
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

          {/* Security & System */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                <Shield className="w-4 h-4 text-purple-400" />
              </div>
              <div>
                <h3 className="text-white font-bold">System Security</h3>
                <p className="text-white/40 text-xs">Manage workspace permissions and sandboxing.</p>
              </div>
            </div>

            <div className="bg-[#0d0d0f] border border-white/5 rounded-2xl p-6 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h5 className="text-white text-sm font-bold">Python Sandboxing</h5>
                  <p className="text-white/40 text-[11px]">Execute dynamic code in an isolated environment.</p>
                </div>
                <div className="w-12 h-6 bg-yellow-400 rounded-full relative cursor-pointer">
                  <div className="absolute right-1 top-1 w-4 h-4 bg-black rounded-full" />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h5 className="text-white text-sm font-bold">Auto-Update Tools</h5>
                  <p className="text-white/40 text-[11px]">Automatically fetch missing Python libraries from PyPI.</p>
                </div>
                <div className="w-12 h-6 bg-white/10 rounded-full relative cursor-pointer">
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white/40 rounded-full" />
                </div>
              </div>
            </div>
          </section>

          <div className="pt-10 flex items-center justify-center gap-4">
            <button className="text-white/20 hover:text-white/40 text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 transition-colors">
              <RefreshCw className="w-3 h-3" />
              Reset System Defaults
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
