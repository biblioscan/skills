# BiblioScan Skills

Open-source AI agent skills for [BiblioScan](https://biblioscan.ai) users: people who buy and resell second-hand books.

| Skill | What it does |
|---|---|
| [`biblioscan-annonce`](biblioscan-annonce/SKILL.md) | Turns an ISBN or ASIN (or a list) into priced listings published on Vinted and Leboncoin |

---

## `biblioscan-annonce`

Give your agent one or more ISBNs/ASINs and a folder of photos. For each book, the skill:

1. **Reads the BiblioScan stats**: median sale price, sales over 12 months, current Amazon price, price history.
2. **Checks the competition** on Chasse aux Livres, Vinted and Leboncoin, using the shortcut links from the BiblioScan page.
3. **Grades the book's condition** from your photos (New / Very good / Good / Satisfactory).
4. **Sets one price** for both platforms: a little under the Amazon and Chasse aux Livres prices, then matched to the cheapest Vinted/Leboncoin listing based on condition. See [`pricing.md`](biblioscan-annonce/references/pricing.md).
5. **Writes the listing**: title in the form `Title Tome N - Author`, and the summary from Chasse aux Livres as the description.
6. **Publishes** on Vinted and Leboncoin with the 4 photos, choosing the right category and shipping size.
7. **Logs** every book in `biblioscan-annonces.csv`, so a batch can be resumed and nothing is listed twice.

### Example

> Publish these books, the photos are in ~/Desktop/photos: 9782909698281, 9782070360024

Worked example for *Aghora Tome 1 - Robert E. Svoboda* (ISBN 9782909698281):

| Source | Value |
|---|---|
| BiblioScan median | 145 € (4 sales / 12 months) |
| Amazon | 153 € (8 offers) |
| Chasse aux Livres | lowest at 148 € |
| Leboncoin | no competitor |
| Vinted | 4 competitors, lowest at 90 € |
| **Published price** | **95 €** on both platforms (our copy is in better condition than the one at 90 €) |

### Requirements

- **An AI agent that supports [Agent Skills](https://agentskills.io)** (`SKILL.md` folders) **and can control a web browser**:

  | Agent | Browser tool |
  |---|---|
  | [Claude Code](https://claude.com/claude-code) | [Claude in Chrome](https://claude.com/chrome) extension |
  | [Codex CLI](https://github.com/openai/codex) | [Playwright MCP](https://github.com/microsoft/playwright-mcp) or [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) |
  | Other agents (Cursor, Gemini CLI…) | Any of the above MCP servers |

- **Signed in to biblioscan.ai, vinted.fr and leboncoin.fr in the browser the agent controls.** The skill never types passwords. Playwright and DevTools MCP use their own browser profile by default, so sign in there once.
- **Python 3.** No extra packages: on macOS, images are converted with the built-in `sips`; elsewhere, Pillow is used if it is installed.

### Installation

```bash
git clone https://github.com/biblioscan/skills.git biblioscan-skills
```

Then copy the skill folder to where your agent looks for skills:

| Agent | Command |
|---|---|
| Claude Code | `cp -r biblioscan-skills/biblioscan-annonce ~/.claude/skills/` |
| Codex CLI | `cp -r biblioscan-skills/biblioscan-annonce ~/.codex/skills/` |
| Other | See your agent's documentation for its skills folder |

Restart the agent. The skill loads automatically whenever you ask to list, price or publish books.

**Browser setup**

- *Claude Code*: install the Claude in Chrome extension and allow it on `biblioscan.ai`, `cal.fr` / `chasse-aux-livres.fr`, `vinted.fr` and `leboncoin.fr`.
- *Codex CLI*: add Playwright MCP to `~/.codex/config.toml`:

  ```toml
  [mcp_servers.playwright]
  command = "npx"
  args = ["@playwright/mcp@latest"]
  ```

### Photos

Take **4 photos per book**: cover, back, spine, and the book open. Any of these layouts works:

```
photos/9782909698281/1.jpg … 4.jpg     # one sub-folder per ISBN
photos/9782909698281_1.jpg …           # ISBN in the file name (ISBN-10 or ISBN-13)
photos/IMG_0001.HEIC …                 # unsorted: the agent matches them to the BiblioScan cover
```

HEIC, PNG and WebP files are converted to JPEG automatically. If the files are named 1 to 4, that order is kept; otherwise the agent finds the cover, back, spine and open-book shots itself.

### Safety

- **Nothing risky gets published.** A book is skipped and marked `à vérifier` in the log when there is no price data, the photos are uncertain, the cover is missing or the computed price looks wrong.
- **No paid options.** Leboncoin upsells ("À la une", "Remonter") are always declined.
- **CAPTCHAs are solved by you.** If a site shows a bot check, the agent pauses and asks you to solve it in the open tab, then resumes.

### Files

```
biblioscan-annonce/
├── SKILL.md                  # workflow
├── references/
│   ├── pricing.md            # pricing rules and condition grid
│   ├── vinted.md             # Vinted form guide
│   ├── leboncoin.md          # Leboncoin form guide
│   └── browser-tools.md      # browser actions mapped per agent and tool
└── scripts/
    ├── prepare_photos.py     # matches photos to ISBNs, converts and resizes them
    └── fetch_metadata.py     # fallback title/summary (Google Books, Open Library)
```

`fetch_metadata.py` is only used when Chasse aux Livres cannot be reached. It needs no setup. If Google Books starts returning rate-limit errors, you can set a free API key:

```bash
export GOOGLE_BOOKS_API_KEY=your_key   # optional
```

### Customizing

The pricing logic lives in [`references/pricing.md`](biblioscan-annonce/references/pricing.md) in plain language. Edit the percentages and rounding rules to match your own strategy.

## License

[MIT](LICENSE): use, modify and redistribute freely, including for commercial use.
