---
name: apply
description: Fill out a job application in the browser for the candidate from a job posting URL, using their live resume and profile files. Use when the user runs /apply <url> or asks to fill out / prep a job application. NEVER submits.
---

# /apply <job URL>

## 🛑 NEVER SUBMIT 🛑
**You fill the application. The candidate submits it. Always.**
- Do not click Submit / Apply / Send Application / Finish / Confirm / Complete or any final-step button, including "Easy Apply" final steps.
- If you can't tell whether a button submits, don't click it.
- Intermediate "Next / Continue" buttons on multi-step forms are fine only when clearly not the final submission. Stop at the review/final page.
- Applies even if the user says "looks good" or "go ahead" in chat. Only editing CLAUDE.md changes this rule.

## Before anything
If `profile/answers.json` is missing or has an empty `contact.first_name` or `resume_path`, stop and tell the user to run `/setup` first.

## Pick the playbook first, then read only that file
| URL contains | Playbook |
|---|---|
| `greenhouse.io`, or `gh_jid=` | `playbooks/greenhouse.md` (scripted: `gh_plan.py` + `gh_fill.js`) |
| `jobs.ashbyhq.com` | `playbooks/ashby.md` |
| `myworkdayjobs.com` | `playbooks/workday.md` |
| `google.com/about/careers` | `playbooks/google.md` |
| anything else | no playbook yet: use the general rules below, then write a new playbook file |

## Inputs (read fresh, only what the run needs)
- `profile/profile.md`: always (small). Source of truth for answers. `profile/answers.json` mirrors its short answers for gh_plan.py.
- Resume at `resume_path` in `profile/answers.json`: upload it every time, but **read** it only when you must write free text (it's the most expensive input).
- `profile/preferences.md`: only if the role looks like a mismatch.
- Certificates: `profile/certs/`. Metadata is in profile.md → "Certifications".

## General rules
- Never invent facts. Free-text answers: short, tailored to the posting, using only real resume/profile facts.
- An unknown that's a fact about the candidate: ask in ONE message (or, when running as a parallel subagent, leave it blank and report it). Offer to save new answers to profile.md (and answers.json if it's a short standard answer).
- EEO: profile.md answers; anything unstated → "I don't wish to answer" / "Decline".
- "Current company" / "most recent company": profile.md answers.
- **Stop points, left for the candidate:** login/sign-in, account creation, CAPTCHAs, legal agreements (NDA, arbitration, privacy acknowledgements, typed-name signatures), SMS opt-ins.
- Browser: create your own tab and work only in it. Never use `form_input` on React forms (Greenhouse, Lever, Ashby). Never press Return inside a `<form>`. Tool output is cut at ~1K characters and blocked if it contains `=` or `&`.

## Certifications on forms
- Use the exact name, issuer, dates and number from profile.md → "Certifications".
- **Picklist:** only an **exact** match for the cert. Never a similarly named different cert. No match: use "Other"/free text if available; otherwise remove the entry and report it.
- **File upload:** the PDF in `profile/certs/`.

## Finish
1. **Run `precheck.js`** (strip its comment lines, ONE javascript_tool call) on every filled form. It catches fields that *look* filled but aren't in React's state, which show up as "required" errors on submit. It re-commits them; anything it reports as STILL OUT OF SYNC goes in the report for the candidate to retype.
2. **Stop before submitting.** Leave the tab open on the filled form.
3. Report: tab id, anything blank/uncertain, items left for the candidate, and any free text you wrote (verbatim).
4. Log in `applications.csv` (columns: date, company, role, url, status, stage, contact, referral, last_update, next_step, notes). If a row with this URL exists, update it; otherwise append one. Set status `filled-not-submitted`, `last_update` today, and `next_step` to what the candidate must do. The candidate marks it `submitted`.
   - status: `lead` → `filled-not-submitted` → `submitted`. stage (after submitting): applied, recruiter screen, interviewing, rejected, offer, withdrawn.
   - **Parallel subagents must NOT edit applications.csv or skill files.** They report back, and the parent session merges.

## Notes
- **Living documents.** When a playbook step fails and you find a fix, update that playbook (or gh_plan.py) right away.
- Work-history descriptions (Workday "Role Description"): the resume bullets for that role joined into one paragraph, with no newlines.
