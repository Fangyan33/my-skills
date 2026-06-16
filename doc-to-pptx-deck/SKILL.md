---
name: doc-to-pptx-deck
description: Convert Markdown or DOCX reports into styled screenshot-based PowerPoint decks. Use when Codex needs to read a .md or .docx source, draft and confirm a PPT outline, generate one HTML page per slide, screenshot the HTML pages into images, and merge those images into a .pptx file. Requires explicit user confirmation before each of the four stages.
---

# Doc To PPTX Deck

Use this skill to turn a Markdown or DOCX report into a 16:9 PPTX deck through a controlled four-stage pipeline:

1. source document -> PPT outline
2. outline + content -> one HTML file per slide
3. HTML files -> PNG screenshots
4. PNG screenshots -> PPTX

The default output is a screenshot-based PPTX where each slide is a full-page image. Do not promise editable slide text unless the user explicitly asks for a different implementation.

## Mandatory Confirmation Gates

Never run the full pipeline in one uninterrupted pass. Before each stage, tell the user what will be produced and ask for confirmation.

- **Gate 1**: Before reading/converting the source into an outline, confirm the source file and expected deck length.
- **Gate 2**: After presenting the outline, wait for user confirmation before writing HTML files.
- **Gate 3**: After HTML files exist, wait for user confirmation before screenshotting them into `img`.
- **Gate 4**: After images exist, wait for user confirmation before merging them into PPTX.

Accept confirmations such as “继续”, “确认”, “开始生成 HTML”, “开始截图”, or “合并 PPTX”. If the user asks for changes at any gate, revise that stage output first.

## Stage 1: Source To Outline

Read the source before planning.

- For `.md`, read headings, tables, and executive summaries directly.
- For `.docx`, extract text with an available DOCX parser/tool. If no parser exists, inspect the zipped XML structure or ask before installing dependencies.
- Create a page-level outline with slide number, title, main message, and suggested layout.
- Keep slide count near the user’s requested count. If unspecified, choose a compact deck length based on document density.
- Present the outline to the user and stop at Gate 2.

## Stage 2: Outline To HTML

Generate one standalone HTML file per slide in `html/`, named `01.html`, `02.html`, and so on.

- Use the default style in `references/default-style.md` unless the user explicitly provides a reference template.
- If the user provides a template, inspect the template HTML first and adopt its size, color system, typography, and layout components.
- Each HTML file must contain a complete document with inline CSS so it can be opened and screenshotted independently.
- Use a `.ppt-slide` root element sized to the slide canvas.
- Keep text concise enough to fit. Prefer cards, tables, metric blocks, and flow diagrams over dense paragraphs.
- When a slide needs imagery and no real image is provided, reserve an image area with a local placeholder, generated image, or network image only if network use is acceptable.
- After writing HTML, report the file count and stop at Gate 3.

## Stage 3: HTML To Images

Use `scripts/render_html_to_images.py` to screenshot each HTML page.

Default command:

```bash
python3 skills/doc-to-pptx-deck/scripts/render_html_to_images.py \
  --html-dir html \
  --img-dir img \
  --selector .ppt-slide \
  --viewport 1280x720 \
  --channel chrome
```

Notes:

- The script expects Playwright CLI and Chrome/Chromium to be available.
- If Chrome fails under sandbox restrictions, retry with the required approval/escalation flow.
- Verify that `img/01.png`, `img/02.png`, etc. exist and match the slide size.
- Stop at Gate 4 after reporting image count and dimensions.

## Stage 4: Images To PPTX

Use `scripts/images_to_pptx.py` to create the deck.

Default command:

```bash
python3 skills/doc-to-pptx-deck/scripts/images_to_pptx.py \
  --img-dir img \
  --output deck.pptx
```

The script:

- sorts `*.png` by filename;
- creates one 16:9 slide per image;
- places each image at full-slide size;
- writes a PowerPoint 2007+ `.pptx` using Python standard library only.

After generation, verify the PPTX exists and contains the same number of slides as images.

## Validation Checklist

Before final response:

- Confirm the outline was approved before HTML generation.
- Confirm the HTML stage was approved before screenshots.
- Confirm the screenshot stage was approved before PPTX merge.
- Verify generated counts: HTML pages, PNG images, PPTX slides.
- Report output paths and any dependency or approval issues encountered.
