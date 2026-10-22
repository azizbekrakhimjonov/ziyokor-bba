/* Shared, browser-safe question formatting and statistics helpers. */
(function (root) {
  const tags = new Set(['P', 'DIV', 'BR', 'B', 'STRONG', 'I', 'EM', 'U', 'SUB', 'SUP', 'UL', 'OL', 'LI', 'TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TH', 'TD', 'IMG']);
  const discard = new Set(['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'TEMPLATE', 'SVG', 'MATH']);
  function sanitize(html) {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    function clean(node) {
      if (node.nodeType === 3) return document.createTextNode(node.textContent || '');
      if (node.nodeType !== 1 || discard.has(node.tagName)) return document.createDocumentFragment();
      const out = tags.has(node.tagName) ? document.createElement(node.tagName.toLowerCase()) : document.createDocumentFragment();
      if (node.tagName === 'IMG') {
        const src = node.getAttribute('src') || '';
        if (!/^data:image\/(png|jpeg|jpg|webp|gif);base64,[a-z0-9+/=\s]+$/i.test(src)) return document.createDocumentFragment();
        out.setAttribute('src', src);
        out.setAttribute('alt', node.getAttribute('alt') || 'Savol rasmi');
      }
      if (node.tagName === 'TD' || node.tagName === 'TH') {
        for (const key of ['colspan', 'rowspan']) {
          const n = Number(node.getAttribute(key));
          if (Number.isInteger(n) && n > 1 && n <= 50) out.setAttribute(key, String(n));
        }
      }
      for (const child of node.childNodes) out.appendChild(clean(child));
      return out;
    }
    const container = document.createElement('div');
    for (const node of doc.body.childNodes) container.appendChild(clean(node));
    return container.innerHTML;
  }
  function plain(html) {
    const el = document.createElement('div');
    el.innerHTML = sanitize(html);
    el.querySelectorAll('br').forEach(n => n.replaceWith('\n'));
    el.querySelectorAll('p,div,tr,li').forEach(n => n.append('\n'));
    el.querySelectorAll('td,th').forEach(n => n.append('\t'));
    return (el.textContent || '').trim();
  }
  function distribution(results) {
    const evaluated = results.map(r => root.BBAgrading.evaluateResult(r));
    const complete = evaluated.filter(r => r.gradingStatus === 'final');
    const scores = complete.map(r => r.rawScore);
    const counts = Array(15).fill(0);
    scores.forEach(s => counts[Math.min(14, Math.floor(s / 5))]++);
    return { counts, scores, total: scores.length, pending: evaluated.filter(r => r.gradingStatus === 'pending').length, invalid: evaluated.filter(r => r.gradingStatus === 'invalid').length, mean: scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0 };
  }
  function gradeDistribution(results, fan, variant) {
    const rows = results.filter(r => (r.vf ?? String(r.fan || '').split(' — ')[0]) === fan && (r.vn ?? (String(r.fan || '').split(' — ')[1] || '—')) === variant);
    const d = distribution(rows), counts = Array(7).fill(0);
    rows.map(r => root.BBAgrading.evaluateResult(r)).filter(r => r.gradingStatus === 'final').forEach(result => {
      const grade = result.grade;
      const i = ['None','C','C+','B','B+','A','A+'].indexOf(grade);
      counts[i]++;
    });
    return { ...d, counts, participants: rows.length, percentages: counts.map(n => d.total ? n / d.total * 100 : 0) };
  }
  function allocateWeights(questions, total) {
    if (!questions.length || questions.some(q => q.pd)) return [];
    // Each question gets 0.5 (everyone solved it) up to 3 (nobody solved it), by share of students who solved it.
    // The total is NOT forced to the admin maximum: it may end up above or below it.
    const weights = [];
    questions.forEach(q => {
      const solved = q.t ? q.ok / q.t : Math.min(1, Math.max(0, (Number(q.p) || 0) / 100));
      weights[q.i] = Math.round((0.5 + 2.5 * (1 - solved)) * 100) / 100;
    });
    return weights;
  }
  root.BBAtools = { sanitize, plain, distribution, gradeDistribution, allocateWeights };
})(globalThis);