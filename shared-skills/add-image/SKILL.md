---
name: add-image
description: Use when adding a new image to a website section, especially when the best source is a screenshot that should be regenerated into a cleaner visual. Covers the workflow from screenshot to GPT image generation, rounded corners, and an in-page preview that closes when clicking outside.
---

# Add Image

## Overview

Use this skill when a web section needs a polished visual based on a rough screenshot, dashboard capture, or UI mockup. The default workflow is to keep the screenshot as the visual reference, regenerate a cleaner version with GPT, place it into the site, round the corners if needed, and make sure the preview opens in-page and closes on backdrop click.

## When To Use

- The user wants to add a screenshot-like image to a website.
- A raw screenshot looks too messy and should be turned into a cleaner marketing-style visual.
- A section needs a card image plus a related dashboard or product screenshot beside it.
- The current image preview opens the file directly and should instead use an overlay/lightbox.

## Workflow

### 1. Start from a screenshot

- Prefer a real screenshot as the source of truth for content and layout.
- If the screenshot has browser chrome, noise, or distracting edges, crop it first.
- Keep the original screenshot in the project as reference when useful.

### 2. Regenerate the image with GPT

- Use the screenshot as the visual pattern.
- Ask for the same layout, same dark/light direction, and the same type of UI, but cleaner.
- Keep the prompt narrow. Change only what the user asked for.
- If the image should look productized, GPT output is usually better than using the screenshot directly.

### 3. Save the generated result into the project

- Put web images in the project's image folder, usually `web/site/images/`.
- Use explicit names that describe the role, e.g. `newsletter-card.png`, `newsletter-briefing-generated.png`.
- Do not overwrite the only original source unless the user explicitly wants that.

### 4. Add it to the web cleanly

- Prefer one image per box/card.
- Avoid stacking image background plus wrapper background unless that is intentional.
- If two visuals should sit side by side, give each its own container instead of one shared visual frame.
- Match aspect ratio per image instead of forcing one ratio for unrelated visuals.

### 5. Round corners only where it helps

- If the surrounding UI uses cards, give the image preview similar rounding.
- Apply rounding on the element that visually frames the image, not on multiple nested wrappers.
- Avoid double framing: one visible border/background layer is usually enough.

### 6. Make preview work inside the page

- Do not rely on links that open the raw image file directly.
- Use an in-page lightbox/overlay preview.
- The preview must close with:
  - click outside the image
  - close button
  - `Esc`
- Lock page scroll while the overlay is open.

## Prompt Pattern

Use a prompt like:

`Create a cleaner image based on this screenshot. Keep the same layout and visual hierarchy, preserve the same product UI feel, change only the requested content, and output a polished standalone image without browser chrome.`

## Quality Checks

- The image matches the original screenshot's intent.
- The generated result is cleaner than the screenshot, not more generic.
- Corners, border, and inner spacing fit the site style.
- Clicking the preview does not navigate away from the page.
- Clicking beside the preview closes it immediately.

## Common Mistakes

- Using a generated image with its own fake background inside another styled card, causing double background.
- Treating two different visuals as if they should share one aspect ratio.
- Opening the raw image file instead of an overlay.
- Regenerating too aggressively and losing the structure of the original screenshot.
