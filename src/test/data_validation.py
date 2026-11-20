import sys
from pathlib import Path
import pandas as pd
import numpy as np

class ValidationLedger:
    def __init__(self, ledger_rows):
        self.ledger_rows = ledger_rows

    def schema_validation(self):

        columns = {"ledger_entry_id", "upi_ref_no", "account_number", "txn_type", "bank_name", "amount", "txn_timestamp",
             "status", "counterparty_vpa"}

        missing_col = columns - set(self.ledger_rows.columns)

        if missing_col:

            raise ValueError(f"THE LEDGER FILE ARE {len(missing_col)} MISSING COLUMNS: {missing_col}")

        else:
             is_true_schema = True

        return is_true_schema, len(missing_col), missing_col

    def missing_records(self):

        req_record_count = 1000000
        df_records = round(100 * (req_record_count - len(self.ledger_rows) / req_record_count), 2)
        status = []

        if df_records > 5.00:
            is_true_record_count = False
            status.append("Critical")

        elif  1.00 < df_records < 5.00:
            is_true_record_count = False
            status.append("Warning")

        else:
            is_true_record_count = True
            status.append("OK")

        return is_true_record_count, status, df_records

    def null_values(self):
        is_null_values = True
        required_column  = ["upi_ref_no", "account_number", "txn_type", "bank_name", "amount"]

        if self.ledger_rows[required_column].isnull().any().any():

            raise ValueError("Ledger contains null values")

        else:
            is_null_values = False

        return is_null_values

    def data_transformation(self):
        ledger_rows = self.ledger_rows
        ledger_rows["status_code"] = np.where(ledger_rows["status"] == "POSTED", "00", "91")
        return ledger_rows


class ValidationNpci:
    def __init__(self, npci_rows):
        self.npci_rows = npci_rows

    def schema_validation(self):

        columns = {"rrn","payer_vpa","payee_vpa","txn_amt","txn_date","txn_time",
                   "response_code","settlement_date"}

        missing_col = columns - set(self.npci_rows.columns)

        if missing_col:
            is_true_schema = False
            raise ValueError(f"THE NPCI FILE ARE {len(missing_col)} MISSING COLUMNS: {missing_col}")

        else:
             is_true_schema = True

        return is_true_schema, len(missing_col), missing_col

    def missing_records(self):

        is_true_record_count = False
        df_records = round(100 * (1000000 - len(self.npci_rows)) / 1000000, 2)
        status = []

        if df_records > 5.00:
            status.append("Critical")

        elif 1.00 < df_records < 5.00 :
            status.append("Warning")
        else:
            is_true_record_count = True
            status.append("OK")

        return is_true_record_count, status, df_records

    def null_values(self):
        is_null_values = True
        required_column  = ["rrn","payer_vpa","payee_vpa","txn_amt","txn_date","txn_time","response_code","settlement_date"]

        if self.npci_rows[required_column].isnull().any().any():
            raise ValueError("NPCI contains null values")
        else:
            is_null_values = False

        return is_null_values

    def data_transformation(self):

        npci_rows = self.npci_rows

        npci_rows["txn_amt"] = (
            npci_rows["txn_amt"].astype(str).str.replace(",", "").astype(float)
        )
        return npci_rows



class ReportGenerator:

    def __init__(self, ledger, npci, date):
        self.ledger = ledger
        self.npci = npci
        self.date = date

    def Ledger(self):
        schema = self.ledger.schema_validation()
        records_missing = self.ledger.missing_records()
        null_valus = self.ledger.null_values()
        project_dir = Path(__file__).resolve().parents[2]
        ledger_path = project_dir / "Report" / "Ledger"

        with open(ledger_path / f"Ledger{self.date}.txt", "w") as f:
            f.write("*" * 100 + "\n")
            f.write(f"                                   DATA VALIDATION REPORT  - {self.date}     \n")
            f.write("*" * 100 + "\n")
            f.write("*" * 100 + "\n")
            f.write("* Schema Validation:\n")
            f.write("*" * 100 + "\n")
            f.write(f"*  Data Passed Schema Validation? : {schema[0]}\n")
            f.write(f"*  No. Of Missing Columns:    {schema[1]}\n")
            f.write(f"*  Missing Columns:    {schema[2]}\n")
            f.write("*" * 100 + "\n")
            f.write("* Missing Records Validation:\n")
            f.write("*" * 100 + "\n")
            f.write(f"*  Is Record Count OK: {records_missing[0]}\n")
            f.write(f"*  Status: {records_missing[1]}\n")
            f.write(f"*  Percentage Difference: {records_missing[2]}%\n")
            f.write("*" * 100 + "\n")
            f.write("* Null Values Validation:\n")
            f.write("*" * 100 + "\n")
            f.write(f"*  Contains Null Values: {null_valus}\n")
            f.write("*" * 100 + "\n")

        print("Report Generated For Ledger")


    def Npci(self):
        schema = self.npci.schema_validation()
        records_missing = self.npci.missing_records()
        null_value = self.npci.null_values()
        project_dir = Path(__file__).resolve().parents[2]
        npci_path = project_dir / "Report" / "NPCI"



        with open(npci_path / f"NPCI{self.date}.txt", "w") as f:
            f.write("*" * 100 + "\n")
            f.write(f"                                   DATA VALIDATION REPORT  - {self.date}     \n")
            f.write("*" * 100 + "\n")
            f.write("*" * 100 + "\n")
            f.write("* Schema Validation:\n")
            f.write("*" * 100 + "\n")
            f.write(f"*  Data Passed Schema Validation? : {schema[0]}\n")
            f.write(f"*  No. Of Missing Columns:    {schema[1]}\n")
            f.write(f"*  Missing Columns:    {schema[2]}\n")
            f.write("*" * 100 + "\n")
            f.write("* Missing Records Validation:\n")
            f.write("*" * 100 + "\n")
            f.write(f"*  Is Record Count OK: {records_missing[0]}\n")
            f.write(f"*  Status: {records_missing[1]}\n")
            f.write(f"*  Percentage Difference: {records_missing[2]}%\n")
            f.write("*" * 100 + "\n")
            f.write("* Null Values Validation:\n")
            f.write("*" * 100 + "\n")
            f.write(f"*  Contains Null Values: {null_value}\n")
            f.write("*" * 100 + "\n")

        print("Report Generated For NPCI")



def main():
    Date_in = sys.argv[1]

    project_dir = Path(__file__).resolve().parents[2]
    ledger_dir = project_dir / "data" / "raw" / "ledger"
    npci_dir = project_dir / "data" / "raw" / "ncpi"

    ledger_path = ledger_dir / f"ledger{Date_in}.csv"
    npci_path = npci_dir / f"npci{Date_in}.csv"

    if not ledger_path.is_file():
        raise FileNotFoundError(f"Ledger file not found: ledger{Date_in}.csv")
    if not npci_path.is_file():
        raise FileNotFoundError(f"npci file not found: npci{Date_in}.csv")



    ledger_dtypes = {
        'ledger_entry_id': 'str',
        'upi_ref_no': 'str',
        'account_number': 'str',
        'txn_type': 'str',
        'bank_name': 'str',
        'amount': 'str',
        'txn_timestamp': 'str',
        'status': 'str',
        'counterparty_vpa': 'str',
        'channel': 'str'
    }

    npci_dtypes = {
        'rrn': 'str',
        'payer_vpa': 'str',
        'payee_vpa': 'str',
        'txn_amt': 'str',
        'txn_date': 'str',
        'txn_time': 'str',
        'response_code': 'category',
        'settlement_date': 'str'
    }

    df_ledger = pd.read_csv(ledger_path, dtype=ledger_dtypes)
    df_npci = pd.read_csv(npci_path, dtype=npci_dtypes)
    print(f"Loaded ledger file - Ledger{Date_in}: {df_ledger.shape}")
    print(f"Loaded npci file - Npci{Date_in}: {df_npci.shape}")



    ledger_test = ValidationLedger(df_ledger)
    npci_test = ValidationNpci(df_npci)

    ReportGenerator(ledger_test, npci_test, Date_in).Ledger()
    ReportGenerator(ledger_test, npci_test, Date_in).Npci()

    df_ledger_clean = ledger_test.data_transformation()
    df_npci_clean = npci_test.data_transformation()

    df_ledger_clean.to_csv(f"data/silver/ledger/ledger{Date_in}.csv", index=False)
    df_npci_clean.to_csv(f"data/silver/npci/npci{Date_in}.csv", index=False)
    print("Process Completed....")

if __name__ == "__main__":
    main()