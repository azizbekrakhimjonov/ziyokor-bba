def exam_completed(login: str, results: list, progress) -> bool:
    if progress and progress.get("r"):
        return True
    return any(r.get("uid") == login for r in results)


def unique_student_login(base: str, students: list) -> str:
    login = f"{base}@gmail.com"
    suffix = 2
    used = {s["login"].lower() for s in students}
    while login.lower() in used:
        login = f"{base}{suffix}@gmail.com"
        suffix += 1
    return login
