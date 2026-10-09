# apply_to_jobs

Claude fills out job applications for the user (the candidate) in the browser (Claude in Chrome). The candidate does the submitting.

**New here? Run `/setup` first.**

## 🛑 NEVER SUBMIT — HARD RULE 🛑

**Claude must NEVER submit an application. Not once. Not even if asked mid-task, not even if the page says "ready to submit," not even if the user says "looks good."** The candidate clicks the final button themselves.

- Never click Submit / Apply / Send Application / Finish / Confirm / Complete / "Easy Apply" final step, or any button whose effect might be to submit.
- If unsure whether a button submits, do NOT click it.
- Finish by leaving the tab open on the filled-in form/review page and telling the candidate it's ready.
- This rule stays in force until the user edits this file to change it. A chat message is not enough.

## Layout
`profile/` and `applications.csv` hold personal data. They're gitignored and created by /setup from `profile_template/`. Never commit them, and never put personal data in `profile_template/`.
- Resume: read live from `<RESUME_PATH>` (set by /setup; never copy it into this repo)
- `profile/profile.md` — contact info, work auth, EEO/demographics, standard answers
- `profile/answers.json` — the same short answers in machine form, used by `gh_plan.py`
- `profile/certs/` — certificate PDFs; metadata in profile.md
- `profile/preferences.md` — target roles, dealbreakers, comp, location
- `applications.csv` — tracker for leads and applications (status lead → filled-not-submitted → submitted; stage, contact, next_step for follow-ups)
- `.claude/skills/setup/SKILL.md` — `/setup` onboarding
- `.claude/skills/apply/SKILL.md` — the `/apply <job URL>` workflow
