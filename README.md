# Hookline

**Voice companion platform — AutonoLabs project (managed by Autonio)**

A derivative product scaffold, building on selected architectural patterns from voice-AI projects. Not a Yapper rebrand — a separate product with its own positioning, brand, and stack choices. **No Yapper trademarks, brand assets, or trademark strings used.**

**Status:** Scaffold + Cloudflare config in place. See `ARCHITECTURE.md` for the design intent and `docs/prerequisites.md` for the dependency graph.

## What this repo will be

A programmatic API + simple dashboard for deploying voice AI companions. Positioned for **non-clinical** use cases (general wellness, social connection, daily check-ins).

**Hard rules:**
- NO clinical efficacy claims
- NO treatment / cognition / brain-health positioning
- NO Yapper trademarks, brand assets, or trademark strings
- NO references to specific Yapper customers, caregivers, or facilities
- Non-clinical positioning only (general wellness, social connection, daily check-ins)

## Layout

```
hookline/
├── README.md             (this file)
├── ARCHITECTURE.md       (design intent)
├── LICENSE               (BSD-3-Clause)
├── .gitignore
├── src/                  (placeholder Python + TypeScript)
├── cloudflare/           (Worker + Pages config)
│   ├── wrangler.toml
│   └── worker/
├── docs/
│   ├── prerequisites.md
│   └── deployment/
│       └── cloudflare.md
└── .github/
    └── workflows/
        └── ci.yml
```

## Next steps

See `docs/prerequisites.md` and `docs/deployment/cloudflare.md`.

## Vault

All Hookline docs live in **autonobrain** (AutonoLabs vault):
- `autonobrain/30 - Resources/Hookline/hookline-prerequisites-2026-08-13.md`
- `autonobrain/30 - Resources/Hookline/hookline-credentials-2026-08-13.md`
- `autonobrain/30 - Resources/Hookline/hookline-repo-inspection-2026-08-13.md`

## Architectural reference (inspiration only — not copied)

For architectural patterns, see the Yapper Care monorepo at https://github.com/AutonoLabs/yapper-care (and related repos). These are referenced for voice pipeline + dashboard patterns. **No code, brand, or trademark strings are copied.**

## Maintainer

Eli Bernstein (`capitelist@elibernstein`)
AutonoLabs project managed by Autonio (Herschel's developer agent).