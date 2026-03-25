# HSC Quiz PWA + AI Agent

Auto-updating HSC practice quizzes. The AI agent watches NESA nightly and
adds new subjects automatically. Students install it on their phone like an app.

---

## What's included

| File | What it does |
|------|-------------|
| `index.html` | The quiz app (works on any device) |
| `manifest.json` | Makes it installable as a phone app |
| `sw.js` | Allows offline use |
| `agent.js` | The AI that fetches new papers and generates questions |
| `subjects/` | One JSON file per subject — agent adds these automatically |
| `.github/workflows/agent.yml` | Runs the agent every night automatically |

---

## Setup (beginner-friendly, ~20 minutes)

### Step 1 — Put the app on GitHub Pages (free hosting)

1. Go to [github.com](https://github.com) and create a free account
2. Click **New repository**, name it `hsc-quiz`, make it **Public**
3. Upload all these files (drag and drop works)
4. Go to **Settings → Pages → Source** and select **main branch**
5. Your app is now live at `https://YOUR-USERNAME.github.io/hsc-quiz`

### Step 2 — Add your Anthropic API key (so the agent can run)

1. Get a key at [console.anthropic.com](https://console.anthropic.com)
2. In your GitHub repo, go to **Settings → Secrets → Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`, Value: paste your key
5. Save

### Step 3 — The agent runs automatically every night

That's it! GitHub Actions will run `agent.js` every night at 11pm Sydney time.
When it finds new NESA papers, it generates questions and pushes them to your repo.
GitHub Pages then automatically updates — students see new subjects next time they open the app.

### Run the agent manually anytime

Go to **Actions → HSC Quiz Agent → Run workflow** to trigger it immediately.

---

## How to install the app on your phone

**Android:**
1. Open Chrome and go to your GitHub Pages URL
2. Tap the three dots menu → **Add to Home screen**
3. Tap **Install** — done!

**iPhone:**
1. Open Safari and go to your GitHub Pages URL
2. Tap the Share button (box with arrow)
3. Scroll down and tap **Add to Home Screen**
4. Tap **Add** — done!

The app works offline once installed.

---

## How to add a subject manually

Drop a JSON file in `subjects/` following this format:

```json
{
  "id": "chemistry-2024",
  "name": "Chemistry",
  "icon": "⚗️",
  "accentColor": "#6af7c8",
  "isNew": true,
  "year": "2024",
  "questions": [
    {
      "year": "HSC 2024",
      "text": "Your question here?",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "explanation": "Why A is correct..."
    }
  ]
}
```

Then add the filename to `subjects/index.json`:
```json
[
  { "file": "chemistry-2024.json" },
  { "file": "mathematics-advanced-2024.json" }
]
```

Commit and push — the app updates automatically.
