"""Головний модуль запуску Лабораторної роботи №2 (демонстрація та CLI-утиліта)."""

import argparse
from pathlib import Path
import sys
import time

from labs.lab02.task1 import Admin, Session, User, UserAccount
from labs.lab02.task2 import run_scanner


def run_demo() -> None:
    """Сценарій демонстрації функціоналу Завдання 1 (ООП)."""
    print("=" * 65)
    print("ДЕМОНСТРАЦІЯ ЗАВДАННЯ 1: ООП Модель користувачів та сесій")
    print("=" * 65)

    user = User(username="j_smith", email="j.smith@corp.ua", role="analyst")
    user.set_password("SecurePassword2026!")
    print(f"[+] Створено користувача: {user}")

    try:
        user.email = "invalid_email_format"
    except ValueError as e:
        print(f"[!] Валідація email спрацювала: {e}")

    admin = Admin(
        username="sys_admin",
        email="admin@corp.ua",
        permissions=["read", "write"],
    )
    admin.set_password("AdminSecret2026!")
    admin.grant_permission("execute")
    print(f"[+] Створено адміністратора: {admin}")

    account = UserAccount(user=user)

    print("\n--- Спроба входу з неправильним паролем ---")
    success_wrong = account.login("j_smith", "WrongPassword", "192.168.1.50")
    print(f"Результат входу: {success_wrong} (Автентифіковано: {account.is_authenticated()})")

    print("\n--- Спроба успішного входу ---")
    success_ok = account.login("j_smith", "SecurePassword2026!", "192.168.1.50")
    print(f"Результат входу: {success_ok} (Автентифіковано: {account.is_authenticated()})")

    test_session = Session("192.168.1.50")
    time.sleep(1.1)
    is_active_fast = test_session.is_active(timeout_sec=1)
    print(f"\n[Тест таймауту] Сесія після 1.1 сек (таймаут 1 сек): {is_active_fast}")

    print(f"\n[__getitem__] Користувач з акаунту: {account['user']}")
    try:
        _ = account["__password_hash"]
    except KeyError as e:
        print(f"[!] Захист приватності спрацював: {e}")

    account.logout()
    print(f"\nПісля виходу автентифіковано: {account.is_authenticated()}\n")
    account.audit_log.show_all()


def main() -> None:
    """Точка входу CLI для запуску команд demo та analyze."""
    parser = argparse.ArgumentParser(
        description="Лабораторна робота №2: CLI утиліти кібербезпеки"
    )
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")

    subparsers.add_parser("demo", help="Запустити демонстрацію Завдання 1 (ООП)")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Запустити сканер доступності сервісів (Варіант 5)"
    )
    analyze_parser.add_argument(
        "--targets",
        type=Path,
        default=Path("labs/lab02/data/data_v05/targets.json"),
        help="Шлях до JSON-файлу цілей сканування",
    )
    analyze_parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Таймаут підключення в секундах (дефолт: 2.0)",
    )
    analyze_parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("labs/lab02/data/scan_results.csv"),
        help="Шлях для вивантаження звіту CSV",
    )
    analyze_parser.add_argument(
        "--verbose", action="store_true", help="Детальний режим логування"
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        run_scanner(args.targets, args.out_csv, args.timeout, args.verbose)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()