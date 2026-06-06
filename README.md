# SortResume 💎

> Find real candidates in a world of AI noise.

**Global B2B SaaS** for HR firms and staffing agencies.

## What Makes This Different

Every ATS tool measures keyword overlap. SortResume measures **4 signals**:

| Signal | Weight | What it detects |
|---|---|---|
| Semantic Match | 35% | Meaning — "ML Eng" = "Machine Learning Developer" |
| Keyword Match | 25% | Section-weighted TF-IDF |
| Substance Score | 25% | Keywords proven with outcomes + metrics |
| AI Noise Score | 15% | Detects ChatGPT-generated resume padding |

## Project Structure

```
SortResume/
├── engine/                 # Accuracy layer — built first, tested first
│   ├── parser/             # PDF parsing + section detection
│   ├── scorer/             # 4-signal hybrid scorer
│   └── signals/            # Individual signal implementations
├── api/                    # FastAPI backend
│   ├── routers/            # Endpoints
│   ├── services/           # Business logic
│   ├── models/             # Pydantic schemas
│   └── core/               # Config, database, auth
├── streamlit_app/          # Frontend UI
│   ├── pages/              # Multi-page app
│   └── components/         # Reusable components
└── tests/                  # Accuracy-first test suite
    ├── unit/               # Per-signal tests
    ├── integration/        # End-to-end tests
    └── fixtures/           # Real resume + JD test pairs
```

## Accuracy Target (must pass before any UI ships)
- Spearman correlation > 0.75 with human recruiter rankings
- AI noise precision > 85%
- Section detection accuracy > 90% on 50 diverse PDFs

## Build Order
```
Layer 1: PDF parser + section detector  ← START HERE
Layer 2: JD parser
Layer 3: 4 scoring signals
Layer 4: Calibration
Layer 5: AI noise detector
Layer 6: Integration + explainability
Layer 7: FastAPI layer
Layer 8: Streamlit UI
```

**Nothing ships until scorer passes accuracy tests.**
