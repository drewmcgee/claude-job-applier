// Greenhouse one-shot filler. gh_plan.py injects ANSWERS; pass the printed script verbatim as ONE javascript_tool call.
// Pure JS through React internals: no keystrokes, focus or screenshots. Works in background tabs, so it's safe with
// parallel agents. Only sets values: never clicks a button, never submits.
// ANSWERS: { id: "text or exact option label" | ["opt", ...] (multi/checkboxes) | {s: "search text", v: "option label"} }
// Output: only problems ("x id: why") plus "!" lines for required fields still empty. No "=" or "&" in output.
await (async () => {
  const A = /*ANSWERS*/{};
  const tick = () => new Promise(r => { const c = new MessageChannel(); c.port1.onmessage = () => r(); c.port2.postMessage(0); });
  const sleep = async ms => { const t = performance.now(); while (performance.now() - t < ms) await tick(); };
  const norm = s => String(s ?? '').replace(/\s+/g, ' ').replace(/\*/g, '').trim().toLowerCase();
  const fib = el => el && el[Object.keys(el).find(k => k.startsWith('__reactFiber'))];
  const up = (el, pred) => { let f = fib(el); for (let d = 0; f && d < 60; d++, f = f.return) if (pred(f)) return f; return null; };
  const inst = el => up(el, f => typeof f.stateNode?.selectOption === 'function')?.stateNode;
  const match = (opts, want) => { const w = norm(want); return opts.find(o => norm(o.label) === w) || opts.find(o => norm(o.label).startsWith(w)); };
  // Hidden tabs never hydrate (no React = nothing works). The caller must take a scale-0.1 screenshot first.
  { const t0 = performance.now(); while (!fib(document.getElementById('first_name')) && performance.now() - t0 < 4000) await tick();
    if (!fib(document.getElementById('first_name'))) return 'NOT HYDRATED: take a scale 0.1 screenshot of this tab, then rerun this script'; }
  // Wait until every combobox has a React instance and the count is steady for 600ms.
  const ready = () => { if (!fib(document.getElementById('first_name'))) return 0; const cs = [...document.querySelectorAll('input[role=combobox]')].filter(e => !/^iti/.test(e.id)); return cs.every(inst) ? cs.length + 1 : 0; };
  { const t0 = performance.now(); let last = -1, since = t0;
    while (performance.now() - t0 < 20000) { const n = ready(); if (n !== last) { last = n; since = performance.now(); } else if (n && performance.now() - since > 600) break; await tick(); } }
  async function sel(el, val) {
    const s = inst(el); if (!s) return 'no select instance';
    const wants = Array.isArray(val) ? val : [typeof val === 'object' ? val.v : val];
    const search = typeof val === 'object' && !Array.isArray(val) ? val.s : '';
    let opts = s.props.options || [];
    const lo = up(el, f => typeof f.memoizedProps?.loadOptions === 'function')?.memoizedProps.loadOptions;
    if (lo && (search || !opts.length)) { const r = await lo(search, [], { page: 1 }); opts = r?.options || r || []; }
    else if (search) {
      s.props.onInputChange?.(search, { action: 'input-change', prevInputValue: '' });
      const t = performance.now(); while (performance.now() - t < 8000) { opts = inst(el).props.options || []; if (match(opts, wants[0])) break; await tick(); }
    }
    const miss = [];
    for (const w of wants) { const o = match(opts, w); if (o) inst(el).selectOption(o); else miss.push(w); }
    return miss.length ? `no option "${miss.join('", "')}" in ${opts.slice(0, 5).map(o => o.label).join(' / ')}` : null;
  }
  async function text(el, v) {
    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, v);
    for (const t of ['input', 'change', 'blur']) el.dispatchEvent(new Event(t, { bubbles: true }));
    for (let i = 0; i < 5; i++) await tick(); const p = el[Object.keys(el).find(k => k.startsWith('__reactProps'))]; return el.value === v && (!p || p.value === undefined || p.value === v) ? null : 'text did not reach React state';
  }
  const boxes = id => { const stem = id.replace(/\[\]$/, ''); return [...document.querySelectorAll('input[type=checkbox],input[type=radio]')].filter(c => (c.name || '').replace(/\[\]$/, '') === stem || (c.id || '').startsWith(stem + '_') || c.closest('fieldset')?.querySelector(`[id^="${CSS.escape(stem)}"]`)); };
  const boxLabel = c => norm(document.querySelector(`label[for="${CSS.escape(c.id)}"]`)?.textContent || c.closest('label')?.textContent);
  async function fill(id, val) {
    try {
      const el = document.getElementById(id) || document.querySelector(`[name="${CSS.escape(id)}"]`);
      if (el && el.getAttribute('role') === 'combobox') return await sel(el, val);
      if (el && /^(text|email|tel|url|number|search|textarea)$/.test(el.type || el.tagName.toLowerCase())) return await text(el, String(val));
      const bs = boxes(id); if (!bs.length) return /--0$/.test(id) ? null : 'field not on page';
      const miss = [];
      for (const w of [].concat(val)) { const c = bs.find(b => boxLabel(b) === norm(w)) || bs.find(b => boxLabel(b).startsWith(norm(w))); if (!c) miss.push(w); else if (!c.checked) c.click(); }
      return miss.length ? `no box "${miss.join('", "')}" in ${bs.slice(0, 6).map(boxLabel).join(' / ')}` : null;
    } catch (e) { return e.message.slice(0, 60); }
  }
  let todo = Object.entries(A);
  for (let pass = 0; pass < 2 && todo.length; pass++) {
    if (pass) await sleep(1500);
    const failed = [];
    for (const [id, val] of todo) { const err = await fill(id, val); if (err) failed.push([id, val, err]); }
    todo = failed;
  }
  document.activeElement?.blur?.();
  await sleep(300);
  const out = todo.map(([id, , err]) => `x ${id}: ${err}`);
  for (const el of document.querySelectorAll('input, textarea')) {
    if (!el.id || /recaptcha|^iti/.test(el.id) || ['hidden', 'submit', 'button', 'checkbox', 'radio', 'file'].includes(el.type)) continue;
    const lab = document.querySelector(`label[for="${CSS.escape(el.id)}"]`)?.textContent || '';
    if (!(/\*/.test(lab) || el.getAttribute('aria-required') === 'true' || el.required)) continue;
    const v = el.getAttribute('role') === 'combobox' ? el.closest('.select-shell')?.querySelector('[class*=single-value],[class*=multi-value__label]') : el.value;
    if (!v) out.push(`! ${el.id} ${norm(lab).slice(0, 50)}`);
  }
  for (const fs of document.querySelectorAll('fieldset')) {
    const lg = fs.querySelector('legend')?.textContent || '';
    if (/\*/.test(lg) && fs.querySelector('input[type=checkbox],input[type=radio]') && !fs.querySelector('input:checked')) out.push(`! [boxes] ${norm(lg).slice(0, 50)}`);
  }
  const resume = [...document.querySelectorAll('[class*=file-name],[class*=filename],[class*=chip]')].some(n => /\.pdf/i.test(n.textContent));
  return [`done ${Object.keys(A).length - todo.length}/${Object.keys(A).length} set, resume ${resume ? 'attached' : 'NOT attached'}`, ...out].join('\n').replace(/[=&]/g, ' ');
})();
