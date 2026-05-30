import sys
sys.path.insert(0, "./")
from dsa  import linear_search, build_index, dict_lookup, benchmark


sample_transactions = [
    {"id": 1, "amount": 100.0, "party": "Saka"},
    {"id": 2, "amount": 200.0, "party": "Collins"},
    {"id": 3, "amount": 300.0, "party": "Trossard"},
]

def test_linear_search_found():
    result = linear_search(sample_transactions, 2)
    assert result is not None, "Expected to find transaction with ID 2"
    assert result["party"] == "Collins", f"Expected party 'Collins', got {result['party']}" 

def test_linear_search_not_found():
    result = linear_search(sample_transactions, 999)
    assert result is None, "Expected to not find transaction with ID 999"

def test_build_index():
    index = build_index(sample_transactions)
    assert isinstance(index, dict), "Expected index to be a dictionary"
    assert len(index) == len(sample_transactions), f"Expected index length {len(sample_transactions)}, got {len(index)}"
    for t in sample_transactions:
        assert t["id"] in index, f"Expected transaction ID {t['id']} in index"
        assert index[t["id"]]["party"] == t["party"], f"Expected party '{t['party']}' for ID {t['id']}, got '{index[t['id']]['party']}'"

def test_dict_lookup_found():
    index = build_index(sample_transactions)
    result = dict_lookup(index, 3)
    assert result is not None, "Expected to find transaction with ID 3"
    assert result["party"] == "Trossard", f"Expected party 'Trossard', got {result['party']}"

def test_dict_lookup_not_found():
    index = build_index(sample_transactions)
    result = dict_lookup(index, 999)
    assert result is None, "Expected to not find transaction with ID 999"

def test_benchmark():
    results = benchmark(sample_transactions, loops=1000)
    assert "n_records" in results, "Expected 'n_records' in benchmark results"
    assert "iterations" in results, "Expected 'iterations' in benchmark results"
    assert "linear_search_total_s" in results, "Expected 'linear_search_total_s' in benchmark results"
    assert "dict_lookup_total_s" in results, "Expected 'dict_lookup_total_s' in benchmark results"
    assert "linear_avg_time" in results, "Expected 'linear_avg_time' in benchmark results"
    assert "dict_avg_time" in results, "Expected 'dict_avg_time' in benchmark results"
    assert "speedup_factor" in results, "Expected 'speedup_factor' in benchmark results"
    assert results["n_records"] == len(sample_transactions), f"Expected n_records {len(sample_transactions)}, got {results['n_records']}"
    assert results["iterations"] == 1000, f"Expected iterations 1000, got {results['iterations']}"

if __name__ == "__main__":
    test_linear_search_found()
    test_linear_search_not_found()
    test_build_index()
    test_dict_lookup_found()
    test_dict_lookup_not_found()
    test_benchmark()
    print("All tests passed!")


