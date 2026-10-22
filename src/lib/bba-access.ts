/** Browser-safe rules shared by the custom exam API and regression tests. */
export function examCompleted(login: string, results: { [key: string]: unknown }[], progress: { r?: unknown } | null) {
  return Boolean(progress?.r) || results.some(r => r['uid'] === login);
}

export function uniqueStudentLogin(base: string, students: { login: string }[]) {
  let login = `${base}@gmail.com`, suffix = 2;
  const used = new Set(students.map(s => s.login.toLowerCase()));
  while (used.has(login.toLowerCase())) login = `${base}${suffix++}@gmail.com`;
  return login;
}