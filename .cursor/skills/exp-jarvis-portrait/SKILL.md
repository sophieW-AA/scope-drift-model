---
name: exp-jarvis-portrait
description: Convert any photo of a single person into a JARVIS-style holographic portrait. Use when the user says "JARVIS this", "JARVIS portrait", or any variation requesting the JARVIS HUD treatment on a person's photo.
---

# JARVIS Portrait Conversion

## Trigger
User provides a photo of a single person and asks to "JARVIS this", "JARVIS portrait", or any variation requesting the JARVIS HUD treatment.

## Input
- **Required:** One photo of an individual person (file ID or URL)

## Process
1. Use `edit_image` with the person's photo as the only image
2. Apply this prompt:
```
Crop this image very tight to the person's face — the face should take up approximately 75% of the entire image, showing only the face and a small amount of neck/collar. Do NOT rotate, reposition, or re-angle the person — keep their pose, angle, and orientation exactly as in the original photo. Replace the background with a dark navy/black background. Keep the person's face, hair, glasses, clothing, and all features completely unchanged — exactly as they are in the photo. Then add a JARVIS-style holographic HUD overlay: red glowing circles, arcs, and data readouts on the left side, blue scanner circles and readouts on the right side. The HUD elements should float semi-transparently in front of and around the face. Cinematic lighting. Do NOT alter the person's appearance in any way. No helmet or headgear.
```
3. Return the converted image

## Key Rules
- **Face takes up 75% of the image** — tight crop, only face and a small amount of neck/collar visible
- **Preserve orientation** — never rotate or reposition the person; keep their original pose and angle
- **Never alter faces** — the person must look exactly like their photo
- **HUD colours:** Red elements LEFT, Blue elements RIGHT (matching Iron Man JARVIS)
- **No helmets or headgear** — ever
- If the AI morphs the face, retry with a stronger prompt emphasising the person's specific features

## Output
Return the converted image directly.
