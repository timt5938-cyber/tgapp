import React, { useState, useEffect, useRef } from 'react';
import { useTelegram } from './hooks/useTelegram';
import { api, PresetsResponse } from './api/client';
import { Header } from './components/Header';
import { ConspectusEditor } from './components/ConspectusEditor';
import { NotebookCustomizer } from './components/NotebookCustomizer';
import { PagePreview } from './components/PagePreview';
import { CalibrationModal } from './components/CalibrationModal';
import { SettingsModal } from './components/SettingsModal';

const DEFAULT_SAMPLE_TEXT = `Тема: Основы баз данных и ACID

1. Введение в СУБД
Реляционные базы данных структурируют информацию в виде таблиц со строгими связями (Foreign Keys).
[ВАЖНО] Транзакции обязаны гарантировать принципы ACID.
- Atomicity: атомарность операций
- Consistency: сохранность инвариантов
- Isolation: параллельное исполнение без конфликтов
- Durability: надежная фиксация на диске
[ФОРМУЛА] BEGIN TRANSACTION; COMMIT;
[ВЫВОД] Реляционные СУБД критичны для финансовых и транзакционных систем.`;

export const App: React.FC = () => {
  const { user, haptic } = useTelegram();

  // Core conspectus state
  const [text, setText] = useState(DEFAULT_SAMPLE_TEXT);
  const [mode, setMode] = useState('smart'); // 'smart' or 'verbatim'

  // Customization state
  const [paperStyle, setPaperStyle] = useState('squared_5mm');
  const [hasMargins, setHasMargins] = useState(true);
  const [penColor, setPenColor] = useState('blue_ballpoint');
  const [fontPreset, setFontPreset] = useState('marck_script');
  const [jitter, setJitter] = useState(1.0);
  const [slant, setSlant] = useState(1.0);
  const [humanize, setHumanize] = useState(true);

  // Settings & modals
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('user_gemini_api_key') || '');
  const [isCalibrationOpen, setIsCalibrationOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Data & loading
  const [presetsData, setPresetsData] = useState<PresetsResponse | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [successDelivered, setSuccessDelivered] = useState(false);

  const previewTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch presets on mount
  useEffect(() => {
    api.getPresets()
      .then(setPresetsData)
      .catch((err) => console.error('Presets error:', err));
  }, []);

  // Live preview update with debounce
  useEffect(() => {
    if (previewTimeoutRef.current) {
      clearTimeout(previewTimeoutRef.current);
    }

    setIsLoadingPreview(true);
    previewTimeoutRef.current = setTimeout(async () => {
      try {
        const res = await api.getPreview({
          text,
          paper_style: paperStyle,
          has_margins: hasMargins,
          pen_color: penColor,
          font_preset: fontPreset,
          jitter,
          slant,
          humanize
        });
        setPreviewUrl(res.page_preview_base64);
        setTotalPages(res.total_pages);
      } catch (err) {
        console.error('Failed to load preview:', err);
      } finally {
        setIsLoadingPreview(false);
      }
    }, 450);

    return () => {
      if (previewTimeoutRef.current) clearTimeout(previewTimeoutRef.current);
    };
  }, [text, paperStyle, hasMargins, penColor, fontPreset, jitter, slant, humanize]);

  const handleGenerate = async () => {
    haptic.impact('heavy');
    setIsGenerating(true);
    setSuccessDelivered(false);

    try {
      const res = await api.generate({
        user_id: user.id,
        text,
        mode,
        paper_style: paperStyle,
        has_margins: hasMargins,
        pen_color: penColor,
        font_preset: fontPreset,
        jitter,
        slant,
        humanize,
        custom_gemini_key: geminiKey || undefined
      });

      if (res.success) {
        haptic.notify('success');
        setSuccessDelivered(true);
        setTimeout(() => setSuccessDelivered(false), 8000);
      }
    } catch (err: any) {
      haptic.notify('error');
      alert(err.message || 'Ошибка генерации конспекта');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col max-w-xl mx-auto pb-10">
      <Header
        user={user}
        onOpenCalibration={() => {
          haptic.selection();
          setIsCalibrationOpen(true);
        }}
        onOpenSettings={() => {
          haptic.selection();
          setIsSettingsOpen(true);
        }}
      />

      <main className="p-4 space-y-4 flex-1">
        {/* Input & Mode */}
        <ConspectusEditor
          text={text}
          setText={(t) => {
            setText(t);
            setSuccessDelivered(false);
          }}
          mode={mode}
          setMode={(m) => {
            haptic.selection();
            setMode(m);
          }}
        />

        {/* Live Page Preview */}
        <PagePreview
          previewUrl={previewUrl}
          totalPages={totalPages}
          isLoading={isLoadingPreview}
          isGenerating={isGenerating}
          onGenerate={handleGenerate}
          successDelivered={successDelivered}
        />

        {/* Notebook & Handwriting Customizer */}
        <NotebookCustomizer
          presetsData={presetsData}
          paperStyle={paperStyle}
          setPaperStyle={(s) => {
            haptic.selection();
            setPaperStyle(s);
          }}
          hasMargins={hasMargins}
          setHasMargins={(m) => {
            haptic.selection();
            setHasMargins(m);
          }}
          penColor={penColor}
          setPenColor={(c) => {
            haptic.selection();
            setPenColor(c);
          }}
          fontPreset={fontPreset}
          setFontPreset={(f) => {
            haptic.selection();
            setFontPreset(f);
          }}
          jitter={jitter}
          setJitter={setJitter}
          slant={slant}
          setSlant={setSlant}
          humanize={humanize}
          setHumanize={setHumanize}
        />
      </main>

      {/* Modals */}
      <CalibrationModal
        userId={user.id}
        isOpen={isCalibrationOpen}
        onClose={() => setIsCalibrationOpen(false)}
        onCalibrationSuccess={() => {
          haptic.notify('success');
        }}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        geminiKey={geminiKey}
        setGeminiKey={setGeminiKey}
      />
    </div>
  );
};
