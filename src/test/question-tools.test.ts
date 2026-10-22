import { readFileSync } from 'node:fs';
import { describe, expect, it, beforeAll } from 'vitest';
import * as grading from '../../public/bba-grading.js';

type Result = { c: number; tn: number; wn: number; ts: number; ws: number | null; mx: number; vf?: string; vn?: string; fan?: string };
type Distribution = { counts: number[]; mean: number; pending: number; total: number; participants: number; percentages: number[] };
type Tools = { allocateWeights: (questions: { i: number; p: number; pd?: boolean }[], total: number) => number[]; sanitize: (html: string) => string; plain: (html: string) => string; distribution: (rows: Result[]) => Distribution; gradeDistribution: (rows: Result[], fan: string, variant: string) => Distribution };
let tools: Tools;
beforeAll(() => {
  Object.assign(window, { BBAgrading: grading });
  window.eval(readFileSync('public/bba-question-tools.js', 'utf8'));
  tools = (window as unknown as { BBAtools: Tools }).BBAtools;
});
describe('Copied question content', () => {
  it('preserves copied table text while removing executable content', () => {
    const clean = tools.sanitize('<table><tr><td colspan="2">Davlat</td><td>Respublika</td></tr></table><script>alert(1)</script><img src="x" onerror="alert(1)">');
    expect(tools.plain(clean)).toContain('Davlat\tRespublika');
    expect(clean).not.toContain('script');
    expect(clean).not.toContain('onerror');
  });
  it('retains embedded diagram images', () => {
    expect(tools.sanitize('<img src="data:image/png;base64,AAAA" onload="alert(1)">')).toContain('data:image/png;base64,AAAA');
    expect(tools.sanitize('<img src="javascript:alert(1)">')).toBe('');
  });
});
describe('Automatic variant weights (0.5 to 3 per question)', () => {
  it('gives 0.5 when 17 of 17 students solved it', () => {
    expect(tools.allocateWeights([{ i: 0, p: 100, t: 17, ok: 17 } as never], 80)[0]).toBe(0.5);
  });
  it('gives 3 when nobody solved it', () => {
    expect(tools.allocateWeights([{ i: 0, p: 0, t: 17, ok: 0 } as never], 80)[0]).toBe(3);
  });
  it('lets the total go above the admin maximum of 80', () => {
    const qs = Array.from({ length: 45 }, (_, i) => ({ i, p: 0, t: 10, ok: 0 }));
    expect(tools.allocateWeights(qs as never, 80).reduce((s, v) => s + v, 0)).toBe(135);
  });
  it('waits for every written question to be reviewed', () => {
    expect(tools.allocateWeights([{ i: 0, p: 0, pd: true }], 80)).toEqual([]);
  });
});
