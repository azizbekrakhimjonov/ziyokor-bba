"""Port of public/bba-grading.js — keep in sync with browser/API contract."""


def calculate_grade(*, test_score, written_score=0, max_score):
    max_v = float(max_score)
    test = float(test_score)
    pending = written_score is None or written_score == ""
    written = None if pending else float(written_score)
    raw = None if pending else test + written
    invalid = (
        not (max_v == max_v and max_v > 0)
        or not (test == test and test >= 0)
        or test > max_v
        or (
            not pending
            and (not (written == written and written >= 0))
        )
    )
    percentage = None
    scaled_score_75 = None
    grade = None
    if not invalid and not pending:
        percentage = min(raw / 65 * 100, 100)
        scaled_score_75 = raw * 75 / max_v
        grade = (
            "A+"
            if raw >= 70
            else "A"
            if raw >= 65
            else "B+"
            if raw >= 60
            else "B"
            if raw >= 55
            else "C+"
            if raw >= 50
            else "C"
            if raw >= 46
            else "None"
        )
    return {
        "rawScore": None if invalid else raw,
        "maxScore": max_v,
        "percentage": percentage,
        "scaledScore75": scaled_score_75,
        "grade": grade,
        "gradingMethod": "normalized",
        "gradingStatus": "invalid" if invalid else ("pending" if pending else "final"),
        "raschStatus": "Kalibrlanmagan",
        "error": (
            "Maksimal ball musbat bo‘lsin; to‘plangan ball 0 va maksimal ball oralig‘ida bo‘lishi kerak."
            if invalid
            else None
        ),
    }


def result_inputs(r, db=None):
    db = db or {}
    fan = r.get("vf") or str(r.get("fan") or "").split(" — ")[0]
    variant = r.get("vn") or (str(r.get("fan") or "").split(" — ")[1] if " — " in str(r.get("fan") or "") else "—")
    config = next(
        (v for v in (db.get("vars") or []) if v.get("fan") == fan and v.get("name") == variant),
        None,
    )
    weights = r.get("weights") if r.get("gradingVersion") else (r.get("weights") or (db.get("wt") or {}).get(f"{fan}|{variant}"))
    if r.get("gradingVersion"):
        max_score = r.get("mx")
    else:
        max_score = (config or {}).get("tot") or r.get("mx") or (float(r.get("tn") or 0) + float(r.get("wn") or 0))
    qa = r.get("qa")
    if isinstance(weights, list) and isinstance(qa, list):
        test_score = sum(float(weights[i] or 0) for i, v in enumerate(qa) if v == 1)
        weighted_test = (
            sum(round(float(weights[i] or 0) * 100) for i, v in enumerate(qa) if v == 1) / 100
        )
    else:
        test_score = float(r.get("ts") if r.get("ts") is not None else r.get("c") or 0)
        weighted_test = test_score
    return {
        "testScore": weighted_test,
        "writtenScore": r.get("ws"),
        "maxScore": max_score,
        "weights": weights,
    }


def evaluate_result(r, db):
    inp = result_inputs(r, db)
    return calculate_grade(
        test_score=inp["testScore"],
        written_score=inp["writtenScore"],
        max_score=inp["maxScore"],
    )


def snapshot_result(r, db):
    inp = result_inputs(r, db)
    qa = r.get("qa")
    weights = inp.get("weights")
    if weights and isinstance(qa, list):
        written_max = sum(round(float(weights[i] or 0) * 100) for i, v in enumerate(qa) if v is None) / 100
    else:
        written_max = r.get("wm")
    out = dict(r)
    out.update(
        {
            "mx": inp["maxScore"],
            "ts": inp["testScore"],
            "wm": written_max,
            "gradingVersion": 1,
        }
    )
    if inp.get("weights") is not None:
        out["weights"] = list(inp["weights"])
    out["grading"] = calculate_grade(
        test_score=inp["testScore"],
        written_score=inp["writtenScore"],
        max_score=inp["maxScore"],
    )
    return out


def validate_written_score(value, maximum):
    if value in ("", None):
        return None
    score = float(value)
    max_v = float(maximum)
    if not (score == score and max_v == max_v) or score < 0:
        raise ValueError("Yozma ball 0 dan kichik bo‘lmasin.")
    if score > max_v:
        raise ValueError("Yozma ball maksimal yozma balldan oshmasin.")
    return score
