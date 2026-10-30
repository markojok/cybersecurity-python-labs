import csv
import functools
import hashlib
import json
import os
import sys
from datetime import datetime

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

HASH_ALGORITHM = "sha3_256"
MIN_PASSWORD_LEN = 16
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "users.csv")
LOG_FILE = os.path.join(DATA_DIR, "log.json")


class ValidationError(Exception):

    pass


def log_event(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        username = kwargs.get(
            "username", args[0] if len(args) > 0 else "unknown"
        )
        status = "failure"
        try:
            res = func(*args, **kwargs)
            status = "success" if res else "failure"
            return res
        except Exception:
            status = "failure"
            raise
        finally:
            os.makedirs(DATA_DIR, exist_ok=True)
            log_entry = {
                "event": func.__name__,
                "user": username,
                "result": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs,
            }

            logs = []
            if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
                try:
                    with open(LOG_FILE, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except (IOError, json.JSONDecodeError):
                    logs = []

            logs.append(log_entry)
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)

    return wrapper


def generate_hash(password: str, salt: str = "00000") -> str:
    if not password or not salt:
        raise ValueError("Пароль та сіль не можуть бути порожніми.")

    if len(password) < MIN_PASSWORD_LEN:
        raise ValidationError(
            f"Пароль закороткий. Мінімальна довжина: {MIN_PASSWORD_LEN}"
        )

    salted_password = (password + salt).encode("utf-8")
    return hashlib.sha3_256(salted_password).hexdigest()


def create_user(username: str, password: str) -> tuple:
    personal_salt = str(VARIANT_NUMBER).zfill(5)
    pwd_hash = generate_hash(password, salt=personal_salt)
    return (username, pwd_hash)


def create_users(users_list: tuple) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    hashed_users = [create_user(user, pwd) for user, pwd in users_list]

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password_hash"])
        writer.writerows(hashed_users)


def load_users_db() -> list:
    users_db = []
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"Файл бази даних {CSV_FILE} не знайдено.")

    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  
        for row in reader:
            if row:
                users_db.append((row[0], row[1]))
    return users_db


@log_event
def login(username: str, password: str, users_db: list) -> bool:
    if not username or not password:
        raise ValueError("Логін або пароль не можуть бути порожніми.")

    personal_salt = str(VARIANT_NUMBER).zfill(5)
    input_hash = generate_hash(password, salt=personal_salt)

    for db_user, db_hash in users_db:
        if db_user == username and db_hash == input_hash:
            return True
    return False


def run_task3() -> None:
    print("=" * 65)
    print(
        f"Завдання 3 | Студент: {STUDENT_NAME} ({GROUP_NAME}), "
        f"Варіант: {VARIANT_NUMBER}"
    )
    print("=" * 65)

    users_to_register = (
        ("admin_user", "SuperSecretPass2026!#"),
        ("sec_analyst", "SecurePassword999!#"),
        ("dev_lead_01", "DeveloperKey_2026_x"),
        ("audit_officer", "AuditorPasscode_123"),
        ("system_tech", "SystemTechPass_9999"),
        ("guest_user1", "GuestAccess_2026_ok"),
        ("manager_usr", "ManagerPassword_777"),
        ("operator_01", "OperatorPass_333333"),
        ("data_engineer", "DataEnginePass_2026"),
        ("support_spec", "SupportAgentPass_00"),
    )

    try:
        create_users(users_to_register)
        print("[+] Користувачів успішно зареєстровано та збережено в CSV.")

        db = load_users_db()
        print("\nБаза даних користувачів (users.csv):")
        print(f"{'Логін':<18} | {'Хеш пароля (SHA3-256)'}")
        print("-" * 65)
        for u, h in db:
            print(f"{u:<18} | {h[:32]}...")

        print("\nПеревірка авторизації (Логування у log.json):")
        res_ok = login("admin_user", "SuperSecretPass2026!#", db)
        print(f"Спроба входу admin_user (правильний): {res_ok}")

        res_fail = login("admin_user", "WrongPassword12345", db)
        print(f"Спроба входу admin_user (неправильний): {res_fail}")

    except (
        FileNotFoundError,
        PermissionError,
        IOError,
        ValidationError,
        ValueError,
    ) as e:
        print(f"[!] Помилка виконання: {e}")


if __name__ == "__main__":
    run_task3()
