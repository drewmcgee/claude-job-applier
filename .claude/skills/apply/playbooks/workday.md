# Workday playbook (myworkdayjobs.com)
This flow is multi-step: My Information, My Experience, Application Questions 1 and 2, Voluntary Disclosures, Review. It needs you to sign in first. Pick "Apply Manually".
- **Advancing pages:** "Save and Continue" (`[data-automation-id=pageFooterNextButton]`) is OK to click, but only after checking its text is "Save and Continue" or "Next". Never click on the Review page.
- **Text inputs:** the JS value setter does NOT stick (it shows, but the page reports "required"). Use JS `focus()` + `select()` by id, then a real `computer type`. Batch all fields in one call.
- **Button dropdowns** (`button[aria-haspopup]`): JS `.click()` the button, then JS `.click()` the `[role=option]` with exact text. Many can be done in ONE `javascript_tool` call with an async helper, clicking outside between them because a stale open menu makes the next one read the wrong options. Option wording is often long ("Yes, I would consider relocating for this role"), so list the options first if an exact match fails.
- **Search/prompt fields** (School, Field of Study, Certification, Country phone code): type, `Return` (runs the search), wait 2, `Down` (moves focus to the first result), then check which result is highlighted (zoom or read `document.activeElement`). Press `Down` again until the exact match is highlighted, then `Return`.
  - JS or ref clicks on results do NOT register.
  - **Return selects whatever is highlighted**, which is how a wrong certification got picked. Always verify the highlighted text first.
  - Return is only safe because Workday pages have no `<form>`. Check that `document.querySelectorAll('form').length` is 0 before using it.
  - School naming is odd (e.g. "The University of California, Santa Barbara"). Search a distinctive part of the name, pick the exact match, and record the picklist name in profile.md.
- **Dates:** separate inputs `<id>-dateSectionMonth-input` / `-dateSectionYear-input`. Focus each and type digits ("10", "2024").
- **Repeatable sections** (Work Experience, Education, Certifications, Websites): click the section's "Add" / "Add Another" button by JS, then re-scan to get the new ids (e.g. `workExperience-28--jobTitle`). Delete an unneeded entry with the "Delete" button under its "<Section> N" heading.
- **Questions:** labels aren't linked to their fields. Read each question's text by walking up from the field to the nearest `label`, `legend` or rich-text element.
- **Verify** with short JS reads per field. Use a zoomed screenshot only for search fields, where the chosen value is hard to read from the DOM.
