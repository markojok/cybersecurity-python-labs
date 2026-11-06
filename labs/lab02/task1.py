"""Завдання 1: Модель користувача й облікового запису (ООП)."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import re

PASSWORD_ITERATIONS = 100_000
SESSION_TIMEOUT_SEC = 900
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9._-]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


class User:
    """Клас користувача системи з безпечним збереженням хешованого пароля."""

    def __init__(
        self, username: str, email: str, role: str = "user", active: bool = True
    ) -> None:
        self.username = username
        self.email = email
        self.role = role
        self.active = active
        self.__password_salt: bytes = b""
        self.__password_hash: str = ""

    @property
    def email(self) -> str:
        """Геттер для email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Сеттер для email з валідацією за допомогою регулярного виразу."""
        if not EMAIL_REGEX.match(value):
            raise ValueError(f"Некоректний формат email: '{value}'")
        self._email = value

    def set_password(self, password: str) -> None:
        """Встановлення пароля з використанням PBKDF2-HMAC-SHA256 та випадкової солі."""
        if not password:
            raise ValueError("Пароль не може бути порожнім.")
        self.__password_salt = os.urandom(16)
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PASSWORD_ITERATIONS,
        )
        self.__password_hash = hash_bytes.hex()

    def check_password(self, password: str) -> bool:
        """Перевірка пароля з безпечним порівнянням за часом (hmac.compare_digest)."""
        if not self.__password_hash or not self.__password_salt:
            return False
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PASSWORD_ITERATIONS,
        )
        return hmac.compare_digest(hash_bytes.hex(), self.__password_hash)

    def deactivate(self) -> None:
        """Деактивація облікового запису користувача."""
        self.active = False

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}', status='{status}')"


class Admin(User):
    """Клас адміністратора системи з підтримкою прав доступу (наслідування)."""

    def __init__(
        self,
        username: str,
        email: str,
        permissions: set[str] | list[str] | None = None,
        active: bool = True,
    ) -> None:
        super().__init__(username, email, role="admin", active=active)
        self.permissions: set[str] = (
            set(permissions) if permissions is not None else set()
        )

    def grant_permission(self, permission: str) -> None:
        """Надання права доступу."""
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        """Відкликання права доступу."""
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        """Перевірка наявності права доступу."""
        return permission in self.permissions

    def __str__(self) -> str:
        base_str = super().__str__()
        perms_str = ", ".join(sorted(self.permissions)) if self.permissions else "None"
        return f"{base_str} [Permissions: {perms_str}]"


class Session:
    """Клас сесії користувача з контролем таймауту."""

    def __init__(self, ip: str) -> None:
        self.ip = ip
        now = datetime.now(timezone.utc)
        self.login_time: datetime = now
        self.last_activity: datetime = now

    def touch(self) -> None:
        """Оновлення часу останньої активності."""
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        """Перевірка, чи не минув таймаут сесії."""
        if timeout_sec <= 0:
            raise ValueError("Параметр timeout_sec повинен бути додатним.")
        elapsed = datetime.now(timezone.utc) - self.last_activity
        return elapsed < timedelta(seconds=timeout_sec)


@dataclass
class AuditRecord:
    """Датаклас окремого запису в журналі аудиту."""

    timestamp: datetime
    username: str
    action: str


class AuditLog:
    """Клас для збереження та відображення історії аудиторських подій."""

    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def add_log(self, username: str, action: str) -> None:
        """Додавання події в журнал аудиту з поточним часом UTC."""
        record = AuditRecord(
            timestamp=datetime.now(timezone.utc),
            username=username,
            action=action,
        )
        self.records.append(record)

    def show_all(self) -> None:
        """Виведення всіх записів журналу аудиту."""
        print("=== Журнал аудиту (Audit Log) ===")
        for rec in self.records:
            time_str = rec.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"[{time_str}] User: {rec.username:<15} | Action: {rec.action}")


class UserAccount:
    """Обліковий запис, що об'єднує User, Session та AuditLog (композиція)."""

    def __init__(
        self,
        user: User,
        session: Session | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.user = user
        self.session = session
        self.audit_log = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        """Автентифікація користувача та відкриття сеансу."""
        if (
            not self.user.active
            or self.user.username != username
            or not self.user.check_password(password)
        ):
            self.audit_log.add_log(username, "login_failure")
            return False

        self.session = Session(ip=ip)
        self.session.touch()
        self.audit_log.add_log(username, "login_success")
        return True

    def is_authenticated(self) -> bool:
        """Перевірка наявності та чинності сесії (без подовження часу сесії)."""
        if self.session is None:
            return False
        return self.session.is_active(SESSION_TIMEOUT_SEC)

    def logout(self) -> None:
        """Завершення поточного сеансу."""
        if self.session is not None:
            self.audit_log.add_log(self.user.username, "logout")
            self.session = None

    def __getitem__(self, key: str) -> object:
        allowed = {"user": self.user, "session": self.session, "audit_log": self.audit_log}
        if key in allowed:
            return allowed[key]
        raise KeyError(f"Ключ '{key}' недоступний або захищений.")

    def __setitem__(self, key: str, value: object) -> None:
        if key == "user":
            if not isinstance(value, User):
                raise TypeError("Значення для 'user' повинно бути екземпляром User.")
            self.user = value
        elif key == "session":
            if value is not None and not isinstance(value, Session):
                raise TypeError("Значення для 'session' повинно бути екземпляром Session або None.")
            self.session = value
        elif key == "audit_log":
            if not isinstance(value, AuditLog):
                raise TypeError("Значення для 'audit_log' повинно бути екземпляром AuditLog.")
            self.audit_log = value
        else:
            raise KeyError(f"Ключ '{key}' не дозволений для запису.")