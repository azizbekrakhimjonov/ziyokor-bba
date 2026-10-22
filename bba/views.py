import copy
import json
import secrets
import string
from pathlib import Path
from typing import Any

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .access import exam_completed, unique_student_login
from .grading import evaluate_result, snapshot_result, validate_written_score
from .store import DEF, PB, delete_from_id, delete_id, get_data, list_data_from_id, upsert_data

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type",
}


def _j(body: Any, status: int = 200) -> JsonResponse:
    return JsonResponse(body, status=status, json_dumps_params={"ensure_ascii": False}, headers=CORS)


def _rnd(n: int, abc: str) -> str:
    return "".join(secrets.choice(abc) for _ in range(n))


def _slug(s: str) -> str:
    part = (s.split() or [""])[0].lower()
    for ch in "‘’`ʻʼ'":
        part = part.replace(ch, "")
    part = "".join(c for c in part if "a" <= c <= "z")[:16]
    return part or "talaba"


def _pub(st: dict) -> dict:
    return {"id": st["login"], "email": st["login"], "name": st["name"]}


def _users_list(students: list) -> list:
    return [
        {
            "id": s["login"],
            "email": s["login"],
            "name": s["name"],
            "ok": True,
            "at": s.get("at") or "",
        }
        for s in students
    ]


def handle_bba_post(b: dict) -> JsonResponse:
    now = int(__import__("time").time() * 1000)
    try:
        main_data = get_data(1)
    except Exception as e:
        print(e)
        return _j(
            {
                "error": 1,
                "message": "Baza ochilmadi. DATABASES va migratsiyalarni tekshiring.",
            },
            503,
        )

    db = copy.deepcopy(main_data) if main_data else copy.deepcopy(DEF)
    db.setdefault("st", [])
    db.setdefault("res", [])
    db.setdefault("qs", [])
    dirty = False
    for s in db["st"]:
        if not s.get("sid"):
            s["sid"] = max([0, *[x.get("sid") or 0 for x in db["st"]]]) + 1
            dirty = True

    def put(d: dict) -> None:
        upsert_data(1, d)

    def get_p(sid: int):
        return get_data(PB + sid)

    def put_p(sid: int, d: dict) -> None:
        upsert_data(PB + sid, d)

    if dirty:
        put(db)

    ad = db.get("adm") or {"u": "admin", "p": "admin123"}
    if not db.get("adm"):
        db["adm"] = ad
        put(db)

    admin = bool(b.get("u") == ad["u"] and b.get("p") == ad["p"])
    stu = None if admin else next((x for x in db["st"] if x.get("login") == b.get("u") and x.get("pass") == b.get("p")), None)

    action = b.get("a")

    if action == "login":
        if admin:
            rows = list_data_from_id(PB)
            ids = {r.get("id") for r in db["res"]}
            add = False
            for x in rows:
                prog = x.get("data") or {}
                r = prog.get("r")
                if r and r.get("id") not in ids:
                    db["res"].append(r)
                    add = True
            if add:
                put(db)
            safe = {k: v for k, v in db.items() if k != "adm"}
            return _j({"admin": True, "db": safe})
        if not stu:
            return _j({"error": 1}, 401)
        if not stu.get("sid"):
            return _j({"error": 1}, 409)
        pr = get_p(stu["sid"])
        if exam_completed(stu["login"], db["res"], pr):
            return _j({"error": 1, "completed": True}, 403)
        prog = pr if pr and not pr.get("r") else None
        return _j(
            {
                "s": _pub(stu),
                "qs": db.get("qs"),
                "dur": db.get("dur"),
                "act": db.get("act"),
                "vars": db.get("vars"),
                "prog": prog,
                "now": now,
            }
        )

    if action == "begin":
        if not stu or not b.get("key"):
            return _j({"error": 1}, 403)
        if not stu.get("sid"):
            return _j({"error": 1}, 409)
        pr = get_p(stu["sid"])
        if exam_completed(stu["login"], db["res"], pr):
            return _j({"error": 1, "completed": True}, 403)
        if pr and not pr.get("r"):
            return _j({"prog": pr, "now": now})
        try:
            k = str(b["key"])
            if k.startswith("v"):
                f, n = json.loads(k[1:])
                vars_list = db.get("vars") or []
                v = next((x for x in vars_list if x.get("fan") == f and x.get("name") == n), None)
                if v and v.get("open") and now < int(v["open"]):
                    return _j({"error": 1, "notyet": 1, "open": v["open"], "now": now}, 403)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        np = {
            "key": str(b["key"])[:300],
            "start": now,
            "end": now + int(db.get("dur") or 90) * 60000,
            "ans": {},
        }
        put_p(stu["sid"], np)
        return _j({"prog": np, "now": now})

    if action == "ans":
        if not stu or not isinstance(b.get("ans"), dict):
            return _j({"error": 1}, 403)
        if len(json.dumps(b["ans"], ensure_ascii=False)) > 200_000:
            return _j({"error": 1}, 413)
        if not stu.get("sid"):
            return _j({"error": 1}, 409)
        pr = get_p(stu["sid"])
        if not pr or pr.get("r"):
            return _j({"error": 1}, 409)
        if now > pr["end"] + 30_000:
            return _j({"late": 1, "now": now})
        pr["ans"] = b["ans"]
        put_p(stu["sid"], pr)
        return _j({"ok": 1, "now": now})

    if action == "result":
        if not stu or not b.get("r"):
            return _j({"error": 1}, 403)
        if not stu.get("sid"):
            return _j({"error": 1}, 409)
        pr = get_p(stu["sid"])
        if exam_completed(stu["login"], db["res"], pr):
            return _j({"ok": 1})
        if not pr:
            return _j({"error": 1}, 409)
        r = snapshot_result(
            {**b["r"], "uid": stu["login"], "email": stu["login"], "name": stu["name"]},
            db,
        )
        if r.get("grading", {}).get("gradingStatus") == "invalid":
            return _j({"error": 1, "message": r["grading"].get("error")}, 400)
        put_p(stu["sid"], {**pr, "r": r})
        db["res"].append(r)
        put(db)
        return _j({"ok": 1})

    if action == "setadm":
        if not admin:
            return _j({"error": 1, "message": "Joriy admin login yoki parol noto‘g‘ri."}, 403)
        nu = str(b.get("nu") or "").strip()
        npw = str(b.get("np") or "").strip()
        if len(nu) < 3:
            return _j({"error": 1, "message": "Yangi login kamida 3 belgi bo‘lsin."}, 400)
        if any(x.get("login") == nu for x in db["st"]):
            return _j({"error": 1, "message": "Bu login o‘quvchida band."}, 400)
        if npw and len(npw) < 6:
            return _j({"error": 1, "message": "Yangi parol kamida 6 belgi bo‘lsin."}, 400)
        next_pass = npw or ad["p"]
        if nu == ad["u"] and next_pass == ad["p"]:
            return _j({"error": 1, "message": "Hech narsa o‘zgarmadi."}, 400)
        db["adm"] = {"u": nu, "p": next_pass}
        put(db)
        return _j({"ok": 1, "u": nu})

    if not admin:
        return _j({"error": 1}, 403)

    if action == "users":
        return _j({"st": db["st"], "users": _users_list(db["st"])})

    if action == "addst":
        name = " ".join(str(b.get("name") or "").strip().split())
        if len(name) < 3 or len(name) > 100:
            return _j({"error": 1}, 400)
        w = name.split()
        base = _slug(w[1] if len(w) > 1 else w[0])
        login = unique_student_login(base, db["st"])
        sid = max([0, *[x.get("sid") or 0 for x in db["st"]]]) + 1
        s = {"name": name, "login": login, "pass": base + _rnd(3, string.digits), "sid": sid}
        db["st"].append(s)
        put(db)
        return _j({"st": s})

    if action == "del":
        s = next((x for x in db["st"] if x.get("login") == b.get("login")), None)
        if not s:
            return _j({"error": 1}, 404)
        db["st"] = [x for x in db["st"] if x is not s]
        db["res"] = [r for r in db["res"] if r.get("uid") != s["login"]]
        if s.get("sid"):
            delete_id(PB + s["sid"])
        put(db)
        return _j({"ok": 1})

    if action == "reset":
        s = next((x for x in db["st"] if x.get("login") == b.get("login")), None)
        if not s:
            return _j({"error": 1}, 404)
        db["res"] = [r for r in db["res"] if r.get("uid") != s["login"]]
        if s.get("sid"):
            delete_id(PB + s["sid"])
        put(db)
        return _j({"ok": 1})

    if action == "clear":
        db["res"] = []
        delete_from_id(PB)
        put(db)
        return _j({"ok": 1})

    if action == "save":
        if not b.get("db"):
            return _j({"error": 1}, 400)
        d = b["db"]
        d["adm"] = db["adm"]
        d["st"] = db["st"]
        ids = {r.get("id") for r in (d.get("res") or [])}
        d["res"] = list(d.get("res") or []) + [r for r in db["res"] if r.get("id") not in ids]
        vars_list = d.get("vars") or []
        if any(not isinstance(v.get("tot"), (int, float)) and not str(v.get("tot", "")).replace(".", "", 1).isdigit() for v in vars_list):
            pass
        for v in vars_list:
            tot = float(v.get("tot") or 0)
            if tot <= 0 or tot != tot:
                return _j({"error": 1, "message": "Maksimal ball musbat son bo‘lsin."}, 400)
        original = {r.get("id"): r for r in db["res"]}

        def map_result(r):
            previous = original.get(r.get("id"))
            if previous and not r.get("gradingVersion"):
                preserved = snapshot_result(previous, db)
                source = {**r, "mx": preserved["mx"], "weights": preserved.get("weights"), "gradingVersion": 1}
            else:
                source = r
            return snapshot_result(source, d)

        d["res"] = [map_result(r) for r in d["res"]]
        try:
            for r in d["res"]:
                if float(r.get("wn") or 0) > 0:
                    validate_written_score(r.get("ws"), r.get("wm") if r.get("wm") is not None else r.get("wn"))
        except ValueError:
            return _j({"error": 1, "message": "Yozma ball maksimal yozma balldan oshmasin."}, 400)
        invalid = next((r for r in d["res"] if evaluate_result(r, d).get("gradingStatus") == "invalid"), None)
        if invalid:
            ev = evaluate_result(invalid, d)
            return _j({"error": 1, "message": ev.get("error")}, 400)
        put(d)
        return _j({"ok": 1})

    return _j({"error": 1}, 400)


def platform_home(request):
    path = Path(settings.PUBLIC_DIR) / "bba-platform.html"
    if not path.is_file():
        raise Http404("bba-platform.html topilmadi")
    return FileResponse(path.open("rb"), content_type="text/html; charset=utf-8")


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def bba_api(request):
    if request.method == "OPTIONS":
        return HttpResponse(status=204, headers=CORS)
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _j({"error": 1, "message": "Noto‘g‘ri so‘rov."}, 400)
    return handle_bba_post(body)
