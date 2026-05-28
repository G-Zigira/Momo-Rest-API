"""
parser.py — Parse modified_sms_v2.xml and convert SMS records to JSON objects.
"""

import xml.etree.ElementTree as ET
import re
import json


def _detect_type(body: str) -> str:
    """Heuristic: classify transaction type from SMS body text."""
    body_lower = body.lower()
    if "cash out" in body_lower:
        return "cash_out"
    if "airtime" in body_lower:
        return "airtime"
    if "payment" in body_lower:
        return "payment"
    if "received" in body_lower:
        return "incoming"
    if "sent" in body_lower:
        return "outgoing"
    return "unknown"


def _extract_amount(body: str) -> float:
    """Pull the first 'NNN RWF' amount from the message body."""
    match = re.search(r"([\d,]+)\s+RWF", body)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0


def _extract_fee(body: str) -> float:
    """Extract fee amount; default 0 if not found."""
    match = re.search(r"Fee:\s*([\d,]+)\s*RWF", body)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0


def _extract_balance(body: str) -> float:
    """Extract 'new MoMo balance' figure."""
    match = re.search(r"balance is ([\d,]+)\s*RWF", body)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0


def _extract_party(body: str) -> str:
    """Extract sender/receiver name and number (e.g. 'Alice (0788111001)')."""
    match = re.search(r"(?:from|to)\s+([A-Za-z]+\s*\([^)]+\))", body)
    if match:
        return match.group(1)
    match = re.search(r"(?:from|to)\s+([^.]+?)\s*\.", body)
    if match:
        return match.group(1).strip()
    return "N/A"


def _extract_transaction_id(body: str) -> str:
    match = re.search(r"Transaction ID:\s*(\S+)", body)
    return match.group(1) if match else "N/A"


def parse_xml(filepath: str) -> list[dict]:
    """
    Parse an SMS XML file and return a list of transaction dictionaries.

    Each dictionary contains:
        id, address, date_ms, readable_date, body,
        transaction_type, amount, fee, balance_after,
        party, transaction_id
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    transactions = []
    for sms in root.findall("sms"):
        body = sms.get("body", "")
        record = {
            "id": int(sms.get("id", 0)),
            "address": sms.get("address", ""),
            "date_ms": int(sms.get("date", 0)),
            "readable_date": sms.get("readable_date", ""),
            "body": body,
            "transaction_type": _detect_type(body),
            "amount": _extract_amount(body),
            "fee": _extract_fee(body),
            "balance_after": _extract_balance(body),
            "party": _extract_party(body),
            "transaction_id": _extract_transaction_id(body),
        }
        transactions.append(record)

    return transactions


if __name__ == "__main__":
    txns = parse_xml("modified_sms_v2.xml")
    print(f"Parsed {len(txns)} transactions.")
    print(json.dumps(txns[:2], indent=2))
