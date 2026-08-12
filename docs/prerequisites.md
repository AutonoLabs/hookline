# Hookline — Prerequisites & blockers

**Status:** Pending Eli sign-off.

---

## What's ready

✅ Repo created at https://github.com/AutonoLabs/hookline
✅ README + ARCHITECTURE drafted
✅ Yapper Care repos cloned to `/Users/elibernstein/Code/hookline-source/` for reference
✅ License: BSD-3-Clause
✅ Org: AutonoLabs

## What Eli needs to decide / do

### Blockers

| # | Question | Default | Action |
|---|---|---|---|
| 1 | **Domain** — what's the actual domain? `hookline.io`, `hookline.ai`, `gethookline.com`, `usehookline.com`? | `hookline.io` | Eli picks + registers |
| 2 | **Brand identity** — name only, or full visual identity (logo, palette, typography)? | Name only for now | Eli commissions brand or uses placeholder |
| 3 | **Pricing model** — per-seat, per-call, per-companion, freemium + paid tiers? | Per-companion ($X/mo/companion + usage) | Eli decides |
| 4 | **Initial customer** — self-serve developers, or B2B sales-led? | Self-serve | Eli decides |
| 5 | **LLM provider** — OpenAI Realtime primary, or Anthropic/Gemini? | OpenAI Realtime | Eli confirms |
| 6 | **Twilio account** — already have one? New one? | New one (separate from Yapper) | Eli creates |
| 7 | **Stripe account** — already have one? | New one (separate from Yapper) | Eli creates |
| 8 | **Voice provider** — Twilio direct, VAPI managed, or Dograh self-host? | Twilio direct first, VAPI for v2 | Eli picks |
| 9 | **First feature** — what ships in alpha? Voice + dashboard only? Or voice + CRM integration? | Voice + dashboard only | Eli confirms scope |
| 10 | **Customer target** — who is the first customer? | Indie devs + small BPOs | Eli confirms |

### Things Eli needs to provide

- **Domain registration** — hookline.io (or whatever the chosen name is)
- **Cloudflare account** — for DNS + email (use existing CF account)
- **Twilio account** — sign up, get Account SID + Auth Token + phone number
- **OpenAI / Anthropic / Gemini API key** — for LLM
- **Stripe account** — for billing
- **Sentry account** (optional) — for error tracking
- **Postgres host** — Vercel Postgres, Supabase, Neon, or self-host

### Things to verify with Motio/Lex (legal)

- **Trademark clearance** for "Hookline" — Motio runs a search
- **Open-source license compatibility** — any BSD/Apache/GPL code we're borrowing from Yapper repos?
- **Domain squatter check** — is hookline.io actually available?
- **Privacy policy + ToS** — who drafts?
- **Data handling** — what country? GDPR/CCPA/PIPEDA scope?

## What's in flight

- ⚙️ **Herschel is writing the credentials matrix** — see `autonobrain/70 - System/hookline-credentials-2026-08-13.md`
- ⚙️ **Herschel is writing the Yapper repo inspection report** — see `autonobrain/70 - System/hookline-repo-inspection-2026-08-13.md`
- ⚙️ **Herschel is drafting the architecture decisions log** — to be appended to ARCHITECTURE.md

## What's next (after Eli answers the 10 blockers)

1. **Autonio** — wire up the chosen stack (FastAPI + Pipecat + Twilio)
2. **Motio** — trademark search + legal entity setup
3. **Herschel** — operational infrastructure (Cloudflare DNS, Bitwarden items, cron monitoring)
4. **Yappio** — marketing site (clone yapper-website but new brand)
5. **Scott** — market research + accelerator outreach (if applicable)

## Time estimate

- Domain + Twilio + Stripe + API keys: 1 day
- Scaffold + initial API: 1 week
- Alpha release: 2-3 weeks (if Eli is hands-on)
- Public beta: 4-6 weeks

## Vault

- This file (in hookline repo)
- `autonobrain/70 - System/hookline-prerequisites-2026-08-13.md` (mirror)