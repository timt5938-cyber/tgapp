import React from 'react';
import { Sliders, Palette, FileSpreadsheet, Check } from 'lucide-react';
import { PresetsResponse } from '../api/client';

interface NotebookCustomizerProps {
  presetsData: PresetsResponse | null;
  paperStyle: string;
  setPaperStyle: (s: string) => void;
  hasMargins: boolean;
  setHasMargins: (m: boolean) => void;
  penColor: string;
  setPenColor: (c: string) => void;
  fontPreset: string;
  setFontPreset: (f: string) => void;
  jitter: number;
  setJitter: (j: number) => void;
  slant: number;
  setSlant: (s: number) => void;
  humanize: boolean;
  setHumanize: (h: boolean) => void;
}

export const NotebookCustomizer: React.FC<NotebookCustomizerProps> = ({
  presetsData,
  paperStyle,
  setPaperStyle,
  hasMargins,
  setHasMargins,
  penColor,
  setPenColor,
  fontPreset,
  setFontPreset,
  jitter,
  setJitter,
  slant,
  setSlant,
  humanize,
  setHumanize
}) => {
  return (
    <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <div className="flex items-center space-x-2 text-slate-800 font-bold text-sm">
          <Sliders className="w-4 h-4 text-blue-600" />
          <span>Настройки тетради и почерка</span>
        </div>
      </div>

      {/* Handwriting preset selector */}
      <div>
        <label className="block text-xs font-semibold text-slate-600 mb-1.5">
          Стиль почерка:
        </label>
        <div className="grid grid-cols-2 gap-2">
          {presetsData?.presets.map((preset) => {
            const isSelected = fontPreset === preset.id;
            return (
              <button
                key={preset.id}
                onClick={() => setFontPreset(preset.id)}
                className={`p-2.5 rounded-xl text-left border transition relative ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50/50 ring-1 ring-blue-500'
                    : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
                }`}
              >
                <div className="font-semibold text-xs text-slate-800 flex items-center justify-between">
                  <span>{preset.name}</span>
                  {isSelected && <Check className="w-3.5 h-3.5 text-blue-600 shrink-0" />}
                </div>
                <div className="text-[10px] text-slate-500 line-clamp-1 mt-0.5">
                  {preset.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Pen ink colors & Paper styles */}
      <div className="grid grid-cols-2 gap-4">
        {/* Ink color */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5">
            Цвет чернил:
          </label>
          <div className="flex items-center space-x-2">
            {presetsData?.pen_colors.map((color) => {
              const isSelected = penColor === color.id;
              return (
                <button
                  key={color.id}
                  onClick={() => setPenColor(color.id)}
                  title={color.name}
                  className={`w-7 h-7 rounded-full flex items-center justify-center transition active:scale-90 ${
                    isSelected ? 'ring-2 ring-offset-2 ring-blue-500 scale-110' : 'opacity-80 hover:opacity-100'
                  }`}
                  style={{ backgroundColor: color.hex }}
                >
                  {isSelected && <Check className="w-3.5 h-3.5 text-white stroke-[3]" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* Paper style */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5">
            Тип листа:
          </label>
          <select
            value={paperStyle}
            onChange={(e) => setPaperStyle(e.target.value)}
            className="w-full text-xs font-medium py-1.5 px-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 outline-none focus:border-blue-500"
          >
            {presetsData?.paper_styles.map((style) => (
              <option key={style.id} value={style.id}>
                {style.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Toggles & Sliders */}
      <div className="pt-2 border-t border-slate-100 space-y-3">
        {/* Red margins toggle */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-700">Красные тетрадные поля</span>
          <input
            type="checkbox"
            checked={hasMargins}
            onChange={(e) => setHasMargins(e.target.checked)}
            className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
          />
        </div>

        {/* Humanize markers toggle */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-700">Маркеры и формулы в рамках</span>
          <input
            type="checkbox"
            checked={humanize}
            onChange={(e) => setHumanize(e.target.checked)}
            className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
          />
        </div>

        {/* Jitter slider */}
        <div>
          <div className="flex justify-between text-[11px] font-medium text-slate-500 mb-1">
            <span>Неровность строк (дрожание руки)</span>
            <span>{jitter.toFixed(1)}x</span>
          </div>
          <input
            type="range"
            min="0.0"
            max="2.0"
            step="0.2"
            value={jitter}
            onChange={(e) => setJitter(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
        </div>
      </div>
    </div>
  );
};
