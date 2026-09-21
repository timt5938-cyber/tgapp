import { useEffect, useState } from 'react';

export function useTelegram() {
  const [isReady, setIsReady] = useState(false);
  const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : undefined;

  useEffect(() => {
    if (tg) {
      tg.ready();
      tg.expand();
      setIsReady(true);
    }
  }, [tg]);

  const user = tg?.initDataUnsafe?.user || {
    id: 123456789,
    first_name: 'Студент',
    username: 'student'
  };

  const haptic = {
    impact: (style: 'light' | 'medium' | 'heavy' = 'medium') => {
      try {
        tg?.HapticFeedback?.impactOccurred(style);
      } catch (e) {}
    },
    notify: (type: 'success' | 'warning' | 'error') => {
      try {
        tg?.HapticFeedback?.notificationOccurred(type);
      } catch (e) {}
    },
    selection: () => {
      try {
        tg?.HapticFeedback?.selectionChanged();
      } catch (e) {}
    }
  };

  return {
    tg,
    user,
    isReady,
    haptic,
    close: () => tg?.close()
  };
}
