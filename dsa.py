import time
import random



def linear_search(transactions: list[dict], target_id: int) -> dict | None:
    
    for t in transactions:
        if t["id"] == target_id:
            return t
    return None


def build_index(transactions: list[dict]) -> dict[int, dict]:
    
    return {t["id"]: t for t in transactions} #creates a hash map (dictionary) where the keys are transaction IDs and the values are the transaction records themselves allowing a O(1) average time complexity lookups by ID


def dict_lookup(index: dict[int, dict], target_id: int) -> dict | None:
    
    return index.get(target_id) #gets transaction by ID from the hash map


def benchmark(transactions: list[dict], loops: int = 10_000) -> dict:
    
    if not transactions:
        return {}

    ids = [t["id"] for t in transactions]
    index = build_index(transactions)

    
    start_time = time.perf_counter()
    for _ in range(loops):
        linear_search(transactions, random.choice(ids))
    linear_time = time.perf_counter() - start_time

 
    start_time = time.perf_counter()
    for _ in range(loops):
        dict_lookup(index, random.choice(ids))
    dict_lookup_time = time.perf_counter() - start_time

    #speedup is based on an assumption that linear_time is greater than dict_lookup_time, which is generally expected for large datasets
    speedup = linear_time / dict_lookup_time if dict_lookup_time > 0 else float("inf")

    return {
        "n_records": len(transactions),
        "iterations": loops,
        "linear_search_total_s": round(linear_time, 6),
        "dict_lookup_total_s": round(dict_lookup_time, 6),
        "linear_avg_time": round(linear_time / loops * 1_000_000, 4), # * 1_000_000 converts seconds to microseconds for better readability
        "dict_avg_time": round(dict_lookup_time / loops * 1_000_000, 4),
        "speedup_factor": round(speedup, 1),
    }


if __name__ == "__main__":
    from parser import parse_xml

    txns = parse_xml("Momo-rest-API/modified_sms_v2.xml")
    print(f"Dataset: {len(txns)} records\n")

    results = benchmark(txns, loops=30_000)

    print("  BENCHMARK RESULTS\n\n")
    print(f"  Records          : {results['n_records']}")
    print(f"  Iterations       : {results['iterations']:,}")
    print(f"  Linear  total    : {results['linear_search_total_s']} s")
    print(f"  Dict    total    : {results['dict_lookup_total_s']} s")
    print(f"  Linear  avg      : {results['linear_avg_time']} µs/op")
    print(f"  Dict    avg      : {results['dict_avg_time']} µs/op")
    print(f"  Speedup          : {results['speedup_factor']}×  faster with dict")

    
    txn_linear = linear_search(txns, 10)
    idx = build_index(txns)
    txn_dict = dict_lookup(idx, 10)
    assert txn_linear == txn_dict, "Mismatch — results should be identical!"
    print(f"\nCorrectness check passed. Both return: id={txn_linear['id']}, "
          f"type={txn_linear['transaction_type']}, amount={txn_linear['amount']} RWF")
