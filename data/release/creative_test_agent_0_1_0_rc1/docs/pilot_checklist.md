# Pilot Checklist

## Technical Readiness

- [ ] `pytest` passes (all tests, no failures)
- [ ] `uvicorn src.main:app --reload` starts without errors
- [ ] `GET /` returns 200 (UI dashboard)
- [ ] `GET /health` returns 200
- [ ] `GET /llm/health` returns 200
- [ ] Local-only banner visible on dashboard:
  - Closed-loop mode: ON
  - Cloud LLMs: BLOCKED
  - Provider: stub
- [ ] Stub mode works (no local LLM required)
- [ ] Optional: local LLM (Ollama/LM Studio) works if configured
- [ ] All UI pages load (assets, brands, audiences, runs, compare)

## Demo Data Readiness

- [ ] `python scripts/seed_demo_data.py` completes successfully
- [ ] Brand profile "NovaBank" exists
- [ ] 3 audience profiles exist (Beginner Freelancer, Experienced Self-Employed, Skeptical Small Business Owner)
- [ ] 3 creative variants exist (A — Practical, B — Freedom, C — Risky)
- [ ] Default rubric exists with 8 criteria
- [ ] Test run can be created and completed for each variant
- [ ] Report can be generated for each completed run
- [ ] A/B comparison works with 2+ completed runs
- [ ] Client-facing HTML report renders correctly

## Client Conversation Checklist

- [ ] Clarify what types of creatives the client typically produces
  - Text ads, social media posts, video scripts, landing pages, etc.
- [ ] Clarify which file formats the client uses
  - .txt, .md, .pdf, .png, .jpg, .webp — all supported
  - .docx, .pptx, .psd, .ai — **not yet supported**
- [ ] Clarify expected report structure
  - Internal (detailed, critical) vs client-facing (polished)
- [ ] Clarify local deployment environment
  - Single laptop, agency server, or client infrastructure
- [ ] Clarify security / NDA requirements
  - All processing is local — no data leaves the machine
- [ ] Clarify who will use the tool
  - Account managers, creative directors, strategists, or clients directly
- [ ] Clarify whether a real local LLM is required for pilot
  - Stub mode: works immediately, scores are deterministic
  - Ollama: requires local installation, realistic scoring
  - LM Studio: requires local installation, realistic scoring
- [ ] Discuss which LLM model fits the client's language and market
  - Russian-language creatives may need a Russian-capable model

## Known Limitations to Discuss

- [ ] No production authentication (local use only in current MVP)
- [ ] No real video analysis (video_stub placeholder only)
- [ ] Image OCR not implemented (text in images not extracted)
- [ ] PDF extraction works for text PDFs only (not scanned documents)
- [ ] All data is in-memory — resets on server restart
  - Acceptable for demo; persistent storage is a planned upgrade
- [ ] No real PDF export (pdf_stub placeholder)
- [ ] UI is desktop-only (not mobile-responsive)

## Notes

```
Use this space for custom notes during the pilot conversation.
```
