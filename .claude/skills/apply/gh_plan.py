#!/usr/bin/env python3
"""Greenhouse planner: no browser needed.

    python3 gh_plan.py <job URL> [--set ID=VALUE ...] [--leave ID ...]

Prints the form URL to open, open/closed status, pay, every question with its auto-answer (or TODO / YOU),
then the ready-to-run gh_fill.js with the answers injected (pass it verbatim as ONE javascript_tool call).
--set overrides or adds an answer: plain text, an exact option label, "a|b" for multi, or "search>>label" for async selects.
--leave drops an answer, so the field is left for you.

Auto-answers come from profile/answers.json (filled by /setup). Keep it in sync with profile/profile.md.
"""
import html, json, re, sys, urllib.request, urllib.parse
from pathlib import Path

DECLINE_ = ["I don't wish to answer", 'I prefer not', 'Prefer not', 'Decline']

CFG_PATH = Path(__file__).resolve().parents[3] / 'profile' / 'answers.json'
try:
    CFG = json.loads(CFG_PATH.read_text())
except Exception as e:
    sys.exit(f'Cannot read {CFG_PATH} ({e}). Run /setup first.')
PROFILE = CFG['contact']
if not PROFILE.get('first_name') or not PROFILE.get('email'):
    sys.exit('profile/answers.json is not filled in yet. Run /setup first.')
# Page-standard fields (not in the API). gh_fill skips the education ones quietly when a form has no education section.
STANDARD = {k: v for k, v in CFG.get('greenhouse_standard', {}).items() if v not in (None, '', {})}
A_ = CFG.get('answers', {})
# (label regex, answer key in answers.json). First match wins.
# CANDIDATE means always leave it for the candidate (legal or consent items). A missing/null answer means TODO.
CANDIDATE = object()
RULES = [
    (r'privacy|acknowledg|consent|arbitration|attest|certify|agree|signature|communications|sms|whatsapp|text messages', CANDIDATE),
    (r'linkedin', PROFILE.get('linkedin')),
    (r'github|website|portfolio', PROFILE.get('github') or PROFILE.get('website')),
    (r'u\.?s\.? person|export control|u\.?s\.? citizen', A_.get('us_person')),
    (r'legally authori[sz]ed|authori[sz]ed to work|eligible to work|right to work', A_.get('work_authorized')),
    (r'sponsor', A_.get('needs_sponsorship')),
    (r'(worked|employed|work).{0,40}(before|previously|currently|ever|in the past)|(previously|ever|currently).{0,30}(work|employ)|former employee|have you (been employed|worked) (by|at|for)', A_.get('worked_here_before')),
    (r'relocat', A_.get('willing_to_relocate')),
    (r'on-?site|in-?office|in office|hybrid|in person|commut|days (a|per) week', A_.get('onsite_ok')),
    (r'clearance', A_.get('security_clearance')),
    (r'non-?compete|related to|relative|family|government official|sanction|outside (business|activit)|conflict', A_.get('conflict_questions')),
    (r'(most recent|last|previous).{0,15}(company|employer)|(company|employer).{0,25}(most recent|last)', A_.get('most_recent_company')),
    (r'current.{0,25}(company|employer)', A_.get('current_company')),
    (r'(earliest )?start date|notice period|when can you start', A_.get('start_date')),
    (r'docker|kubernetes|big data|spark|hadoop', A_.get('docker_k8s_bigdata')),
    (r'^\s*(zip|postal)', A_.get('zip')),
    (r'^\s*(city|location)\b', A_.get('city')),
]
EEO_KEYS = [  # demographic / EEOC label regex -> answers.json eeo key
    (r'transgender', 'transgender'), (r'gender|^sex', 'gender'), (r'hispanic|latin', 'hispanic_latino'),
    (r'race|ethnic', 'race'), (r'veteran|military', 'veteran'), (r'disab', 'disability'),
    (r'orientation', 'sexual_orientation'), (r'\bage\b', 'age_range'),
]
EEO = [(rx, CFG.get('eeo', {}).get(k) or DECLINE_) for rx, k in EEO_KEYS]
DECLINE = DECLINE_

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', 'replace')

def api(board, jid):
    try:
        return json.loads(get(f'https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{jid}?questions=true'))
    except Exception:
        return None

def resolve(url):
    u = urllib.parse.urlparse(url); q = urllib.parse.parse_qs(u.query)
    m = re.search(r'greenhouse\.io/(?:embed/job_app\?for=)?([\w-]+)/jobs/(\d+)', url)
    if m: return m.group(1), m.group(2), False
    if 'for' in q and 'token' in q: return q['for'][0], q['token'][0], True
    jid = (q.get('gh_jid') or q.get('token') or [None])[0]
    if not jid: sys.exit('Cannot find a Greenhouse job id in the URL.')
    host = u.hostname.split('.'); cands = [host[-2], host[-2].replace('-', '')]
    try: cands += re.findall(r'greenhouse\.io/(?:embed/job_board(?:/js)?\?for=|embed/job_app\?for=)?([\w-]+)', get(url))
    except Exception: pass
    for b in dict.fromkeys(c for c in cands if c not in ('embed', 'v1', 'boards')):
        if api(b, jid): return b, jid, True
    sys.exit(f'Board not found for gh_jid {jid}; tried {list(dict.fromkeys(cands))[:6]}. Pass the job-boards URL instead.')

def pick(options, prefs):
    for p in prefs:
        for o in options:
            if o.lower() == p.lower(): return o
        for o in options:
            if o.lower().startswith(p.lower()): return o
    return None

def main():
    args = sys.argv[1:]
    if not args: sys.exit(__doc__)
    url, sets, leaves = args[0], {}, set()
    i = 1
    while i < len(args):
        if args[i] == '--set': k, v = args[i + 1].split('=', 1); sets[k] = v; i += 2
        elif args[i] == '--leave': leaves.add(args[i + 1]); i += 2
        else: sys.exit(f'Unknown arg {args[i]}')
    board, jid, embed = resolve(url)
    d = api(board, jid)
    if not d: print(f'CLOSED: no job {board}/{jid} on boards-api (404).'); return
    form = f'https://job-boards.greenhouse.io/embed/job_app?for={board}&token={jid}' if embed else f'https://job-boards.greenhouse.io/{board}/jobs/{jid}'
    content = html.unescape(html.unescape(d.get('content', '')))
    pay = list(dict.fromkeys(re.findall(r'\$\s?\d[\d,.]*\s?[kK]?\s*(?:[-–—]|to)\s*\$?\s?\d[\d,.]*\s?[kK]?', re.sub('<[^>]+>', ' ', content))))[:3]
    print(f"{d.get('company_name')} | {d['title']} | {d.get('location', {}).get('name')}\nOPEN {form}\npay: {'; '.join(pay) or 'not posted'}")

    A, lines = {}, []
    def add(fid, req, kind, label, opts, ans, why=''):
        tag = 'YOU' if ans is None and why == 'you' else ('TODO' if ans is None else '')
        if ans is not None: A[fid] = ans
        o = (' {' + ' / '.join(x[:40] for x in opts[:8]) + (' …' if len(opts) > 8 else '') + '}') if opts and ans is None else ''
        shown = ans if not isinstance(ans, dict) else ans['v']
        if req or ans is not None or opts:
            lines.append(f"{'*' if req else ' '}{fid} [{kind}] {label[:70]}{o} -> {tag or shown}")
    for k in ('first_name', 'last_name', 'email', 'phone'):
        if PROFILE.get(k): A[k] = PROFILE[k]
    for q in d.get('questions', []):
        label = re.sub(r'\s+', ' ', q['label']).strip()
        for f in q['fields']:
            name, typ = f['name'], f['type']
            if name in PROFILE or typ in ('input_file', 'textarea') and name in ('resume_text', 'cover_letter_text') or typ == 'input_file' or name in ('preferred_name',):
                continue
            opts = [v['label'] for v in f.get('values', [])]
            kind = {'multi_value_single_select': 'select', 'multi_value_multi_select': 'multi', 'input_text': 'text', 'textarea': 'para'}.get(typ, typ)
            ans, why = None, ''
            for rx, val in RULES:
                if re.search(rx, label, re.I):
                    if val is CANDIDATE: why = 'you'
                    elif val in (None, '', []): pass
                    elif isinstance(val, list): ans = pick(opts, val) if opts else val[0]
                    elif not opts: ans = val
                    break
            if ans and kind == 'multi': ans = [ans]
            add(name, q['required'], kind, label, opts, ans, why)
    eeo = []
    for c in d.get('compliance') or []:
        for q in c.get('questions', []):
            for f in q['fields']: eeo.append((f['name'], q['required'], q['label'], [v['label'] for v in f.get('values', [])], False))
    dq = d.get('demographic_questions') or {}
    for q in dq.get('questions', []):
        eeo.append((str(q['id']), q['required'], q['label'], [o['label'] for o in q.get('answer_options', [])], 'multi' in q.get('type', '')))
    for fid, req, label, opts, multi in eeo:
        lab = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', label)
        prefs = next((p for rx, p in EEO if re.search(rx, lab, re.I)), DECLINE)
        ans = pick(opts, prefs) or pick(opts, DECLINE)
        add(fid, req, 'eeo', lab, opts, [ans] if ans and multi else ans)
    if d.get('location_questions') and 'candidate-location' in STANDARD: A['candidate-location'] = STANDARD['candidate-location']
    for k, v in STANDARD.items():
        if k != 'candidate-location': A.setdefault(k, v)
    for k, v in sets.items():
        A[k] = v.split('|') if '|' in v else ({'s': v.split('>>')[0], 'v': v.split('>>')[1]} if '>>' in v else v)
        lines.append(f' {k} -> {v} (set)')
    for k in leaves: A.pop(k, None)
    print('\n'.join(lines))
    print('resume: upload via file_upload (find "Resume/CV file input"); education/country/location: standard')
    js = (Path(__file__).parent / 'gh_fill.js').read_text()
    js = '\n'.join(l.strip() for l in js.splitlines() if l.strip() and not l.lstrip().startswith('//'))
    print('----- gh_fill (pass verbatim to javascript_tool) -----')
    print(js.replace('/*ANSWERS*/{}', json.dumps(A, ensure_ascii=False)))

if __name__ == '__main__':
    main()
