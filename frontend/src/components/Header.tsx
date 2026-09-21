import React from 'react';
import { PenTool, Settings as SettingsIcon, Sparkles, UserCheck } from 'lucide-react';

interface HeaderProps {
  user: {
    first_name: string;
    username?: string;
  };
  onOpenCalibration: () => void;
  onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  user,
  onOpenCalibration,
  onOpenSettings
}) => {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="flex items-center space-x-2.5">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <PenTool className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center space-x-1.5">
            <h1 className="text-base font-bold text-slate-800 leading-tight">Конспект Studio</h1>
            <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-blue-100 text-blue-700">
              <Sparkles className="w-2.5 h-2.5 mr-0.5" /> AI Gemini
            </span>
          </div>
          <p className="text-xs text-slate-500 font-medium">Привет, {user.first_name}!</p>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={onOpenCalibration}
          className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 active:scale-95 text-slate-700 transition border border-slate-200"
        >
          <UserCheck className="w-3.5 h-3.5 text-blue-600" />
          <span>Почерк</span>
        </button>

        <button
          onClick={onOpenSettings}
          className="p-1.5 rounded-lg text-slate-600 hover:bg-slate-100 active:scale-95 transition"
          aria-label="Настройки"
        >
          <SettingsIcon className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
