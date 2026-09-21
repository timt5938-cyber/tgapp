# 2. Hybrid Telegram Mini App and Bot Delivery

The system splits functionality between an interactive Telegram Mini App (for visual calibration, tuning, and real-time page preview) and direct Telegram Bot chat messages (for delivering compiled multi-page PDF documents).

## Considered Options
- **All-in-Mini-App:** User downloads generated PDF directly within the WebView iframe. (Rejected due to iOS/Android Telegram WebView sandboxing issues where blob downloads often fail or do not persist to device files properly).
- **Chat-only interface:** User configures everything through inline keyboards and messages. (Rejected due to poor UX for image previews, sheet adjustments, and glyph calibration).
- **Hybrid (Selected):** Rich visual configuration and live preview inside the Mini App; backend triggers the Telegram Bot API (`sendDocument`) to deliver the finalized PDF directly into the user's chat history.

## Consequences
- The Mini App sends Telegram WebApp `initData` containing authenticated `user.id` to the backend.
- The backend needs background job capability to render pages, build the PDF, and notify the user via the bot asynchronously.
