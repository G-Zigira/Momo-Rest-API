"""
dsa.py — Data Structures & Algorithms for transaction search.

Implements and benchmarks:
  1. Linear Search  — O(n) scan through a list
  2. Dictionary Lookup — O(1) average key access

Run standalone to see benchmark results.
"""

import time
import random


# ──────────────────────────────────────────────
# 1. Linear Search
# ──────────────────────────────────────────────

def linear_search(transactions: list[dict], target_id: int) -> dict | None:
    """
    Scan every element from left to right until the id matches.
    Time complexity : O(n)
    Space complexity: O(1)
    """
    for txn in transactions:
        if txn["id"] == target_id:
            return txn
    return None


# ──────────────────────────────────────────────
# 2. Dictionary (Hash-map) Lookup
# ──────────────────────────────────────────────

def build_index(transactions: list[dict]) -> dict[int, dict]:
    """
    Build a hash-map from id → transaction dict.
    Building cost : O(n)  (done once at startup)
    """
    return {txn["id"]: txn for txn in transactions}


def dict_lookup(index: dict[int, dict], target_id: int) -> dict | None:
    """
    Direct key access in a Python dict (hash table).
    Time complexity : O(1) average
    Space complexity: O(n)
    """
    return index.get(target_id)


# ──────────────────────────────────────────────
# Benchmark
# ──────────────────────────────────────────────

def benchmark(transactions: list[dict], iterations: int = 10_000) -> dict:
    """
    Compare linear search vs dictionary lookup over `iterations` random lookups.
    Returns a dict with timing results and analysis.
    """
    if not transactions:
        return {}

    ids = [txn["id"] for txn in transactions]
    index = build_index(transactions)

    # --- Linear search timing ---
    t0 = time.perf_counter()
    for _ in range(iterations):
        linear_search(transactions, random.choice(ids))
    linear_time = time.perf_counter() - t0

    # --- Dictionary lookup timing ---
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

    # Verify correctness
    txn_linear = linear_search(txns, 10)
    idx = build_index(txns)
    txn_dict = dict_lookup(idx, 10)
    assert txn_linear == txn_dict, "Mismatch — results should be identical!"
    print(f"\nCorrectness check passed. Both return: id={txn_linear['id']}, "
          f"type={txn_linear['transaction_type']}, amount={txn_linear['amount']} RWF")
