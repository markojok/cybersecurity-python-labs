import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

USERS = {
    "forensic_lead": {
        "role": "forensic_analyst",
        "clearance": 4,
        "department": "Forensics",
        "active": True,
    },
    "compliance_off": {
        "role": "compliance_officer",
        "clearance": 3,
        "department": "Compliance",
        "active": True,
    },
    "trainee_sec": {
        "role": "trainee",
        "clearance": 1,
        "department": "Training",
        "active": True,
    },
    "vendor_tech": {
        "role": "vendor_support",
        "clearance": 2,
        "department": "Vendor",
        "active": True,
    },
    "archived_usr": {
        "role": "archived",
        "clearance": 1,
        "department": "Archive",
        "active": False,
    },
}

RESOURCES = [
    ("forensic_images", 4),
    ("compliance_reports", 3),
    ("training_videos", 1),
    ("vendor_tools", 2),
    ("evidence_locker", 4),
    ("certification_docs", 1),
    ("audit_findings", 3),
    ("chain_of_custody", 4),
    ("support_tickets", 2),
    ("learning_modules", 1),
]

SECURITY_LEVELS = ("Basic", "Standard", "Protected", "Maximum")
BLOCKED_USERS = {"archived_usr", "terminated_vendor", "security_breach"}


def check_access(username: str, resource_name: str, required_level: int) -> str:
    if username not in USERS:
        return "DENY (User not found)"
    if username in BLOCKED_USERS:
        return "DENY (User is blocked)"

    user = USERS[username]
    if not user.get("active", False):
        return "DENY (Account inactive)"

    if user.get("clearance", 0) >= required_level:
        return "ALLOW"

    return "DENY (Insufficient clearance)"


def run_task2() -> None:
    print("=" * 65)
    print(
        f"Завдання 2 | Студент: {STUDENT_NAME} ({GROUP_NAME}), "
        f"Варіант: {VARIANT_NUMBER}"
    )
    print("=" * 65)

    print("Список ресурсів системи:")
    for res_name, req_lvl in RESOURCES:
        label = SECURITY_LEVELS[req_lvl - 1]
        print(f"  - {res_name:<20} (Рівень: {label})")

    print("\nРезультати перевірки доступу:")
    print("-" * 65)

    test_users = list(USERS.keys()) + ["unknown_usr"]
    for user in test_users:
        for res_name, req_lvl in RESOURCES[:3]:  
            result = check_access(user, res_name, req_lvl)
            print(f"user={user:<15} resource={res_name:<18} -> {result}")
    print("-" * 65 + "\n")


if __name__ == "__main__":
    run_task2()
