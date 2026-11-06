# Лабораторна робота №2. Розробка консольних утиліт для задач кібербезпеки

**Варіант 5:** Сканер доступності мережевих сервісів та перевірка портів

---

## 1. Установлення залежностей

Активуйте віртуальне середовище проєкту з кореневого каталогу репозиторію та встановіть/оновіть залежності:

```bash
# Активація віртуального середовища (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Оновлення залежностей
pip install -r requirements.txt

labs/lab02/
├── __init__.py
├── main.py              # Головна точка входу CLI (команди demo та analyze)
├── task1.py             # ООП-модель користувачів, сесій та аудиту (Завдання 1)
├── task2.py             # Модуль мережевого сканера портів (Завдання 2)
├── README.md            # Інструкція запуску та документація утиліти
└── data/
    ├── targets.json     # Вхідні тестові дані для Варіанта 5
    └── scan_results.csv # Згенерований CSV-звіт доступності вузлів

[
  {"host": "127.0.0.1", "port": 22},
  {"host": "127.0.0.1", "port": 80},
  {"host": "localhost", "port": 443},
  {"host": "192.0.2.10", "port": 80},
  {"host": "198.51.100.20", "port": 443},
  {"host": "203.0.113.30", "port": 22},
  {"host": "service.example.invalid", "port": 8080},
  {"host": "db.example.invalid", "port": 5432},
  {"host": "bad host name", "port": 80},
  {"host": "999.10.10.10", "port": 443},
  {"host": "api.example.invalid", "port": 70000}
]

[INFO] Starting service availability scan from target list labs\lab02\data\targets.json...
[WARNING] Некоректний синтаксис хоста: bad host name
[WARNING] Некоректний синтаксис хоста: 999.10.10.10
[WARNING] Некоректний номер порту (70000) для api.example.invalid

Target Host              Port   Service      Status   Response Time  Notes
------------------------------------------------------------------------------------------
127.0.0.1                22     SSH          OFFLINE  -              TIMEOUT (Connection timed out)
127.0.0.1                80     HTTP         OFFLINE  -              TIMEOUT (Connection timed out)
localhost                443    HTTPS        OFFLINE  -              TIMEOUT (Connection timed out)
192.0.2.10               80     HTTP         OFFLINE  -              TIMEOUT (Connection timed out)
198.51.100.20            443    HTTPS        OFFLINE  -              TIMEOUT (Connection timed out)
203.0.113.30             22     SSH          OFFLINE  -              TIMEOUT (Connection timed out)
service.example.invalid  8080   HTTP-ALT     OFFLINE  -              DNS Resolution Failed
db.example.invalid       5432   PostgreSQL   OFFLINE  -              DNS Resolution Failed
bad host name            80     HTTP         OFFLINE  -              Invalid Host Syntax
999.10.10.10             443    HTTPS        OFFLINE  -              Invalid Host Syntax
api.example.invalid      70000  UNKNOWN      OFFLINE  -              Invalid Port Range (1-65535)

=== Scan Statistics ===
Total Scanned : 11
Online        : 0 (0.0%)
Offline       : 11 (100.0%)

[INFO] Detailed scan report saved to labs\lab02\data\scan_results.csv