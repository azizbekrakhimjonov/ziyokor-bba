export type Grading = { rawScore: number | null; maxScore: number; percentage: number | null; scaledScore75: number | null; grade: string | null; gradingMethod: string; gradingStatus: string; raschStatus: string; error: string | null };
export function calculateGrade(input: { testScore: unknown; writtenScore?: unknown; maxScore: unknown }): Grading;
export function evaluateResult(r: Record<string, any>, db?: Record<string, any>): Grading;
export function resultInputs(r: Record<string, any>, db?: Record<string, any>): { testScore: number; writtenScore: unknown; maxScore: number; weights: number[] | undefined };
export function snapshotResult<T extends Record<string, any>>(r: T, db?: Record<string, any>): T & { mx: number; ts: number; gradingVersion: number; grading: Grading; weights: number[] | undefined };
export function validateWrittenScore(value: unknown, maximum: unknown): number | null;