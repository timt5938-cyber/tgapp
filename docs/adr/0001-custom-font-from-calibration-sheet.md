# 1. Custom Font from Calibration Sheet

To achieve high visual fidelity to the user's authentic handwriting without hallucinating words or corrupting Cyrillic spelling, the system will extract glyphs from a standardized Calibration Sheet rather than estimating handwriting from random freeform photos or relying on generic preset fonts.

## Considered Options
- **Generic handwriting presets with jitter:** Fast and low effort, but does not replicate the user's actual individual handwriting.
- **Pure image generation via diffusion/multimodal models:** Generates entire notebook pages end-to-end, but currently produces frequent spelling and lexical errors in Russian Cyrillic.
- **Calibration Sheet vectorization (Selected):** User fills a guided alphabet grid; OpenCV/image processing isolates each letter into a Personal Font glyph map used for procedural document rendering.

## Consequences
- The user must perform a one-time onboarding action (filling and photographing the Calibration Sheet).
- Once calibrated, the user's Personal Font is stored and can generate any number of conspectus documents accurately.
