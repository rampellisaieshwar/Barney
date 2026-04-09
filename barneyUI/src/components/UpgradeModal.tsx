import React from 'react';
import { X, Check, Zap, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  theme: 'light' | 'dark';
}

export const UpgradeModal: React.FC<UpgradeModalProps> = ({ isOpen, onClose, theme }) => {
  const plans = [
    {
      name: 'FREE',
      price: '$0',
      description: 'For users just getting started with Barney.',
      features: [
        { text: 'Access to all features, with our plagiarism checker', included: false },
        { text: 'Faster response speed', included: false },
        { text: 'Access to beta features like browsing, plugins, and advanced data analysis', included: false },
        { text: 'Free for everyone', included: true },
      ],
      buttonText: 'Current Plan',
      isCurrent: true
    },
    {
      name: 'INDIVIDUALS',
      price: '$36',
      description: 'Ideal for startups and small businesses looking to establish.',
      features: [
        { text: 'Access to all features, with our plagiarism checker', included: true },
        { text: 'Faster response speed', included: true },
        { text: 'Access to beta features like browsing, plugins, and advanced data analysis', included: true },
        { text: 'Live chat support', included: true },
      ],
      buttonText: 'Upgrade',
      isCurrent: false,
      isPopular: true
    },
    {
      name: 'TEAMS',
      price: '$64',
      description: 'Perfect for businesses aiming for a sophisticated user experience.',
      features: [
        { text: 'Access to all features, with our plagiarism checker', included: true },
        { text: 'Faster response speed', included: true },
        { text: 'Access to beta features like browsing, plugins, and advanced data analysis', included: true },
        { text: 'Live chat support', included: true },
      ],
      buttonText: 'Upgrade',
      isCurrent: false
    }
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
          />
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className={cn(
              "relative w-full max-w-5xl rounded-[32px] overflow-hidden shadow-2xl transition-colors duration-300",
              theme === 'light' ? "bg-white" : "bg-[#090B1E] border border-white/10"
            )}
          >
            <div className="p-8 md:p-12">
              <div className="flex items-start justify-between mb-8">
                <div>
                  <h2 className={cn("text-4xl font-bold mb-2", theme === 'light' ? "text-black" : "text-white")}>Upgrade Plans</h2>
                  <p className="text-gray-500">
                    Looking to find out what an upgrade you can get? <span className="underline cursor-pointer">More details</span>
                  </p>
                </div>
                <div className="flex items-center gap-6">
                  <span className="text-azure-radiance text-sm font-bold">Save 30% <span className="text-gray-400 font-normal">with annual</span></span>
                  <button className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-xl border text-sm font-bold",
                    theme === 'light' ? "bg-white border-gray-200" : "bg-white/5 border-white/10"
                  )}>
                    Annually <ChevronDown className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {plans.map((plan, idx) => (
                  <div 
                    key={idx}
                    className={cn(
                      "p-8 rounded-[24px] border flex flex-col relative transition-all",
                      plan.isPopular 
                        ? "border-azure-radiance shadow-lg shadow-azure-radiance/10" 
                        : (theme === 'light' ? "border-gray-100 bg-[#F9FAFC]" : "border-white/5 bg-white/5")
                    )}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-baseline gap-1">
                        <span className={cn("text-4xl font-bold", theme === 'light' ? "text-black" : "text-white")}>{plan.price}</span>
                      </div>
                      <span className={cn(
                        "px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest",
                        plan.isPopular ? "bg-azure-radiance text-white" : "bg-gray-200 text-gray-500"
                      )}>
                        {plan.name}
                      </span>
                    </div>
                    
                    <p className="text-xs text-gray-500 mb-8 leading-relaxed">
                      {plan.description}
                    </p>

                    <div className="flex-1 space-y-4 mb-8">
                      {plan.features.map((feature, fIdx) => (
                        <div key={fIdx} className="flex gap-3">
                          {feature.included ? (
                            <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                          ) : (
                            <X className="w-4 h-4 text-red-400 flex-shrink-0" />
                          )}
                          <span className="text-[11px] leading-tight opacity-70">{feature.text}</span>
                        </div>
                      ))}
                    </div>

                    <button className={cn(
                      "w-full py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all",
                      plan.isPopular 
                        ? "bg-azure-radiance text-white hover:scale-[1.02] shadow-lg shadow-azure-radiance/20" 
                        : (theme === 'light' ? "bg-white border border-gray-200 text-black" : "bg-white/10 text-white")
                    )}>
                      {plan.isPopular && <Zap className="w-3.5 h-3.5 fill-yellow-400 text-yellow-400" />}
                      {plan.buttonText}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
