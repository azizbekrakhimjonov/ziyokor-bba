import { describe, expect, it } from 'vitest';
import { examCompleted, uniqueStudentLogin } from '../lib/bba-access';

describe('One completed exam per student login', () => {
  it('blocks completion saved in progress', () => {
    expect(examCompleted('xasan@gmail.com', [], { r: { id: 1 } })).toBe(true);
  });
  it('blocks completion saved in results', () => {
    expect(examCompleted('xasan@gmail.com', [{ uid: 'xasan@gmail.com' }], null)).toBe(true);
  });
  it('allows unfinished and explicitly reset students', () => {
    expect(examCompleted('xasan@gmail.com', [{ uid: 'other@gmail.com' }], {})).toBe(false);
    expect(examCompleted('xasan@gmail.com', [], null)).toBe(false);
  });
  it('generates separate logins for repeated names', () => {
    const students: { login: string }[] = [];
    for (let i = 0; i < 3; i++) students.push({ login: uniqueStudentLogin('xasan', students) });
    expect(students.map(s => s.login)).toEqual(['xasan@gmail.com', 'xasan2@gmail.com', 'xasan3@gmail.com']);
  });
});