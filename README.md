# apply_to_jobs

Claude Code fills out job applications in your Chrome. You review and submit. It never submits for you.

## Setup (about 10 minutes)
1. Install [Claude Code](https://claude.com/claude-code) and the **Claude in Chrome** extension, and sign in to both.
2. Clone this repo, e.g. into `~/workplace/apply_to_jobs`.
3. `cd` into it, run `claude`, then type `/setup`. Claude reads your resume, asks you a few rounds of questions, and fills in `profile/`.

## Use
- `/apply <job posting URL>`: Claude opens a tab, fills the form, uploads your resume, and stops. You check it and click Submit.
- Login pages, CAPTCHAs, legal agreements and SMS opt-ins are left for you.
- Every application is logged in `applications.csv`. Mark it `submitted` once you've sent it.
- Best support is for Greenhouse (fully scripted), then Ashby, Workday and Google Careers. Other sites work, but more slowly.

## Your data
Everything about you lives in `profile/` and `applications.csv` on your computer. Your resume stays where you keep it and is read from there each time. `profile/`, `applications.csv`, PDFs and `.claude/settings.local.json` are in `.gitignore`, so they stay out of git. `profile_template/` holds only blank templates.
