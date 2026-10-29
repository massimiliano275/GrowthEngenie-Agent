"""Blocca un commit che contiene segreti probabili. Usato come pre-commit hook.

Installazione (una volta, dalla radice della repo):
    python tools/check_secrets.py --install
"""
import re
import subprocess
import sys
from pathlib import Path

PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|api[_-]?secret|secret|password|token)\s*[=:]\s*['\"]?[A-Za-z0-9+/=_\-]{16,}"), "chiave o segreto assegnato"),
    (re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"), "token di bot Telegram"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "chiave privata"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "chiave AWS"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "chiave API sk-"),
]
SKIP = {".env.example"}


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f and Path(f).name not in SKIP]


def main():
    if "--install" in sys.argv:
        hook = Path(".git/hooks/pre-commit")
        hook.write_text("#!/bin/sh\npython tools/check_secrets.py\n", encoding="utf-8")
        print(f"hook installato: {hook}")
        return 0
    found = []
    for f in staged_files():
        blob = subprocess.run(["git", "show", f":{f}"], capture_output=True).stdout
        text = blob.decode("utf-8", errors="ignore")
        for n, line in enumerate(text.splitlines(), 1):
            for rx, label in PATTERNS:
                if rx.search(line):
                    found.append(f"{f}:{n}: {label}")
    if found:
        print("COMMIT BLOCCATO — possibili segreti:")
        print("\n".join(found))
        print("Spostali in .env. Se e' un falso positivo: git commit --no-verify, solo dopo averlo controllato.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
