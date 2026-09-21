import React, { useState } from 'react';
import { X, Upload, CheckCircle2, AlertCircle, Loader2, Camera } from 'lucide-react';
import { api } from '../api/client';

interface CalibrationModalProps {
  userId: number;
  isOpen: boolean;
  onClose: () => void;
  onCalibrationSuccess: () => void;
}

export const CalibrationModal: React.FC<CalibrationModalProps> = ({
  userId,
  isOpen,
  onClose,
  onCalibrationSuccess
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setResultMessage(null);
    setErrorMessage(null);

    try {
      const res = await api.uploadCalibration(userId, file);
      setResultMessage(res.message);
      onCalibrationSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || 'Ошибка обработки фото');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl max-w-md w-full p-5 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h2 className="text-base font-bold text-slate-800 flex items-center space-x-2">
            <Camera className="w-5 h-5 text-blue-600" />
            <span>Калибровка вашего почерка</span>
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Instructions */}
        <div className="p-4 rounded-2xl bg-blue-50/50 border border-blue-100 space-y-2.5 text-xs text-slate-700">
          <p className="font-bold text-slate-900 text-sm">Как добавить свой почерк:</p>
          <p className="leading-relaxed">
            Возьмите любой чистый лист бумаги (А4 или тетрадный) и напишите от руки шариковой или гелевой ручкой:
          </p>
          <div className="space-y-1.5 bg-white p-3 rounded-xl border border-blue-150 font-mono text-[11px] text-slate-800">
            <div>
              <span className="font-bold text-blue-600">1. Заглавные:</span> А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я
            </div>
            <div>
              <span className="font-bold text-blue-600">2. Строчные:</span> а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я
            </div>
            <div>
              <span className="font-bold text-blue-600">3. Цифры:</span> 0 1 2 3 4 5 6 7 8 9
            </div>
          </div>
          <p className="text-slate-500 text-[11px]">
            Сфотографируйте лист при хорошем свете и загрузите сюда (или просто отправьте фото в чат боту).
          </p>
        </div>

        {/* Upload box */}
        <label className="flex flex-col items-center justify-center p-5 border-2 border-dashed border-blue-300 rounded-2xl bg-blue-50/20 hover:border-blue-500 hover:bg-blue-50/40 cursor-pointer transition">
          {isUploading ? (
            <div className="flex items-center space-x-2 text-blue-600 font-semibold text-xs py-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Считываем буквы и вырезаем глифы...</span>
            </div>
          ) : (
            <>
              <Upload className="w-7 h-7 text-blue-500 mb-2" />
              <span className="text-xs font-bold text-slate-800">Загрузить фото листа с почерком</span>
              <span className="text-[11px] text-slate-400 mt-0.5">JPG или PNG со смартфона</span>
            </>
          )}
          <input
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            disabled={isUploading}
            className="hidden"
          />
        </label>

        {/* Feedback Messages */}
        {resultMessage && (
          <div className="flex items-center space-x-2 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{resultMessage}</span>
          </div>
        )}

        {errorMessage && (
          <div className="flex items-center space-x-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
        >
          Закрыть
        </button>
      </div>
    </div>
  );
};
