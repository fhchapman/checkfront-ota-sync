#!/usr/bin/env python3
"""
Run net price sync from a CSV file.
CSV must have columns: checkfront_code, net_amount, currency (optional), source (optional).
Example:
  checkfront_code,net_amount,currency,source
  CFPP-290317,428.28,USD,Viator
  CFPP-290318,150.00,EUR,Get Your Guide
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.net_price_sync import sync_net_amount_from_csv

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_net_price_sync.py <path_to_csv>")
        print("CSV columns: checkfront_code, net_amount, currency (optional), source (optional)")
        sys.exit(1)
    csv_path = sys.argv[1]
    n = sync_net_amount_from_csv(csv_path)
    print(f"Processed {n} rows.")
