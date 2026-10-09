# Greenhouse playbook (v3): 1 Bash call + 3 browser calls, one tiny screenshot, no keystrokes

Tested on forms with education, multi-select EEO, checkboxes and async location: every field set, verified in the same call.
Applies to job-boards.greenhouse.io, boards.greenhouse.io, embed `job_app?for=`, and company pages with `?gh_jid=`.

## 1. Plan (Bash, no browser)
`python3 .claude/skills/apply/gh_plan.py "<job URL>"`
- It resolves the board (including `gh_jid` company pages), prints `CLOSED` if the posting is gone, prints pay, then lists every question with its auto-answer:
  - `-> value`: answered from profile/answers.json (contact, work auth, sponsorship, "worked here before", relocation, EEO, education, location).
  - `-> TODO`: you decide from profile.md / resume (years-of-experience buckets, "how did you hear", free text).
  - `-> YOU`: consent, privacy, arbitration, SMS opt-in. Leave these for the candidate (stop point).
- Resolve TODOs by rerunning with `--set ID=VALUE` (repeatable): text, an exact option label, `a|b` for multi-select or checkboxes, `search>>label` for an async select. Use `--leave ID` to drop an auto-answer.
- Rerun is cheap (one API call). Spot-check the auto-answers; if a rule is wrong, fix `profile/answers.json` (or the regexes in gh_plan.py) rather than patching per run.
- Read the resume PDF **only** if there are free-text questions to write. Most Greenhouse forms have none.

## 2. Open + hydrate + find (ONE `browser_batch`)
`tabs_context_mcp` + `tabs_create_mcp` first (outside the batch), then:
`navigate` to the `OPEN` URL → `computer screenshot` with `scale: 0.1` → `find` "Resume/CV file input".
- **The screenshot is required.** Background tabs never hydrate React (Remix waits for a visible frame), and without hydration nothing can be set. A 0.1-scale shot activates the tab for an instant and costs almost nothing. Once hydrated, the tab can go back to the background.
- If the screenshot fails with "Cannot access a chrome-extension:// URL", retry it.

## 3. Upload + fill + verify (ONE `browser_batch`)
`file_upload` the resume onto the ref from step 2 → `javascript_tool` with the script gh_plan.py printed, **verbatim**.
- Output: `done N/M set, resume attached`, then only problems:
  - `x id: why`: a value didn't take (e.g. no option with that label; the message lists the available options).
  - `! id label`: a required field is still empty (expected for YOU items).
- `NOT HYDRATED` means the screenshot didn't happen. Take it and rerun the same script.
- Fix any `x` with `--set` and rerun the script (it's idempotent). Conditional fields that appear after an answer are covered by the script's second pass.

That's it. Don't scan the page, don't read the job text in the browser, don't take more screenshots.

## How gh_fill.js works (for debugging)
- Selects: walks the React fiber from the input to react-select's instance and calls `selectOption(option)`, which is the same code path as a user click.
  - Async selects (school, degree, discipline): calls the wrapper's `loadOptions(search)`.
  - Location: calls `onInputChange(search)` and polls `props.options`.
- Matching is exact first, then prefix ("Male" never matches "Female").
- Text: native value setter plus input/change/blur events. Checkboxes/radios: `.click()` by label.
- Waits use MessageChannel ticks, because `setTimeout` is throttled to ≥1s in background tabs.
- Synthetic mouse/key/focus events do NOT open react-select menus in an unfocused window. That's why the v2 playbook needed real keystrokes; v3 avoids menus entirely.

## Form facts
- Demographic question ids from the API (`864`, `605`, ...) equal the DOM ids. Compliance (EEOC) fields use names like `gender`, `race`, `veteran_status`.
- Page-standard fields not in the API: `country` (phone code, "United States +1"), `candidate-location`, and education `school--0`, `degree--0`, `discipline--0`. Education ids missing from a form are skipped quietly.
- School: set `school--0` in answers.json as {"s": search text, "v": exact option label}, e.g. {"s": "Santa Barbara", "v": "University of California - Santa Barbara"}. Degree e.g. "Bachelor's Degree".
- Some forms repeat every custom question in two blocks with different ids. gh_plan lists both; answer both.
- `g-recaptcha-response-*` is the invisible reCAPTCHA. Ignore it; you may get a challenge when you submit.
- Tool output is cut at ~1K characters, and output containing `=` or `&` is blocked. gh_fill already strips those.
- Never use `form_input` on Greenhouse (it reports success but nothing sticks), never click options by coordinates, never press Return in a form.
