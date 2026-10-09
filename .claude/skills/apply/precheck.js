// Pre-submit check for React forms (Greenhouse, Ashby, Lever). Run as ONE javascript_tool call right before you submit,
// and as the last step of every fill.
// Finds fields whose visible value differs from React's state ("shows filled, but submit says empty") and re-commits them
// through React's own onChange path. Only sets values: never clicks a button, never submits.
// Output: "ok N fields in sync", or the fields it fixed and any it couldn't fix. No "=" or "&" in output.
await (async () => {
  const tick = () => new Promise(r => { const c = new MessageChannel(); c.port1.onmessage = () => r(); c.port2.postMessage(0); });
  const props = el => { const k = Object.keys(el).find(k => k.startsWith('__reactProps')); return k ? el[k] : null; };
  const name = el => (el.name || el.id || el.getAttribute('aria-label') || '?').slice(0, 24);
  const skip = el => ['hidden', 'file', 'submit', 'button'].includes(el.type) || /recaptcha|^iti/.test(el.id || '') || el.getAttribute('role') === 'combobox';
  const check = () => {
    const bad = [];
    for (const el of document.querySelectorAll('input, textarea')) {
      if (skip(el)) continue;
      const p = props(el);
      if (!p) { if (el.value && el.type !== 'radio' && el.type !== 'checkbox') bad.push([el, 'noreact']); continue; }
      if (el.type === 'radio' || el.type === 'checkbox') { if ('checked' in p && !!p.checked !== el.checked) bad.push([el, 'box']); }
      else if ('value' in p && p.value !== undefined && String(p.value ?? '') !== el.value) bad.push([el, 'text']);
    }
    return bad;
  };
  const total = document.querySelectorAll('input, textarea').length;
  const fixed = [];
  for (const [el, kind] of check()) {
    if (kind === 'box') { const want = el.checked; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'checked').set.call(el, !want); el.click(); }
    else { const v = el.value, proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, ''); el.dispatchEvent(new Event('input', { bubbles: true }));
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, v); for (const t of ['input', 'change', 'blur']) el.dispatchEvent(new Event(t, { bubbles: true })); }
    fixed.push(`${kind} ${name(el)}`);
  }
  for (let i = 0; i < 40; i++) await tick();
  const left = check().map(([el, k]) => `${k} ${name(el)}`);
  const msg = !fixed.length ? `ok ${total} fields in sync` : `fixed ${fixed.length}: ${fixed.join(', ')}` + (left.length ? `\nSTILL OUT OF SYNC (retype these by hand): ${left.join(', ')}` : '\nall in sync now');
  return msg.replace(/[=&]/g, ' ');
})();
