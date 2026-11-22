# UPI Transaction Reconciliation Pipeline

An end-to-end synthetic payment reconciliation pipeline built in **Python**, **Faker**, **Pandas**, and **DuckDB** to validate and reconcile **1,000,000+** bank ledger and NPCI network settlement records, isolating operational breaks and generating daily exception reports.

---

## Executive Summary (Resume Highlights)

* **Scale & Accuracy:** Generated and reconciled **1M+ synthetic UPI bank ledger and NPCI settlement records** using Python, Faker, Pandas, and DuckDB, classifying discrepancies across **status mismatches**, **amount variations**, and **missing entries** into daily operational break reports.
* **Memory-Efficient Joins:** Replaced in-memory `pd.merge()` joins on million-row datasets with **DuckDB SQL join logic** to avoid runtime memory bottlenecks while keeping validation rules centralized and repeatable.
* **Scheduled Execution:** Parameterized daily pipeline runs via `sys.argv` command-line arguments for consistent batch execution.

---

## Pipeline Architecture & Flow

```text
[Faker Synthetic Generator]
          │
          ▼
[Bank Ledger & NPCI Settlement Datasets (1M+ rows)]
          │
          ▼
[Pandas Ingestion & Schema/Pre-Checks]
          │
          ▼
[DuckDB SQL Reconciliation Engine]
   ├── Matched / Settled
   ├── Status Mismatches
   ├── Amount Variations
   └── Missing Ledger / Missing NPCI Entries
          │
          ▼
[Daily Operational Break Reports]

```

---

## Why DuckDB Over `pd.merge()` at 1M+ Rows

| Dimension | `pd.merge()` (In-Memory Pandas) | DuckDB SQL Joins (Pipeline Choice) |
| --- | --- | --- |
| **Memory Footprint** | Higher peak RAM overhead during large multi-column/outer comparisons | Vectorized execution engine with lower memory pressure on 1M+ row joins |
| **Join & Break Logic** | Multi-step DataFrame masks and post-merge column comparisons | Expressive SQL `FULL OUTER JOIN` / `LEFT` / `RIGHT` anti-joins and case rules in one query |
| **Maintainability** | Scattershot DataFrame transformations | Single-source SQL reconciliation rules easy to audit and extend |

---

## Break Categories & Reconciliation Logic

1. **Missing in NPCI Settlement (Ledger-Only):** Transaction appears in the bank ledger but has no matching NPCI settlement record—flags pending, dropped, or delayed network files.
2. **Missing in Bank Ledger (NPCI-Only):** Settlement record exists from NPCI without a corresponding bank ledger entry—flags unposted ledger entries or ingestion gaps.
3. **Status Mismatches:** Transaction status differs between bank ledger and NPCI settlement (e.g., `SUCCESS` vs. `FAILED` / `PENDING`).
4. **Amount Variations:** Transaction amounts diverge between ledger and settlement records, requiring tolerance/rounding checks and settlement investigation.

---

## Key Engineering Takeaways

* **Defensive Validation:** Enforces consistent keys, types, and null handling before comparing financial amounts and statuses so edge cases surface explicitly rather than silently dropping rows.
* **Operational Clarity:** Separates clean/matched volume from actionable exception buckets (`status_mismatch`, `amount_mismatch`, `missing_in_npci`, `missing_in_ledger`) for downstream ops and analytics teams.
* **Pragmatic Tooling:** Uses lightweight local/single-node Python + DuckDB for fast iteration and zero-cluster overhead on 1M+ row reconciliation workloads.

---
