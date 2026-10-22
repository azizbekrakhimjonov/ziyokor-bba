import { describe, expect, it } from 'vitest';
import { calculateGrade, evaluateResult, snapshotResult, validateWrittenScore } from '../../public/bba-grading.js';

describe('Normalized grading contract', () => {
  it.each([
    [73,80,68.4375,'A+'],[75,80,70.3125,'A+'],[84,90,70,'A+'],[92,100,69,'A+'],
    [73,75,73,'A+'],[70,75,70,'A+'],[65,75,65,'A'],[60,75,60,'B+'],[55,75,55,'B'],
    [50,75,50,'C+'],[46,75,46,'C'],[45,75,45,'None'],[0,80,0,'None'],[120,120,75,'A+'],
    [69.99999,75,69.99999,'A'],[45.99999,75,45.99999,'None']
  ])('%s of %s scales to %s and grade %s without rounding', (raw,max,scaled,grade) => {
    const g=calculateGrade({testScore:raw,writtenScore:0,maxScore:max});
    expect(g.scaledScore75).toBeCloseTo(Number(scaled),8);
    expect(g.grade).toBe(grade);
    expect(g.percentage).toBeCloseTo(Math.min(Number(raw)/65*100,100),8);
  });
  it('adds 55.5 test and 17.5 writing to 73 without integer rounding', () => {
    const g=calculateGrade({testScore:55.5,writtenScore:17.5,maxScore:80});
    expect(g.rawScore).toBe(73); expect(g.grade).toBe('A+'); expect(g.percentage).toBe(100);
  });
  it.each([65,72.99,73,80])('caps %s collected points at 100 percent', raw => {
    expect(calculateGrade({testScore:raw,writtenScore:0,maxScore:80}).percentage).toBe(100);
  });
  it.each([[64,98.46],[60,92.31],[55,84.62],[50,76.92],[46,70.77]])('matches the reference percentage for %s points', (raw, percentage) => {
    expect(Number(calculateGrade({testScore:raw,writtenScore:0,maxScore:80}).percentage?.toFixed(2))).toBe(percentage);
  });
  it.each([2.5,3.25,4.75])('keeps fractional written mark %s', score => expect(validateWrittenScore(score,5)).toBe(score));
  it('does not treat unreviewed writing as zero', () => {
    const g=calculateGrade({testScore:70,writtenScore:null,maxScore:80});
    expect(g.grade).toBeNull(); expect(g.rawScore).toBeNull(); expect(g.gradingStatus).toBe('pending');
  });
  it.each([0,-1,'abc',Infinity])('stops for invalid maximum %s', maxScore => {
    const g=calculateGrade({testScore:0,writtenScore:0,maxScore});
    expect(g.gradingStatus).toBe('invalid'); expect(g.grade).toBeNull();
  });
  it('rejects a test score greater than maximum',()=>expect(calculateGrade({testScore:81,writtenScore:0,maxScore:80}).gradingStatus).toBe('invalid'));
  it.each([-1,'bad'])('rejects invalid written score %s',score=>expect(()=>validateWrittenScore(score,5)).toThrow());
  it('keeps a completed exam maximum when its variant is later configured differently',()=>{
    const r=snapshotResult({ts:73,ws:0,mx:80,tn:45,wn:0,vf:'Huquq',vn:'1'}, {vars:[{fan:'Huquq',name:'1',tot:80}]});
    expect(evaluateResult(r,{vars:[{fan:'Huquq',name:'1',tot:100}]}).scaledScore75).toBe(68.4375);
    expect(evaluateResult({...r,mx:90,ts:84}).grade).toBe('A+');
  });
  it('uses the configured maximum for an unsnapshotted legacy result',()=>{
    expect(evaluateResult({ts:73,ws:0,mx:45,vf:'Huquq',vn:'1'}, {vars:[{fan:'Huquq',name:'1',tot:80}]}).grade).toBe('A+');
  });
  it('does not call normalized results calibrated Rasch',()=>{
    const g=calculateGrade({testScore:73,writtenScore:0,maxScore:80});
    expect(g.gradingMethod).toBe('normalized'); expect(g.raschStatus).toBe('Kalibrlanmagan');
  });
});