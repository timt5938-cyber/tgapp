import React, { useState } from 'react';
import { Eye, Send, ZoomIn, ZoomOut, CheckCircle2, Loader2 } from 'lucide-react';

interface PagePreviewProps {
  previewUrl: string | null;
  totalPages: number;
  isLoading: boolean;
  isGenerating: boolean;
  onGenerate: () => void;
  successDelivered: boolean;
}

export const PagePreview: React.FC<PagePreviewProps> = ({
  previewUrl,
  totalPages,
  isLoading,
  isGenerating,
  onGenerate,
  successDelivered
}) => {
  const [zoom, setZoom] = useState(false);

  return (
    <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-3">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <div className="flex items-center space-x-2 text-slate-800 font-bold text-sm">
          <Eye className="w-4 h-4 text-blue-600" />
          <span>Живое превью страницы</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
            1 из {totalPages} стр.
          </span>
          <button
            onClick={() => setZoom(!zoom)}
            className="p-1 rounded text-slate-500 hover:bg-slate-100 transition"
            title="Увеличить"
          >
            {zoom ? <ZoomOut className="w-4 h-4" /> : <ZoomIn className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Preview viewport */}
      <div className="relative rounded-xl overflow-hidden bg-slate-100 border border-slate-200 shadow-inner flex items-center justify-center min-h-[320px]">
        {isLoading && (
          <div className="absolute inset-0 bg-white/70 backdrop-blur-sm z-10 flex flex-col items-center justify-center space-y-2">
            <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />
            <span className="text-xs font-semibold text-slate-600">Отрисовываем превью...</span>
          </div>
        )}

        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Превью конспекта"
            className={`transition-all duration-300 rounded shadow-md object-contain max-h-[460px] w-auto ${
              zoom ? 'scale-125 cursor-zoom-out' : 'cursor-zoom-in'
            }`}
            onClick={() => setZoom(!zoom)}
          />
        ) : (
          <div className="text-center p-6 text-slate-400 text-xs">
            Загрузка предпросмотра...
          </div>
        )}
      </div>

      {/* Success notification banner */}
      {successDelivered && (
        <div className="flex items-center space-x-2 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Конспект успешно сгенерирован и отправлен в чат Telegram!</span>
        </div>
      )}

      {/* Big Action Button */}
      <button
        onClick={onGenerate}
        disabled={isGenerating || isLoading}
        className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 active:scale-[0.99] text-white font-bold text-sm shadow-md shadow-blue-500/25 flex items-center justify-center space-x-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isGenerating ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Синтезируем конспект и PDF...</span>
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            <span>Сгенерировать и отправить в Telegram</span>
          </>
        )}
      </button>
    </div>
  );
};
