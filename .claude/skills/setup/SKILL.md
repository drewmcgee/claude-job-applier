---
name: setup
description: One-time onboarding for a new user of this job-application kit. Reads their resume, interviews them, and fills profile/profile.md, profile/preferences.md, profile/answers.json and CLAUDE.md. Use when the user runs /setup or says they're new / want to set up their profile.
---

# /setup

Goal: after this, `/apply <url>` works for this person with no further edits.

0. **Create your private copy:** if `profile/` doesn't exist, copy `profile_template/` to `profile/` and move `profile/applications.csv` to `./applications.csv`. Both are gitignored, so personal data never gets committed. Only ever edit `profile/`, never `profile_template/`.
1. **Resume.** Ask for the full path to their resume PDF (suggest keeping it outside this folder, e.g. `~/Documents/resume/`, so updates are picked up live). Read it. Write the path to `answers.json` → `resume_path`, replace `<RESUME_PATH>` in `CLAUDE.md`, and add the resume's folder to `.claude/settings.local.json` → `permissions.additionalDirectories` (create the file if missing).
2. **Prefill** everything the resume gives you: name, email, phone, LinkedIn/GitHub, location, education (school, degree, major, dates), most recent employer, years of experience, certifications.
3. **Interview** for the rest with AskUserQuestion (batch up to 4 questions per call; keep it to a few rounds). Confirm the prefilled facts at the same time.
   - Legal first name for forms vs. preferred name
   - Work authorization, sponsorship, US citizen / US person
   - Currently employed? (sets "current company" and "most recent company")
   - Relocation, onsite/hybrid, earliest start / notice period
   - Security clearance history
   - EEO answers (gender, Hispanic/Latino, race, veteran, disability, orientation, age range). Say clearly these are voluntary and "prefer not to answer" is fine for any of them.
   - Target roles, seniority, locations, dealbreakers (for preferences.md)
   - Any certifications: ask them to drop the PDFs into `profile/certs/`
4. **Write** `profile/profile.md` (human-readable, keep the template's sections and salary rules), `profile/preferences.md`, and `profile/answers.json`:
   - `contact`: phone as digits only.
   - `greenhouse_standard`: `candidate-location` as {"s": "City, State full name", "v": "City, State full name, United States"}; `school--0` as {"s": distinctive search text, "v": the school's Greenhouse option label, a best guess fixed on first real run}; degree e.g. "Bachelor's Degree"; month names and 4-digit years. Remove the education keys if they have no degree.
   - `answers` / `eeo`: lists of option labels in preference order, e.g. `["Yes"]`, `["Male", "Man"]`, `["I am not a protected veteran", "No"]`; text for companies/zip/city/start date. Use null for anything they declined or that should be decided per form (EEO null → "decline to answer").
5. **Verify:** run `python3 .claude/skills/apply/gh_plan.py https://job-boards.greenhouse.io/vercel/jobs/5798406004` (any open Greenhouse job works). Show them the answered lines and fix anything wrong.
6. Tell them: install Claude in Chrome, then run `/apply <job URL>`. Claude fills, they submit.
