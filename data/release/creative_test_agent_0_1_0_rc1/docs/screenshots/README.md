# Screenshots for Demo / Pitch Deck

Do not auto-generate screenshots. Capture them manually after starting the app and seeding demo data.

## Setup

```bash
uvicorn src.main:app --reload
# In another terminal:
python scripts/seed_demo_data.py
# Open: http://localhost:8000/
```

## Screenshots to Capture

### 1. Dashboard with Closed-Loop Banner

**Route:** `GET /`
**What to show:** Full dashboard including:
- Status banner at top showing "Closed-loop mode: ON · Cloud LLMs: BLOCKED · Provider: stub"
- Entity counts (3 assets, 1 brand, 3 audiences)
- Recent test runs section

**Framing:** Full browser window showing header and dashboard content.

### 2. Creative Assets List

**Route:** `GET /ui/creative-assets`
**What to show:** Table with 3 demo variants (Practical, Freedom, Risky) showing title, type, and creation date.

### 3. New Creative Form

**Route:** `GET /ui/creative-assets/new`
**What to show:** The form with:
- Title field
- Type selector (Text / File upload)
- Text content textarea
- Metadata field (optional)

### 4. Brand Profile Detail

**Route:** `GET /ui/brand-profiles/{id}`
**What to show:** NovaBank profile with tone of voice, target audience, restrictions, and claims policy visible.

### 5. Audience Profiles

**Route:** `GET /ui/audience-profiles`
**What to show:** List of 3 audience profiles with names and segment descriptions.

### 6. Test Run Detail (After Completion)

**Route:** `GET /ui/test-runs/{id}`
**What to show:**
- Status badge: "completed"
- Scorecard table with criteria and scores
- Risks section
- Final recommendation highlighted
- "View Report" button

### 7. Completed Report

**Route:** `GET /ui/reports/{id}`
**What to show:**
- Report metadata (mode, format, version)
- Final recommendation box
- Scorecard table
- Risks and recommendations
- Export links (JSON, Markdown, HTML, Client HTML, PDF Stub)

### 8. HTML Report (Client-Facing)

**Route:** `GET /reports/{id}?format=html&mode=client_facing`
**What to show:** The standalone HTML page with:
- Client-Facing badge
- Clean table layout
- Colour-coded risks and recommendations
- Final recommendation highlighted

**Tip:** Open in a new tab and take a full-page screenshot.

### 9. A/B Comparison Result

**Route:** `POST /ui/compare` (after selecting 2 completed runs)
**What to show:**
- Winner or "No Clear Winner" box with rationale
- Score deltas table
- Variant summaries with strengths and weaknesses
- Recommendation

## Stitching the Pitch Deck

Suggested order for a client deck:

1. Dashboard with closed-loop banner → establishes trust.
2. Creative assets list → shows what can be tested.
3. Brand profile + audience profiles → shows strategic setup.
4. Test run detail with scorecard → shows analytical depth.
5. A/B comparison → shows decision support.
6. Client-facing HTML report → shows deliverable quality.
