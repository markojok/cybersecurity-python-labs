"""Завдання 2: Варіант 5 — Сканер доступності мережевих сервісів та перевірка портів."""

from dataclasses import asdict, dataclass
import csv
import json
import logging
from pathlib import Path
import re
import socket
import time

IP_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)

# Словник стандартних портових сервісів для автоматичного визначення
PORT_SERVICES = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    5432: "PostgreSQL",
    8080: "HTTP-ALT",
}


@dataclass
class TargetResult:
    """Дані про результат сканування хоста/порту."""

    host: str
    port: int
    service: str
    status: str
    response_time_ms: float
    notes: str


def validate_host(host: str) -> bool:
    """Валідація доменного імені або IP-адреси за допомогою регулярних виразів."""
    return bool(IP_REGEX.match(host) or DOMAIN_REGEX.match(host) or host == "localhost")


def scan_target(host: str, port: int, service: str, timeout: float) -> TargetResult:
    """Перевірка доступності хоста/порту через мережевий сокет."""
    if not validate_host(host):
        logging.warning("Некоректний синтаксис хоста: %s", host)
        return TargetResult(
            host=host,
            port=port,
            service=service,
            status="OFFLINE",
            response_time_ms=0.0,
            notes="Invalid Host Syntax",
        )

    if not (1 <= port <= 65535):
        logging.warning("Некоректний номер порту (%d) для %s", port, host)
        return TargetResult(
            host=host,
            port=port,
            service=service,
            status="OFFLINE",
            response_time_ms=0.0,
            notes="Invalid Port Range (1-65535)",
        )

    start_time = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect((host, port))
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        sock.close()
        return TargetResult(
            host=host,
            port=port,
            service=service,
            status="ONLINE",
            response_time_ms=round(elapsed_ms, 1),
            notes="OK",
        )
    except socket.timeout:
        sock.close()
        return TargetResult(
            host=host,
            port=port,
            service=service,
            status="OFFLINE",
            response_time_ms=0.0,
            notes="TIMEOUT (Connection timed out)",
        )
    except socket.gaierror:
        sock.close()
        return TargetResult(
            host=host,
            port=port,
            service=service,
            status="OFFLINE",
            response_time_ms=0.0,
            notes="DNS Resolution Failed",
        )
    except (ConnectionRefusedError, OSError) as err:
        sock.close()
        return TargetResult(
            host=host,
            port=port,
            service=service,
            status="OFFLINE",
            response_time_ms=0.0,
            notes=f"Refused/Unreachable ({type(err).__name__})",
        )


def run_scanner(
    targets_file: Path, out_csv: Path, timeout: float, verbose: bool = False
) -> None:
    """Головна функція для виконання сканування цілей з файлу та формування звіту."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(message)s")

    if not targets_file.exists():
        logging.error("Файл з цілями не знайдено: %s", targets_file)
        return

    logging.info("Starting service availability scan from target list %s...", targets_file)

    with open(targets_file, "r", encoding="utf-8") as f:
        targets_data = json.load(f)

    results: list[TargetResult] = []
    for item in targets_data:
        host = str(item.get("host", ""))
        port = int(item.get("port", 80))
        service = item.get("service") or PORT_SERVICES.get(port, "UNKNOWN")

        res = scan_target(host, port, service, timeout)
        results.append(res)

    print()
    print(f"{'Target Host':<24} {'Port':<6} {'Service':<12} {'Status':<8} {'Response Time':<14} {'Notes'}")
    print("-" * 90)
    for r in results:
        resp_str = f"{r.response_time_ms} ms" if r.status == "ONLINE" else "-"
        print(f"{r.host:<24} {r.port:<6} {r.service:<12} {r.status:<8} {resp_str:<14} {r.notes}")

    total = len(results)
    online_cnt = sum(1 for r in results if r.status == "ONLINE")
    offline_cnt = total - online_cnt

    online_pct = (online_cnt / total * 100) if total > 0 else 0.0
    offline_pct = (offline_cnt / total * 100) if total > 0 else 0.0

    print("\n=== Scan Statistics ===")
    print(f"Total Scanned : {total}")
    print(f"Online        : {online_cnt} ({online_pct:.1f}%)")
    print(f"Offline       : {offline_cnt} ({offline_pct:.1f}%)\n")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["host", "port", "service", "status", "response_time_ms", "notes"]
        )
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))

    logging.info("Detailed scan report saved to %s", out_csv)