import React, { useState } from 'react';
import { Wand2, FileText, Sparkles, RefreshCw } from 'lucide-react';

interface ConspectusEditorProps {
  text: string;
  setText: (t: string) => void;
  mode: string;
  setMode: (m: string) => void;
}

const SAMPLE_LECTURES = [
  {
    label: "Основы Python",
    text: `Тема: Основы языка Python

1. Типы данных и переменные
Python является языком с динамической типизацией.
Основные типы: int, float, str, bool, list, dict, set, tuple.
[ВАЖНО] Списки изменяемы (mutable), а кортежи неизменяемы (immutable).
[ФОРМУЛА] result = [x**2 for x in range(10) if x % 2 == 0]
2. Функции и замыкания
Функции определяются ключевым словом def и являются объектами первого класса.
[ВЫВОД] Python идеален для быстрой разработки и анализа данных.`
  },
  {
    label: "Базы данных и ACID",
    text: `Тема: Транзакции в реляционных СУБД

1. Понятие транзакции
Транзакция — логическая единица работы, неделимая последовательность SQL-команд.
[ВАЖНО] Каждая транзакция обязана удовлетворять принципам ACID:
- Atomicity (Атомарность) -> все или ничего
- Consistency (Согласованность) -> целостность данных
- Isolation (Изолированность) -> независимость потоков
- Durability (Долговечность) -> сохранение на диске
[ФОРМУЛА] BEGIN TRANSACTION; UPDATE accounts SET balance = balance - 100; COMMIT;
[ВЫВОД] ACID гарантирует надежность критических финансовых операций.`
  },
  {
    label: "Физика: Законы Ньютона",
    text: `Тема: Законы классической механики

1. Инерциальные системы отсчета
Существуют системы, в которых тело сохраняет состояние покоя или равномерного прямолинейного движения.
[ФОРМУЛА] F = m * a
2. Третий закон динамики
Действию всегда есть равное и противоположное противодействие.
[ВАЖНО] Силы взаимодействия имеют одинаковую физическую природу и направлены вдоль одной прямой.
[ВЫВОД] Механика Ньютона применима для макрообъектов на скоростях много меньше скорости света.`
  }
];

export const ConspectusEditor: React.FC<ConspectusEditorProps> = ({
  text,
  setText,
  mode,
  setMode
}) => {
  return (
    <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-3">
      {/* Mode selection pill tabs */}
      <div className="flex items-center p-1 bg-slate-100 rounded-xl">
        <button
          onClick={() => setMode('smart')}
          className={`flex-1 flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition ${
            mode === 'smart'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Умный конспект (Gemini)</span>
        </button>

        <button
          onClick={() => setMode('verbatim')}
          className={`flex-1 flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition ${
            mode === 'verbatim'
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Слово в слово</span>
        </button>
      </div>

      {/* Quick sample pills */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 text-xs no-scrollbar">
        <span className="text-slate-400 text-[11px] font-medium shrink-0">Примеры:</span>
        {SAMPLE_LECTURES.map((sample, idx) => (
          <button
            key={idx}
            onClick={() => setText(sample.text)}
            className="shrink-0 px-2.5 py-1 rounded-full bg-slate-100 hover:bg-blue-50 hover:text-blue-600 text-slate-600 text-[11px] font-medium transition border border-slate-200"
          >
            {sample.label}
          </button>
        ))}
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Вставьте сюда текст лекции, тему или тезисы для рукописного конспекта..."
          rows={6}
          className="w-full p-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none text-sm text-slate-800 placeholder-slate-400 resize-none transition"
        />
        <div className="absolute bottom-2.5 right-3 text-[11px] text-slate-400 font-medium">
          {text.length} симв.
        </div>
      </div>
    </div>
  );
};
