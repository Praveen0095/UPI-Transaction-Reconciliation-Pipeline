import pandas as pd
from faker import Faker
import sys
from datetime import datetime, timedelta
import numpy as np
import string

fake = Faker('en-IN')

SEED = 42
DATE = datetime.strptime(sys.argv[1], "%Y%m%d")
NUM_DAYS = 30
num_records = 1000000
handles = ["okhdfc", "oksbi", "ybl", "paytm", "upi"]
channels = ["UPI_APP", "UPI_QR", "UPI_COLLECT"]

break_choices = ['MATCH', 'AMOUNT_DIFF', 'STATUS_DIFF', 'MISSING_IN_NPCI', 'MISSING_IN_LEDGER']
break_weights = [0.85, 0.04, 0.04, 0.04, 0.03]
assigned_breaks = np.random.choice(break_choices, size=num_records, p=break_weights)


RATES = {
    "MISSING_IN_LEDGER": 0.01,
    "MISSING_IN_NETWORK": 0.01,
    "AMOUNT_MISMATCH": 0.005,
    "DUPLICATE": 0.003,
    "TIMING_DIFF": 0.02,
    "STATUS_MISMATCH": 0.005,
}
REVERSAL_RATE = 0.02
LEDGER_TS_FORMAT = "%Y/%m/%d %H:%M:%S"


ledger_rows = []
ncpi_rows = []

pool_size = 10000
upi_pool = [fake.bban() for _ in range(pool_size)]
bank_pool = [fake.bank() for _ in range(pool_size)]
payer_pool = [fake.user_name() + "@" + np.random.choice(handles) for _ in range(pool_size)]
payee_pool = [fake.user_name() + "@" + np.random.choice(handles) for _ in range(pool_size)]

letters = np.array(list(string.ascii_uppercase), dtype='U1')
rand_indices = np.random.randint(0, 26, size=(num_records, 4))
prefix_arr = letters[rand_indices]
prefixes = prefix_arr[:, 0] + prefix_arr[:, 1] + prefix_arr[:, 2] + prefix_arr[:, 3]
suffixes = np.array([f"{i:013d}" for i in np.random.permutation(num_records)])


upi_refs = np.char.add(prefixes, suffixes)
bank_names = np.random.choice(bank_pool, size=num_records)
payer_ids = np.random.choice(payer_pool, size=num_records)
payee_ids = np.random.choice(payee_pool, size=num_records)
account_nums = np.random.randint(1111111111, 9999999999, size=num_records)
chosen_channels = np.random.choice(channels, size=num_records)
amounts = np.round(np.random.uniform(10.0, 5000.0, num_records), 2)

base_time = datetime(DATE.year, DATE.month, DATE.day)
timestamps = [base_time + timedelta(seconds=int(sec)) for sec in np.random.randint(0, 40000, num_records)]

# Build ledger dataframe
ledger_mask = assigned_breaks != 'MISSING_IN_LEDGER'
ledger_df = pd.DataFrame({
    'ledger_entry_id': [f"LGD_{i:07d}" for i in range(1, num_records + 1)],
    'upi_ref_no': upi_refs,
    'account_number': account_nums,
    'txn_type': 'DEBIT',
    'bank_name': bank_names,
    'amount': [f"{val:.3f}" for val in amounts],
    'txn_timestamp': [ts.strftime("%Y/%m/%d %H:%M:%S") for ts in timestamps],
    'status': 'POSTED',
    'counterparty_vpa': payee_ids,
    'channel': chosen_channels
})
ledger_df = ledger_df[ledger_mask].copy()

# Build npci dataframe
npci_amounts = np.where(assigned_breaks == 'AMOUNT_DIFF', amounts + 10.0, amounts)
response_codes = np.where(assigned_breaks == 'STATUS_DIFF', '91', '00')
settlement_dates = [(ts + timedelta(days=1)).strftime("%d/%m/%Y") for ts in timestamps]

npci_mask = assigned_breaks != 'MISSING_IN_NPCI'
npci_df = pd.DataFrame({
    'rrn': upi_refs,
    'payer_vpa': payer_ids,
    'payee_vpa': payee_ids,
    'txn_amt': [f"{val:,.2f}" for val in npci_amounts],
    'txn_date': [ts.strftime("%d/%m/%Y") for ts in timestamps],
    'txn_time': [ts.strftime("%H:%M:%S") for ts in timestamps],
    'response_code': response_codes,
    'settlement_date': settlement_dates
})


npci_df = npci_df[npci_mask].copy()
date_str = DATE.strftime("%Y%m%d")

pd.DataFrame(ledger_df).to_csv(f"data/raw/ledger/ledger{date_str}.csv", index=False)
pd.DataFrame(npci_df).to_csv(f"data/raw/ncpi/npci{date_str}.csv", index=False)
