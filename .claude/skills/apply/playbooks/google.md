# Google Careers playbook (google.com/about/careers/applications)
Steps: Careers profile, Role information, Voluntary self-identification, Review & apply. "Next" is safe; **"Apply" on Review is the submit button**.
- The Careers profile (resume, work history, skills, cover letter) carries over from past Google applications and may be stale. Always read it on the Review page and flag anything wrong: an old resume, a cover letter written for another role, wrong dates.
- Radios: a JS `.click()` on `input[type=radio]` (matched by label text) works. Inputs from earlier steps stay in the DOM, so match by label, not by index.
- Race checkboxes (`li[role=option]`): JS click does NOT register. Use a real `computer left_click` on the box, then verify `aria-selected`.
