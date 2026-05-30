"""
parser.py — Parse modified_sms_v2.xml and convert SMS records to JSON objects.
Handles all real MTN MoMo SMS body formats found in the dataset.
"""

import xml.etree.ElementTree as ET
import re
import json

# takes SMS body and classsifies it into categories.
def _detect_type(body: str) -> str:
   
    b = body.lower()
    if "*113*r*" in b or "bank deposit" in b:
        return "bank_deposit"
    if "*164*s*" in b or "direct payment" in b or "debit" in b:
        return "debit"
    if "transferred to" in b or "*165*s*" in b:
        return "outgoing_transfer"
    if "you have received" in b or "financial transaction id" in b:
        return "incoming"
    if "airtime" in b and ("payment" in b or "txid" in b or "*162*" in b):
        return "airtime"
    if "your payment of" in b or "txid" in b or "payment of" in b:
        return "payment"
    if "reversal" in b:
        return "reversal"
    if "cash out" in b or "cash withdrawal" in b:
        return "cash_out"
    return "other"

# Uses regex to find the first occurence of an amount.
def _extract_amount(body: str) -> float:
    
    match = re.search(r"([\d,]+)\s*RWF", body)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0

# Extracts fee amount from body, with 0 as a default when nothing is found,
def _extract_fee(body: str) -> float:
   
    m = re.search(r"[Ff]ee was:?\s*([\d,]+)\s*RWF", body)
    if m:
        return float(m.group(1).replace(",", ""))
    return 0.0


# looks for a phrase such as "balance"  which is followed by a number and "RWF"
def _extract_balance(body: str) -> float:
    
    m = re.search(r"[Nn]ew\s+[Bb]alance\s*:?\s*([\d,]+)\s*RWF", body)
    if m:
        return float(m.group(1).replace(",", ""))
    return 0.0

# tries to find who the transaction was with.
def _extract_party(body: str) -> str:
  
    m = re.search(r"transferred to\s+([A-Za-z][\w\s]+?)\s*\((\d+)\)", body)
    if m:
        return f"{m.group(1).strip()} ({m.group(2)})"
    
    m = re.search(r"(?:received\s+[\d,]+\s+RWF\s+)?from\s+([A-Za-z][\w\s]+?)\s*\((\*+\d+)\)", body)
    if m:
        return f"{m.group(1).strip()} ({m.group(2)})"
   
    m = re.search(r"payment of [\d,]+ RWF to\s+([A-Za-z][\w\s]+?)\s+\d{4,}", body)
    if m:
        return m.group(1).strip()
   
    m = re.search(r"transaction of [\d,]+ RWF by\s+([A-Z][A-Z\s]+?)(?:\s+on)", body)
    if m:
        return m.group(1).strip()
   
    if "airtime" in body.lower():
        return "Airtime"
    return "N/A"

# looks for a phrase such as "Transaction ID:" followed by an identifier.
def _extract_transaction_id(body: str) -> str:
    """Extract transaction/financial ID."""
    
    m = re.search(r"TxId:?\s*(\d+)", body)
    if m:
        return m.group(1)
    
    m = re.search(r"Financial Transaction Id:\s*(\d+)", body)
    if m:
        return m.group(1)
    return "N/A"

# Its the function that ties everything together
def parse_xml(filepath: str) -> list[dict]:
   
    tree = ET.parse(filepath)
    root = tree.getroot()

    transactions = []
    for idx, sms in enumerate(root.findall("sms"), start=1):
        body = sms.get("body", "")
        record = {
            "id": idx,                             
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

# it calls the parse_xml function 
if __name__ == "__main__":
    txns = parse_xml("modified_sms_v2.xml")
    print(f"Parsed {len(txns)} transactions.\n")
    
    from collections import Counter
    counts = Counter(t["transaction_type"] for t in txns)
    for ttype, cnt in counts.most_common():
        print(f"  {cnt:5d}  {ttype}")
    print()
    print("Sample record:")
    print(json.dumps(txns[0], indent=2))
