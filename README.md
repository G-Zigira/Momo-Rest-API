Members 
  Collins Gathungu 
  Guivera Zigira
  Ineza Henry Jay-z
  Denzel Ngabo
  Laura Keza


"# Momo-Rest-API" 
# MoMo SMS Transaction API

A lightweight REST API that parses MTN MoMo (Mobile Money) SMS messages from an XML backup, structures them into searchable transaction records, and serves them over HTTP with full CRUD support.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [List Transactions](#1-list-transactions)
  - [Get Transaction by ID](#2-get-transaction-by-id)
  - [Search Transactions](#3-search-transactions)
  - [Create Transaction](#4-create-transaction)
  - [Update Transaction](#5-update-transaction)
  - [Delete Transaction](#6-delete-transaction)
  - [DSA Benchmark](#7-dsa-benchmark)
- [Parser Module](#parser-module)
  - [Transaction Types](#transaction-types)
  - [Extraction Logic](#extraction-logic)
- [Transaction Object Schema](#transaction-object-schema)
- [Error Handling](#error-handling)
- [Architecture Notes](#architecture-notes)

---

## Overview

MoMo SMS messages contain structured financial data — amounts, fees, balances, counterparty names, and transaction IDs — but they arrive as free-text SMS. This project does three things:

1. **Parses** an XML export of SMS messages (`modified_sms_v2.xml`) using regex-based extractors tuned to real MTN MoMo message formats.
2. **Indexes** the parsed records in a hash-map for O(1) lookups by ID.
3. **Serves** the data through a REST API built on Python's standard library `http.server`, with pagination, search, and full CRUD operations.

No external frameworks or databases are required. Everything runs in-memory from a single XML file.

---

## Project Structure

```
.
├── parser.py               # XML parser and SMS field extractors
├── server.py               # REST API server (http.server)
├── dsa.py                  # Data structure utilities (indexing, search, benchmark)
├── modified_sms_v2.xml     # SMS data export (input file)
└── README.md
```

---

## Prerequisites

- **Python 3.10+** (uses `type1 | type2` union syntax)
- No third-party packages needed — the project uses only the standard library.

---

## Getting Started

1. **Place your SMS export** in the project root as `modified_sms_v2.xml`.

2. **Test the parser** standalone to verify your XML file is read correctly:

   ```bash
   python parser.py
   ```

   This prints the total number of parsed transactions, a breakdown by type, and the first record as JSON.

3. **Start the API server:**

   ```bash
   python server.py
   ```

   By default the server binds to `0.0.0.0:8080`. To use a different port:

   ```bash
   python server.py 5000
   ```

4. **Send a test request:**

   ```bash
   curl -u admin:momo2024 http://localhost:8080/transactions?limit=2
   ```

---

## Authentication

All endpoints require **HTTP Basic Auth**.

| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `momo2024` |

Include the header with every request:

```
Authorization: Basic YWRtaW46bW9tbzIwMjQ=
```

Unauthenticated requests receive a `401` response with a `WWW-Authenticate` challenge header.

---

## API Endpoints

### 1. List Transactions

```
GET /transactions
```

Returns a paginated list of transactions with optional type filtering.

**Query Parameters:**

| Parameter | Type   | Default | Description                          |
|-----------|--------|---------|--------------------------------------|
| `page`    | int    | 1       | Page number                          |
| `limit`   | int    | 20      | Results per page                     |
| `type`    | string | —       | Filter by `transaction_type` value   |

**Example:**

```bash
curl -u admin:momo2024 "http://localhost:8080/transactions?page=1&limit=2&type=incoming"
```

**Response (200):**

```json
{
  "page": 1,
  "limit": 2,
  "total": 84,
  "transactions": [
    {
      "id": 3,
      "date_ms": 1710000000000,
      "readable_date": "2024-03-09 12:00:00",
      "body": "You have received 5,000 RWF from Alice (***001)...",
      "transaction_type": "incoming",
      "amount": 5000.0,
      "fee": 0.0,
      "balance_after": 12500.0,
      "party": "Alice (***001)",
      "transaction_id": "8834720193"
    }
  ]
}
```

---

### 2. Get Transaction by ID

```
GET /transactions/{id}
```

Returns a single transaction. The `id` is the sequential index assigned during parsing (starting at 1).

**Example:**

```bash
curl -u admin:momo2024 http://localhost:8080/transactions/3
```

**Response (200):** A single transaction object.

**Response (404):**

```json
{
  "error": "Transaction 3 not found."
}
```

---

### 3. Search Transactions

```
GET /transactions/search?q=...
```

Case-insensitive substring search across `party`, `transaction_type`, `transaction_id`, and `id`.

**Example:**

```bash
curl -u admin:momo2024 "http://localhost:8080/transactions/search?q=alice"
```

**Response (200):**

```json
{
  "query": "alice",
  "results": [ ... ],
  "count": 4
}
```

---

### 4. Create Transaction

```
POST /transactions
```

Creates a new transaction record. The server auto-assigns `id`, `date_ms`, and `readable_date`.

**Required Body Fields:**

| Field              | Type   | Description                              |
|--------------------|--------|------------------------------------------|
| `amount`           | number | Transaction amount in RWF                |
| `transaction_type` | string | Category (e.g. `incoming`, `outgoing_transfer`) |
| `party`            | string | Counterparty name                        |

**Optional Body Fields:**

| Field            | Type   | Default          |
|------------------|--------|------------------|
| `address`        | string | `""`             |
| `body`           | string | `""`             |
| `fee`            | number | `0`              |
| `balance_after`  | number | `0`              |
| `transaction_id` | string | Auto (`T0001`)   |

**Example:**

```bash
curl -u admin:momo2024 \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"amount": 3000, "transaction_type": "outgoing_transfer", "party": "Charlie (0788333003)"}' \
  http://localhost:8080/transactions
```

**Response (201):** The newly created transaction object with its assigned `id`.

---

### 5. Update Transaction

```
PUT /transactions/{id}
```

Partially updates an existing transaction. Send only the fields you want to change. The `id` field is protected and cannot be overwritten.

**Example:**

```bash
curl -u admin:momo2024 \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{"amount": 6000, "fee": 100}' \
  http://localhost:8080/transactions/3
```

**Response (200):** The full updated transaction object.

---

### 6. Delete Transaction

```
DELETE /transactions/{id}
```

Permanently removes a transaction from the in-memory store.

**Example:**

```bash
curl -u admin:momo2024 -X DELETE http://localhost:8080/transactions/3
```

**Response (200):**

```json
{
  "message": "Transaction 3 deleted successfully."
}
```

---

### 7. DSA Benchmark

```
GET /dsa/benchmark
```

Runs 50,000 iterations comparing linear search (O(n)) vs. dictionary/hash-table lookup (O(1)) on the loaded dataset.

**Example:**

```bash
curl -u admin:momo2024 http://localhost:8080/dsa/benchmark
```

**Response (200):**

```json
{
  "dataset_size": 500,
  "iterations": 50000,
  "linear_search_seconds": 2.847,
  "dict_lookup_seconds": 0.019,
  "speedup_factor": "149.8x",
  "note": "Dictionary lookup uses a hash table (O(1) avg). Linear search is O(n)."
}
```

---

## Parser Module

`parser.py` can be used independently of the server. It reads an SMS XML backup and returns a list of structured transaction dictionaries.

```python
from parser import parse_xml

transactions = parse_xml("modified_sms_v2.xml")
print(f"Found {len(transactions)} transactions")
```

### Transaction Types

The parser classifies each SMS into one of these categories based on keyword matching (checked in priority order):

| Type                | Trigger Keywords                              |
|---------------------|-----------------------------------------------|
| `bank_deposit`      | `*113*r*`, `bank deposit`                     |
| `debit`             | `*164*s*`, `direct payment`, `debit`          |
| `outgoing_transfer` | `transferred to`, `*165*s*`                   |
| `incoming`          | `you have received`, `financial transaction id` |
| `airtime`           | `airtime` combined with `payment`/`txid`/`*162*` |
| `payment`           | `your payment of`, `txid`, `payment of`       |
| `reversal`          | `reversal`                                    |
| `cash_out`          | `cash out`, `cash withdrawal`                 |
| `other`             | Anything that doesn't match above             |

### Extraction Logic

Each SMS body is passed through five regex-based extractors:

| Extractor       | What It Finds                         | Pattern Example          |
|-----------------|---------------------------------------|--------------------------|
| `_extract_amount`         | First `NNN RWF` figure       | `5,000 RWF`              |
| `_extract_fee`            | `Fee was: NNN RWF`           | `Fee was: 150 RWF`       |
| `_extract_balance`        | `New balance: NNN RWF`       | `New Balance: 12,500 RWF`|
| `_extract_party`          | Name and number of counterparty | `Alice (***001)`      |
| `_extract_transaction_id` | `TxId:` or `Financial Transaction Id:` | `TxId: 8834720193` |

---

## Transaction Object Schema

Every transaction record (parsed from XML or created via the API) follows this structure:

| Field              | Type   | Description                                  |
|--------------------|--------|----------------------------------------------|
| `id`               | int    | Sequential identifier (1-indexed from parser, auto-incremented for POST) |
| `date_ms`          | int    | Timestamp in milliseconds since Unix epoch   |
| `readable_date`    | string | Human-readable date string                   |
| `body`             | string | Full original SMS text                       |
| `transaction_type` | string | Classified category (see table above)        |
| `amount`           | float  | Transaction amount in RWF                    |
| `fee`              | float  | Fee charged in RWF                           |
| `balance_after`    | float  | MoMo balance after the transaction           |
| `party`            | string | Counterparty name/number, or `"N/A"`         |
| `transaction_id`   | string | MoMo transaction reference, or `"N/A"`       |

---

## Error Handling

All errors return JSON in a consistent format:

```json
{
  "error": "Description of what went wrong."
}
```

| Status | Meaning                                                    |
|--------|------------------------------------------------------------|
| 400    | Request body is not valid JSON                             |
| 401    | Missing or invalid Basic Auth credentials                  |
| 404    | Endpoint not found, or requested transaction ID not found  |
| 422    | JSON is valid but required fields are missing (POST only)  |

---

## Architecture Notes

- **In-memory storage.** All data lives in a Python list. Changes made through the API (POST, PUT, DELETE) are lost when the server restarts; the XML file is never modified.
- **Single-threaded.** The server uses `http.server.HTTPServer`, which handles one request at a time. For concurrent use, swap in `ThreadingHTTPServer` or deploy behind a reverse proxy.
- **No external dependencies.** The entire project runs on the Python standard library.
- **Hash-map indexing.** The `dsa.py` module builds a `dict[int, dict]` index for O(1) lookups by ID. The index is rebuilt after every create, update, or delete operation — acceptable for small datasets but worth reconsidering at scale.
- **Sequential IDs.** The parser assigns IDs starting at 1 based on document order in the XML, not from any field in the SMS data. New records created via POST continue from the highest existing ID.