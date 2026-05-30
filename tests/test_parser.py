import sys
sys.path.insert(0, "./") 
from parser import _extract_amount, _extract_fee, _extract_balance, _extract_party, _extract_transaction_id 

def test_extract_fee():
    result = _extract_fee("Fee was: 500 RWF for this transaction.")
    assert result == 500.0, f"Expected 500.0, got {result}"
def test_extract_fee_no_match():
    result = _extract_fee("No fee mentioned here.")
    assert result == 0.0, f"Expected 0.0, got {result}"

def test_extract_fee_different_format():
    result = _extract_fee("Fee was: 1,000 RWF")
    assert result == 1000.0, f"Expected 1000.0, got {result}"

def test_extract_fee_with_extra_text():
    result = _extract_fee("Fee was: 750 RWF for this transaction. TxId: 12345")
    assert result == 750.0, f"Expected 750.0, got {result}"

def test_extract_fee_with_no_currency():
    result = _extract_fee("Fee was: 600 for this transaction.")
    assert result == 0.0, f"Expected 0.0, got {result}"

def test_extract_amount():
    result = _extract_amount("You have received 1,000 RWF from Collins.")
    assert result == 1000.0, f"Expected 1000.0, got {result}"

def test_extract_amount_no_match():
    result = _extract_amount("No amount mentioned here.")
    assert result == 0.0, f"Expected 0.0, got {result}"

def test_extract_amount_different_format():
    result = _extract_amount("Amount: 2,500 RWF")
    assert result == 2500.0, f"Expected 2500.0, got {result}"   

def test_extract_amount_with_extra_text():
    result = _extract_amount("You have received 3,000 RWF from Collins. TxId: 12345")
    assert result == 3000.0, f"Expected 3000.0, got {result}"

def test_extract_amount_with_no_currency():
    result = _extract_amount("You have received 4,000 from Collins.")
    assert result == 0.0, f"Expected 0.0, got {result}"

def test_extract_balance():
    result = _extract_balance("New Balance: 5,000 RWF")
    assert result == 5000.0, f"Expected 5000.0, got {result}"

def test_extract_balance_no_match():
    result = _extract_balance("No balance mentioned here.")
    assert result == 0.0, f"Expected 0.0, got {result}"

def test_extract_balance_different_format():
    result = _extract_balance("New Balance: 6,500 RWF after transaction.")
    assert result == 6500.0, f"Expected 6500.0, got {result}"

def test_extract_balance_with_extra_text():
    result = _extract_balance("New Balance: 7,000 RWF after transaction. TxId: 12345")
    assert result == 7000.0, f"Expected 7000.0, got {result}"

def test_extract_balance_with_no_currency():
    result = _extract_balance("New Balance: 8,000 after transaction.")
    assert result == 0.0, f"Expected 0.0, got {result}"

def test_extract_party_transferred_to():
    result = _extract_party("You have transferred to Jayz (123456).")
    assert result == "Jayz (123456)", f"Expected 'Jayz', got {result}"

def test_extract_party_received_from():
    result = _extract_party("You have received 1,000 RWF from Collins (****5678).")
    assert result == "Collins (****5678)", f"Expected 'Collins', got {result}"

def test_extract_party_payment_to():
    result = _extract_party("payment of 2,000 RWF to Alice 1234.")
    assert result == "Alice", f"Expected 'Alice', got {result}"

def test_extract_party_transaction_by():
    result = _extract_party("transaction of 3,000 RWF by BOB on 2024-06-01.")
    assert result == "BOB", f"Expected 'BOB', got {result}"

def test_extract_party_airtime():
    result = _extract_party("You have purchased airtime worth 500 RWF.")
    assert result == "Airtime", f"Expected 'Airtime', got {result}"

def test_extract_party_no_match():
    result = _extract_party("No party mentioned here.")
    assert result == "", f"Expected '', got {result}"

def test_extract_transaction_id_txid():
    result = _extract_transaction_id("Your transaction was successful. TxId: 123456789.")
    assert result == "123456789", f"Expected '123456789', got {result}"

def test_extract_transaction_id_financial_id():
    result = _extract_transaction_id("Financial Transaction Id: 987654321 for your reference.")
    assert result == "987654321", f"Expected '987654321', got {result}"

def test_extract_transaction_id_no_match():
    result = _extract_transaction_id("No transaction ID mentioned here.")
    assert result == "", f"Expected '', got {result}"

def test_extract_transaction_id_with_extra_text():
    result = _extract_transaction_id("Your transaction was successful. TxId: 123456789. Please keep this for your records.")
    assert result == "123456789", f"Expected '123456789', got {result}"

def test_extract_transaction_id_with_different_format():
    result = _extract_transaction_id("Financial Transaction Id: 987654321. Thank you for using our service.")
    assert result == "987654321", f"Expected '987654321', got {result}"

def test_extract_transaction_id_with_no_id():
    result = _extract_transaction_id("Your transaction was successful. Please keep this for your records.")
    assert result == "", f"Expected '', got {result}"

def test_extract_transaction_id_with_non_numeric_id():
    result = _extract_transaction_id("Your transaction was successful. TxId: ABCDEFGHIJ.")
    assert result == "", f"Expected '', got {result}"

def test_extract_transaction_id_with_partial_id():
    result = _extract_transaction_id("Your transaction was successful. TxId: 12345.")
    assert result == "12345", f"Expected '12345', got {result}" 

def test_extract_transaction_id_with_multiple_ids():
    result = _extract_transaction_id("Your transaction was successful. TxId: 123456789. Financial Transaction Id: 987654321.")
    assert result == "123456789", f"Expected '123456789', got {result}"

def test_extract_transaction_id_with_no_ids():
    result = _extract_transaction_id("Your transaction was successful. Please keep this for your records.")
    assert result == "", f"Expected '', got {result}"

def test_extract_transaction_id_with_non_numeric_financial_id():
    result = _extract_transaction_id("Financial Transaction Id: ABCDEFGHIJ for your reference.")
    assert result == "", f"Expected '', got {result}"

def test_extract_transaction_id_with_partial_financial_id():
    result = _extract_transaction_id("Financial Transaction Id: 98765 for your reference.")
    assert result == "98765", f"Expected '98765', got {result}"

