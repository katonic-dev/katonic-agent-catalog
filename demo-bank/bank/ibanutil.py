"""IBAN helpers for the invented countries used in this demo."""

from __future__ import annotations

import re

IBAN_SHAPE = re.compile(r"^([A-Z]{2})(\d{2})([A-Z]{4})(\d{14})$")


def _to_digits(text: str) -> str:
    return "".join(str(int(c, 36)) for c in text)


def check_digits(country: str, bank_code: str, account: str) -> str:
    """Return the two correct check digits (mod 97) for an IBAN-shaped number."""
    rearranged = bank_code + account + country + "00"
    remainder = int(_to_digits(rearranged)) % 97
    return f"{98 - remainder:02d}"


def make_iban(country: str, bank_code: str, account: str) -> str:
    return f"{country}{check_digits(country, bank_code, account)}{bank_code}{account}"


def is_valid(iban: str) -> bool:
    text = iban.replace(" ", "").upper()
    if not IBAN_SHAPE.match(text):
        return False
    rearranged = text[4:] + text[:4]
    return int(_to_digits(rearranged)) % 97 == 1


def mask(iban: str) -> str:
    return iban[:4] + "*" * (len(iban) - 8) + iban[-4:]
