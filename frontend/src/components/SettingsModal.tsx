import React, { useState } from 'react';
import { X, Key, Database, Bot, Check, ExternalLink } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  geminiKey: string;
  setGeminiKey: (k: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  geminiKey,
  setGeminiKey
}) => {
  const [localKey, setLocalKey] = useState(geminiKey);
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setGeminiKey(localKey);
    localStorage.setItem('user_gemini_api_key', localKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl max-w-md w-full p-5 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h2 className="text-base font-bold text-slate-800">Настройки</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4 text-xs">
          {/* Gemini API Key */}
          <div>
            <label className="flex items-center space-x-1.5 font-semibold text-slate-700 mb-1.5">
              <Key className="w-3.5 h-3.5 text-blue-600" />
              <span>Личный ключ Google Gemini API:</span>
            </label>
            <input
              type="password"
              value={localKey}
              onChange={(e) => setLocalKey(e.target.value)}
              placeholder="AIzaSy... (необязательно, используется серверный)"
              className="w-full p-2.5 rounded-xl border border-slate-200 focus:border-blue-500 outline-none text-xs font-mono text-slate-800"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Бесплатный ключ можно взять в <a href="https://aistudio.google.com" target="_blank" rel="noreferrer" className="text-blue-600 underline">Google AI Studio</a>. Если поле пустое, действует серверный ключ.
            </p>
            <button
              onClick={handleSave}
              className="mt-2 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center space-x-1 transition"
            >
              {saved ? <Check className="w-3.5 h-3.5" /> : null}
              <span>{saved ? 'Сохранено!' : 'Сохранить ключ'}</span>
            </button>
          </div>

          {/* Cloud Info */}
          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-emerald-600" />
                <span className="font-semibold text-slate-700">База данных Supabase</span>
              </div>
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-semibold text-[10px]">
                tgapp: Active
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4 text-blue-600" />
                <span className="font-semibold text-slate-700">Telegram Bot</span>
              </div>
              <span className="text-slate-500 font-mono text-[10px]">
                @ConspectusBot
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
        >
          Готово
        </button>
      </div>
    </div>
  );
};
