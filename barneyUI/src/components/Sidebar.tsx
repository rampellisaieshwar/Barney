import React from 'react';
import { 
  MessageSquare, 
  FolderOpen, 
  LayoutTemplate, 
  FileText, 
  Users, 
  History, 
  Settings as SettingsIcon, 
  HelpCircle,
  Search,
  Plus,
  Sun,
  Moon,
  LayoutGrid,
  ShieldCheck,
  Brain
} from 'lucide-react';
import { View } from '../types';
import { cn } from '../lib/utils';

interface SidebarProps {
  currentView: View;
  onViewChange: (view: View) => void;
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange, theme, onThemeToggle }) => {
  const menuItems: { id: string; label: string; icon: any; badge?: string }[] = [
    { id: 'console', label: 'AI Chat', icon: MessageSquare },
    { id: 'governance', label: 'Governance', icon: ShieldCheck, badge: 'HITL' },
    { id: 'memory', label: 'Memory & Insights', icon: Brain },
    { id: 'registry', label: 'Projects', icon: FolderOpen },
    { id: 'templates', label: 'Templates', icon: LayoutTemplate },
    { id: 'documents', label: 'Documents', icon: FileText },
  ];

  const secondaryItems = [
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
    { id: 'help', label: 'Help', icon: HelpCircle },
  ] as const;

  return (
    <div className={cn(
      "w-64 h-screen flex flex-col p-4 border-r transition-colors duration-300",
      theme === 'light' ? "bg-[#F9FAFC] border-gray-200" : "bg-[#090B1E] border-white/5"
    )}>
      {/* Logo */}
      <div className="flex items-center justify-between px-2 mb-6">
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-8 h-8 rounded-lg flex items-center justify-center",
            theme === 'light' ? "bg-black text-white" : "bg-white text-black"
          )}>
            <LayoutGrid className="w-5 h-5" />
          </div>
          <span className={cn("font-bold text-xl", theme === 'light' ? "text-black" : "text-white")}>Barney</span>
        </div>
        <button className={cn("p-1.5 rounded-lg", theme === 'light' ? "hover:bg-gray-200" : "hover:bg-white/5")}>
          <LayoutGrid className="w-4 h-4 opacity-50" />
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 opacity-30" />
        <input 
          type="text" 
          placeholder="Search" 
          className={cn(
            "w-full pl-10 pr-4 py-2 rounded-xl text-sm outline-none transition-all",
            theme === 'light' 
              ? "bg-white border border-gray-200 focus:border-azure-radiance" 
              : "bg-white/5 border border-white/10 focus:border-azure-radiance/50"
          )}
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] opacity-30 font-mono">⌘K</span>
      </div>

      {/* Main Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto custom-scrollbar pr-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onViewChange(item.id as View)}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative",
              currentView === item.id 
                ? (theme === 'light' ? "bg-white shadow-sm text-azure-radiance" : "bg-white/10 text-white")
                : (theme === 'light' ? "text-gray-500 hover:bg-white" : "text-white/50 hover:bg-white/5")
            )}
          >
            {currentView === item.id && (
              <div className="absolute left-0 w-1 h-4 bg-azure-radiance rounded-full" />
            )}
            <item.icon className="w-5 h-5" />
            <span className="font-medium text-sm flex-1 text-left">{item.label}</span>
            {item.badge && (
              <span className="bg-azure-radiance text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md">
                {item.badge}
              </span>
            )}
            {item.id === 'documents' && (
              <Plus className="w-4 h-4 opacity-30 group-hover:opacity-100" />
            )}
          </button>
        ))}

        <div className="pt-4 pb-2">
          <p className="px-3 text-[10px] font-bold uppercase tracking-widest opacity-30 mb-2">Settings & Help</p>
          {secondaryItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id as View)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200",
                currentView === item.id 
                  ? (theme === 'light' ? "bg-white shadow-sm text-azure-radiance" : "bg-white/10 text-white")
                  : (theme === 'light' ? "text-gray-500 hover:bg-white" : "text-white/50 hover:bg-white/5")
              )}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium text-sm flex-1 text-left">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Bottom Controls */}
      <div className="mt-auto pt-4 space-y-4">
        {/* Theme Toggle */}
        <div className={cn(
          "p-1 rounded-xl flex items-center gap-1",
          theme === 'light' ? "bg-gray-200/50" : "bg-white/5"
        )}>
          <button 
            onClick={() => theme !== 'light' && onThemeToggle()}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-1.5 rounded-lg text-xs font-bold transition-all",
              theme === 'light' ? "bg-white shadow-sm text-black" : "text-white/40 hover:text-white"
            )}
          >
            <Sun className="w-3.5 h-3.5" />
            Light
          </button>
          <button 
            onClick={() => theme !== 'dark' && onThemeToggle()}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-1.5 rounded-lg text-xs font-bold transition-all",
              theme === 'dark' ? "bg-white/10 text-white" : "text-black/40 hover:text-black"
            )}
          >
            <Moon className="w-3.5 h-3.5" />
            Dark
          </button>
        </div>

        {/* User Profile */}
        <div className={cn(
          "flex items-center gap-3 p-2 rounded-2xl border transition-colors",
          theme === 'light' ? "border-gray-200 hover:bg-white" : "border-white/5 hover:bg-white/5"
        )}>
          <img 
            src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop" 
            alt="User" 
            className="w-10 h-10 rounded-xl object-cover"
            referrerPolicy="no-referrer"
          />
          <div className="flex-1 min-w-0">
            <p className={cn("text-sm font-bold truncate", theme === 'light' ? "text-black" : "text-white")}>Emilia Caitlin</p>
            <p className="text-[10px] opacity-40 truncate">hey@unspace.agency</p>
          </div>
        </div>
      </div>
    </div>
  );
};
