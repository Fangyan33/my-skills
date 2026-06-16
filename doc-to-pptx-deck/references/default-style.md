# Default HTML/CSS Style

Use this default style when the user does not specify a reference template. The style is a red-gold study/report deck suitable for policy, party-study, research, and formal briefing material.

## Required Canvas

Every slide HTML must use a single root slide element:

```css
*{box-sizing:border-box}
body{
  margin:0;
  background:#1a1a1a;
  font-family:"Noto Sans SC",sans-serif;
}
.title-font{font-family:"Noto Serif SC",serif}
.ppt-slide{
  position:relative;
  width:1280px;
  height:720px;
  margin:0 auto;
  overflow:hidden;
  background:linear-gradient(135deg,#8B0000 0%,#A52A2A 50%,#8B0000 100%);
  color:#fff;
}
```

Include this font link unless the template or environment requires otherwise:

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Noto+Serif+SC:wght@600;700;900&display=swap" rel="stylesheet">
```

## Color And Typography

- Primary background: `#8B0000` to `#A52A2A` to `#8B0000`.
- Accent gold: `#FFD700`.
- Body text: `#fff`.
- Muted dark overlay: `rgba(0,0,0,.15)`.
- Card fill: `rgba(255,255,255,.08)`.
- Gold panel fill: `rgba(255,215,0,.12)` or `rgba(255,215,0,.14)`.
- Main title weight: `800` or `900`.
- Body line-height: `1.45` to `1.62`.
- Do not use negative letter spacing or viewport-scaled font sizes.

## Common Components

Use these components as the default vocabulary.

```css
.header{
  height:85px;
  display:flex;
  align-items:center;
  padding:0 64px;
  background:rgba(0,0,0,.15);
}
.header h1{
  font-size:36px;
  margin:0;
  font-weight:800;
}
.main{
  height:635px;
  padding:36px 64px;
}
.card{
  padding:22px;
  border-radius:8px;
  background:rgba(255,255,255,.08);
}
.card h3{
  font-size:22px;
  margin:0 0 10px;
  color:#FFD700;
}
.card p{
  font-size:17px;
  line-height:1.55;
  margin:0;
}
.callout,.note{
  padding:22px 26px;
  border-left:5px solid #FFD700;
  border-radius:8px;
  background:rgba(255,215,0,.12);
}
.panel{
  padding:28px;
  border:3px solid #FFD700;
  border-radius:8px;
  background:rgba(255,215,0,.13);
  box-shadow:0 22px 44px rgba(0,0,0,.35);
}
.gold{color:#FFD700;font-weight:900}
```

## Layout Patterns

Prefer these layouts:

- **Cover**: centered title, badge, divider, 3-4 keyword cards.
- **Section content**: top `.header`, body `.main`, left text and right panel/image.
- **Framework page**: four cards or a 2x2 grid.
- **Data page**: top metric row, lower cards/table.
- **Comparison page**: CSS grid table with gold header row.
- **Process page**: horizontal flow boxes or two-row chain.
- **Summary page**: large final statement plus 3-4 takeaway cards.

Recommended structural CSS:

```css
.left{width:58%;padding-right:44px}
.right{width:42%;padding-left:30px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.top{display:flex;gap:20px;margin-bottom:22px}
.metric{
  flex:1;
  text-align:center;
  padding:22px;
  border-radius:8px;
  background:rgba(255,215,0,.14);
}
.metric strong{
  display:block;
  color:#FFD700;
  font-size:36px;
  margin-bottom:6px;
}
```

## Constraints

- Keep the slide root at exactly `1280px x 720px`.
- Use 16:9 screenshots and PPTX dimensions.
- Keep border radius at `8px` or less.
- Avoid decorative gradient blobs/orbs except subtle cover-page glow elements if needed.
- Do not put cards inside cards.
- Keep text within containers at all viewport sizes used for screenshots.
- If a reference template is provided, inspect it and use that template instead of this default style.
