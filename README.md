# Hookline

**Voice companion platform — scaffold (in progress)**

A derivative product scaffold, building on selected elements from the Yapper Care ecosystem. Not a Yapper rebrand — a separate product with its own positioning, brand, and stack choices.

**Status:** Scaffold only. No production code yet. See `ARCHITECTURE.md` for the design intent and `docs/prerequisites.md` for the dependency graph.

## What this repo will be

A programmatic API + simple dashboard for deploying voice AI companions. Positioned for **non-clinical** use cases (general wellness, social connection, daily check-ins).

**Hard rules (carried over from Yapper Care):**
- NO clinical efficacy claims
- NO treatment / cognition / brain-health positioning
- NO references to specific Yapper customers, caregivers, or facilities
- NO Yapper trademark strings

## Layout

```
hookline/
├── README.md           (this file)
├── ARCHITECTURE.md     (design intent)
├── LICENSE             (BSD-3-Clause)
├── .gitignore
├── src/                (placeholder Python + TypeScript)
├── docs/
│   ├── prerequisites.md
│   └── architecture-decisions.md
└── .github/
    └── workflows/
        └── ci.yml
```

## Next steps

See `docs/prerequisites.md`.

## Vault

- `autonobrain/70 - System/hookline-prerequisites-2026-08-13.md` (prerequisites + blockers)
- `autonobrain/70 - System/hookline-credentials-2026-08-13.md` (credentials matrix — NO secrets)
- `autonobrain/70 - System/hookline-repo-inspection-2026-08-13.md` (Yapper repos inspection)

## Source repos inspected

- https://github.com/AutonoLabs/yapper-care (Chung's mainline)
- https://github.com/AutonoLabs/yapper-brand (brand + marketing)
- https://github.com/AutonoLabs/yapper-website (public marketing site)
- https://github.com/AutonoLabs/yapper-care-backend (post-processing API)
- https://github.com/AutonoLabs/yapper-care-spa (React SPA)
- https://github.com/AutonoLabs/yapper-app (go.yapper.care companion app)

Inspected clones live at `/Users/elibernstein/Code/hookline-source/`.

## Maintainer

Eli Bernstein (`capitelist@elibernstein`)