# <Your Name> — application profile

Run `/setup` and Claude will fill this in with you. Source of truth for work history/skills is your resume PDF (path in `profile/answers.json` → `resume_path`, read live, never copied here). This file holds everything the resume doesn't. `profile/answers.json` mirrors the short answers for the Greenhouse script, so keep both in sync.

## Contact
- Name on applications (legal first name):
- Preferred name (only if a form requires it):
- Email:
- Phone:
- LinkedIn:
- GitHub / website:
- Current location (City, ST):
- Street address (only fill if a form requires it):

## Work authorization
- Citizenship / status:
- Authorized to work in the US:
- Requires visa sponsorship now or in the future:

## EEO / demographic questions (voluntary)
Anything left blank → "I don't wish to answer" / "Decline to self-identify".
- Gender:
- Hispanic/Latino:
- Race/ethnicity:
- Sexual orientation:
- Disability status:
- Veteran status:
- Age range:
- Transgender / other community questions:

## Standard answers
- Past employers (for "have you worked here before"):
- Notice period / earliest start:
- "Current company":
- "Current or most recent company":
- Willing to relocate:
- OK with onsite / hybrid:
- Years of professional experience:
- Security clearance:
- Salary expectations:
  - Optional field: leave blank.
  - Free-text field: "Open / negotiable, based on market rate for the role and total compensation."
  - Numeric field required and posting lists a range: a figure in the upper half of the posted range.
  - Numeric field required and no range posted: STOP and ask.
  - Never volunteer current or past salary.
- "How did you hear about us": the source matching the URL; otherwise "Job board" or "Other". Never claim a referral.

## Education details (for forms)
- School, degree, major, dates:
- School name as it appears in picklists (Greenhouse / Workday), filled in as you discover them:
- GPA:
- Test scores (SAT/ACT/GRE), only if you want them used:

## Certifications
Put certificate PDFs in `profile/certs/` and list each here: exact name, issuer, issued/expiry dates, certification number, file name.

## Conflict-of-interest / background screening questions
- Default answer: No (not related to employees, no non-compete, not a government official, etc.). Change if any apply to you.

## Rules for free-text answers
- Only use facts from the resume or this file. Never invent experience, metrics, or skills.
- If a question isn't covered, ask, then add the answer here.
