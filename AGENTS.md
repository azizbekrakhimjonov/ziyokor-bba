<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->
Question formatting and score-distribution helpers live in public/bba-question-tools.js and are shared with regression tests, so the iframe and tests use identical logic.
Persist only allowlisted question HTML with embedded raster images; sanitize again when rendering to prevent copied markup from executing code.
Dashboard and statistics charts use the shared gradeDistribution helper on one subject/variant pair with collected-score grades, so counts remain consistent with result grades.
Grading lives in public/bba-grading.js, imported by the API and exposed to the legacy iframe; preserve maximum/weight snapshots and use its unrounded collected-score grade contract in every report, keeping normalization only as an internal metric.
Automatic weights use the shared browser-safe allocateWeights helper with minimum-point constraints and cent-exact remainder allocation, so the UI and tests use identical arithmetic.
Custom exam completion and unique-login rules live in a browser-safe access module shared with API regression tests; completion is checked against both progress and result storage.
