import os
import random
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

passwords = ["DataS3cur3!", "123", "Crypt0@Analysis", "test123", "Quantum#2023", "access", "Secur1ty@Pro", "password1", "Adv@nced123", "guest123"]

criteria = {"min_length": 12, "require_digits": True, "require_upper": True, "require_special": True}

forbidden_passwords = {"123", "test123", "access", "password1", "guest123", "admin"}

def evaluate_password(password: str, passwords_list: list) -> str:
    min_len = criteria["min_length"]

    if password in forbidden_passwords or len(password) < min_len:
        return "Заборонений"

    has_digit = any(char.isdigit() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_special = any(not char.isalnum() for char in password)

    all_criteria_met = (
        has_digit and has_upper and has_lower and has_special
    )


    if all_criteria_met:
        is_unique = passwords_list.count(password) == 1
        if len(password) >= (min_len + 4) and is_unique:
            return "Дуже сильний"
        return "Сильний"


    
    if len(password) >= min_len and (has_digit or has_upper or has_special):
        return "Середній"

    return "Слабкий"


def run_task1() -> None:
    print("=" * 65)
    print(
        f"Завдання 1 | Студент: {STUDENT_NAME} ({GROUP_NAME}), "
        f"Варіант: {VARIANT_NUMBER}"
    )
    print("=" * 65)

    random.seed(42)
    sample_indices = random.sample(range(len(passwords)), 3)
    duplicates = [passwords[i] for i in sample_indices]
    extended_passwords = passwords + duplicates

    print(f"{'Пароль':<22} | {'Довжина':<8} | {'Оцінка надійності'}")
    print("-" * 65)

    for pwd in extended_passwords:
        rating = evaluate_password(pwd, extended_passwords)
        print(f"{pwd:<22} | {len(pwd):<8} | {rating}")
    print("-" * 65 + "\n")

if __name__ == "__main__":
    run_task1()