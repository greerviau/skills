// Accessibility and horizontal-overflow audit for a rendered page.
// Loaded with a script tag, it appends the JSON result in <pre id="audit"> for --dump-dom.
// Passed to a browser automation evaluate call, it returns the same JSON string.
(() => {
  const tag = document.currentScript;
  const loadAxe = () => window.axe ? Promise.resolve() : new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/axe-core@4.10.2/axe.min.js';
    s.onload = resolve;
    s.onerror = () => reject(new Error('axe-core failed to load'));
    document.head.append(s);
  });
  // An element inside a container that scrolls or clips horizontally overflows on purpose.
  const insideScroller = el => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      if (/auto|scroll|hidden|clip/.test(getComputedStyle(p).overflowX)) return true;
    }
    return false;
  };
  const describe = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.classList.length ? '.' + [...el.classList].join('.') : '');
  const run = async () => {
    await loadAxe();
    const result = await window.axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag22aa', 'best-practice'] });
    const overflow = [...document.querySelectorAll('body *')]
      .filter(el => el.id !== 'audit' && el.getBoundingClientRect().right > innerWidth + 1 && !insideScroller(el))
      .map(describe);
    return JSON.stringify({
      width: innerWidth,
      pageScrollsSideways: document.documentElement.scrollWidth > innerWidth,
      overflow,
      violations: result.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.map(n => n.target.join(' ')) })),
    });
  };
  const done = run().catch(e => JSON.stringify({ error: String(e) }));
  if (tag) {
    done.then(json => {
      const out = document.createElement('pre');
      out.id = 'audit';
      out.textContent = json;
      document.body.append(out);
    });
  }
  return done;
})();
