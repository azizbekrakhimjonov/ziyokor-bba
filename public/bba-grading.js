/** Single normalized grading contract used by the browser, API and reports. Not Rasch calibration. */
export function calculateGrade({ testScore, writtenScore = 0, maxScore }) {
  const max = Number(maxScore), test = Number(testScore);
  const pending = writtenScore === null || writtenScore === undefined || writtenScore === '';
  const written = pending ? null : Number(writtenScore);
  const raw = pending ? null : test + written;
  const invalid = !Number.isFinite(max) || max <= 0 || !Number.isFinite(test) || test < 0 || test > max || (!pending && (!Number.isFinite(written) || written < 0));
  const percentage = !invalid && !pending ? Math.min(raw / 65 * 100, 100) : null;
  const scaledScore75 = !invalid && !pending ? raw * 75 / max : null;
  const grade = invalid || pending ? null : raw >= 70 ? 'A+' : raw >= 65 ? 'A' : raw >= 60 ? 'B+' : raw >= 55 ? 'B' : raw >= 50 ? 'C+' : raw >= 46 ? 'C' : 'None';
  return { rawScore: invalid ? null : raw, maxScore: max, percentage, scaledScore75, grade, gradingMethod: 'normalized', gradingStatus: invalid ? 'invalid' : pending ? 'pending' : 'final', raschStatus: 'Kalibrlanmagan', error: invalid ? 'Maksimal ball musbat bo‘lsin; to‘plangan ball 0 va maksimal ball oralig‘ida bo‘lishi kerak.' : null };
}

export function resultInputs(r, db = {}) {
  const fan = r.vf ?? String(r.fan || '').split(' — ')[0];
  const variant = r.vn ?? (String(r.fan || '').split(' — ')[1] || '—');
  const config = (db.vars || []).find(v => v.fan === fan && v.name === variant);
  const weights = r.gradingVersion ? r.weights : (r.weights ?? (db.wt || {})[fan + '|' + variant]);
  const maxScore = r.gradingVersion ? r.mx : (config?.tot ?? r.mx ?? (Number(r.tn) + Number(r.wn)));
  const testScore = Array.isArray(weights) && Array.isArray(r.qa) ? r.qa.reduce((s, v, i) => s + (v === 1 ? Number(weights[i] || 0) : 0), 0) : Number(r.ts ?? r.c);
  // Cent-based item weights are added as cents to avoid floating addition exceeding the maximum.
  const weightedTest = Array.isArray(weights) && Array.isArray(r.qa) ? r.qa.reduce((s, v, i) => s + (v === 1 ? Math.round(Number(weights[i] || 0) * 100) : 0), 0) / 100 : testScore;
  return { testScore: weightedTest, writtenScore: r.ws, maxScore, weights };
}
export function evaluateResult(r, db) { return calculateGrade(resultInputs(r, db)); }
export function snapshotResult(r, db) {
  const input = resultInputs(r, db);
  const writtenMax = input.weights && Array.isArray(r.qa) ? r.qa.reduce((s, v, i) => s + (v == null ? Math.round(Number(input.weights[i] || 0) * 100) : 0), 0) / 100 : r.wm;
  return { ...r, mx: input.maxScore, ts: input.testScore, wm: writtenMax, weights: input.weights ? [...input.weights] : undefined, gradingVersion: 1, grading: calculateGrade(input) };
}
export function validateWrittenScore(value, maximum) {
  if (value === '' || value === null) return null;
  const score = Number(value), max = Number(maximum);
  if (!Number.isFinite(score) || !Number.isFinite(max) || score < 0) throw new Error('Yozma ball 0 dan kichik bo‘lmasin.');
  return score;
}