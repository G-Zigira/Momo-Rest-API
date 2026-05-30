import time
import random


# linear search

def linear_search(transactions: list[dict], target_id: int) -> dict | None:
    
    for txn in transactions:
        if txn["id"] == target_id:
            return txn
    return None

# dictionary-based lookup

def build_index(transactions: list[dict]) -> dict[int, dict]:
    
    return {txn["id"]: txn for txn in transactions}


def dict_lookup(index: dict[int, dict], target_id: int) -> dict | None:
    
    return index.get(target_id)

# Benchmarking function to compare linear search vs dictionary lookup.

def benchmark(transactions: list[dict], iterations: int = 10_000) -> dict:
    
    if not transactions:
        return {}

    ids = [txn["id"] for txn in transactions]
    index = build_index(transactions)

# Linear search timing
    t0 = time.perf_counter()
    for _ in range(iterations):
        linear_search(transactions, random.choice(ids))
    linear_time = time.perf_counter() - t0

# dictionary lookup timing
    t0 = time.perf_counter()
    for _ in range(iterations):
        dict_lookup(index, random.choice(ids))
    dict_time = time.perf_counter() - t0

    speedup = linear_time / dict_time if dict_time > 0 else float("inf")

    return {
        "n_records": len(transactions),
        "iterations": iterations,
        "linear_search_total_s": round(linear_time, 6),
        "dict_lookup_total_s": round(dict_time, 6),
        "linear_avg_us": round(linear_time / iterations * 1_000_000, 4),
        "dict_avg_us": round(dict_time / iterations * 1_000_000, 4),
        "speedup_factor": round(speedup, 1),
    }

# extracts the party involved in the transaction, such as the sender or recipient. It looks for common patterns in the SMS body to identify the party name and any associated identifiers (like phone numbers or masked account numbers). If it cannot determine the party, it returns "N/A".
if __name__ == "__main__":
    from parser import parse_xml

    txns = parse_xml("modified_sms_v2.xml")
    print(f"Dataset: {len(txns)} records\n")

    results = benchmark(txns, iterations=50_000)

    print("=" * 50)
    print("  BENCHMARK RESULTS")
    print("=" * 50)
    print(f"  Records          : {results['n_records']}")
    print(f"  Iterations       : {results['iterations']:,}")
    print(f"  Linear  total    : {results['linear_search_total_s']} s")
    print(f"  Dict    total    : {results['dict_lookup_total_s']} s")
    print(f"  Linear  avg      : {results['linear_avg_us']} µs/op")
    print(f"  Dict    avg      : {results['dict_avg_us']} µs/op")
    print(f"  Speedup          : {results['speedup_factor']}×  faster with dict")
    print("=" * 50)

# verifies if its correct
    txn_linear = linear_search(txns, 10)
    idx = build_index(txns)
    txn_dict = dict_lookup(idx, 10)
    assert txn_linear == txn_dict, "Mismatch — results should be identical!"
    print(f"\nCorrectness check passed. Both return: id={txn_linear['id']}, "
          f"type={txn_linear['transaction_type']}, amount={txn_linear['amount']} RWF")
