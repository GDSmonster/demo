# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a QQ Music hackathon demo showcasing "Music as Language" — a feature that lets users share individual lyrics with their corresponding audio clips, either as plain text or as music-based sticker images in chat conversations.

The project is a **single-file HTML prototype** (`index.html`) demonstrating the complete user flow from selecting lyrics in a music player to sending them in WeChat-style chat interfaces.

## Project Structure

- **`index.html`** — The entire application: a ~3100-line self-contained HTML file with embedded CSS and JavaScript. All UI components, animations, and interactive demos live here.
- **`assets/img/`** — Images for stickers, UI screenshots, and visual examples
- **`assets/audio/`** — Audio clips for the interactive demo
- **`split_lyrics.py`** — Python utility for automatic lyric-to-audio alignment using Whisper ASR
- **`lyrics.txt`, `lyrics_align.html`** — Supporting files for lyric processing
- **Preview PNG files** — Screenshots of various UI states for documentation

## Architecture

### Single-Page Structure

The HTML is organized into distinct sections via CSS class namespaces:

1. **Hero & Navigation** (`.hero`, `.nav`) — Landing page with value proposition
2. **Background Section** (`.pain`, `.background-*`) — Design rationale and user research
3. **Features Section** (`.features`, `.f-card`, `.f-flow`) — Product capability overview with flowcharts
4. **Demo Stage** (`.stage`, `.demo-layout`, `.phone`) — Interactive phone simulators showing:
   - **Reply Flow Demo** — 4-step music reply workflow (player → confirmation → WeChat → AI)
   - **Community Demo** — Music sticker community and collection walkthrough
5. **Value Section** (`.value`, `.loop-wrap`) — Business value and user benefit loop
6. **Footer** — Basic project attribution

### Phone Simulator Pattern

Multiple interactive phone mockups (`.phone`, `.phone-screen`) simulate real app flows:

- **`.player`** — QQ Music player with tappable lyrics
- **`.confirm`** — Lyric clip editor with waveform and sticker options
- **`.chat`** — WeChat-style message interface
- **`.ai`** — AI lyric suggestion interface
- **`.cscreen`** (community screens) — Music sticker browsing and management

Each screen is toggled via `.on` class and orchestrated by inline `<script>` sections at the end of the HTML.

### State Management

Uses vanilla JavaScript with imperative DOM manipulation:

- Tab/step navigation: `.step-tab` buttons toggle `.screen.on`
- Audio playback: HTML5 `<audio>` elements controlled by play/pause buttons
- Animations: CSS transitions + `.playing`, `.pressed`, `.on` state classes
- Demo auto-play: Custom scripted sequences with simulated pointer (`.community-demo-pointer`)

## Key Technologies & Patterns

- **No build system** — Pure HTML/CSS/JS, open directly in a browser
- **Inline SVG** — Icons and decorative elements embedded as SVG markup
- **CSS Grid for layout** — `.demo-layout`, `.reply-flow-branches`, `.qm-grid`
- **CSS custom properties** — Design tokens in `:root` (colors, spacing, shadows)
- **Responsive breakpoints** — `@media(max-width: 960px)` and `@media(max-width: 600px)`
- **Accessibility** — `aria-label`, `role`, `aria-labelledby` on major sections; `hidden` attribute for conditional visibility

## Design System

Defined in CSS `:root` variables:

```css
--green: #31c27c          /* Primary action color */
--green-deep: #0fae66     /* Hover/active state */
--ink: #14251b            /* Primary text */
--sub: #617769            /* Secondary text */
--line: #dce8df           /* Borders */
--bg-2: #f6f8f6           /* Alternate background */
```

Typography follows a fluid scale using `clamp()` for responsive sizing.

## Lyric Alignment Tool

`split_lyrics.py` generates timestamped lyrics for audio synchronization:

**Dependencies:**
- `faster-whisper` — ASR with word-level timestamps
- Uses `difflib.SequenceMatcher` for forced alignment between recognized words and provided lyrics

**Usage:**
```bash
python split_lyrics.py --audio song.mp3 --lyrics lyrics.txt --out output.json
```

Outputs JSON with `{text, start, end}` per line and an LRC file.

## Development Workflow

### Viewing the Demo

Simply open `index.html` in a modern browser (Chrome/Safari/Firefox). No local server required.

### Making Changes

1. Edit `index.html` directly
2. Reload the browser to see changes
3. For CSS: styles are in the `<style>` block (lines ~7–1208)
4. For JavaScript: inline `<script>` blocks are at the bottom of the HTML
5. Audio/image assets referenced via relative paths (`assets/img/`, `assets/audio/`)

### Common Modifications

- **Adding a new demo screen**: Create a new `.screen` div inside `.phone-screen`, add a corresponding `.step-tab` button, wire up with JS event listeners
- **Styling adjustments**: Modify CSS custom properties in `:root` for global changes, or target specific component classes
- **Responsive tweaks**: Check the three main breakpoints (>960px, 600-960px, <600px)

## Code Conventions

- **Class naming**: BEM-like (`.component-element`, `.state-modifier`)
- **Indentation**: 2 spaces (CSS and HTML)
- **Comments**: Section headers use `/* ============ Section ============ */`
- **Language**: UI text is in Chinese; code comments mix Chinese and English
- **No minification**: Code is readable and formatted for easy editing

## Important Notes

- Assets (audio, images) are referenced but not all tracked in this directory listing — verify paths when adding new resources
- The demo includes embedded audio clips; ensure `assets/audio/` contains the necessary files for playback features to work
- Phone mockup dimensions are fixed (`width: 360px; height: 740px`) for consistent demo appearance
- Auto-play demos (community walkthrough) use custom animation sequencing — see `#community` section scripts for timing logic
