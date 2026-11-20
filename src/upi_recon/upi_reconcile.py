import sys
import pandas as pd
from pathlib import Path
import duckdb


class Breaker:
    def __init__(self, merged_df, report_path,date_str):
        self.merged_df = merged_df
        self.report_path = report_path
        self.date_str = date_str


    def breaker_report(self):
        merged_df = self.merged_df
        report_path = self.report_path
        date_str = self.date_str
        total_records = len(merged_df)
        total_match = (merged_df["break_type"] == "MATCH").sum()
        total_miss_ledger = (merged_df["break_type"] == "MISSING_IN_LEDGER").sum()
        total_miss_npci = (merged_df["break_type"] == "MISSING_IN_NPCI").sum()
        total_amt_mismatch = (merged_df["break_type"] == "AMOUNT_DIFF").sum()
        total_mis_status = (merged_df["break_type"] == "STATUS_DIFF").sum()

        with open(self.report_path/ f"Breaker_report{date_str}.txt", "w") as f:
            f.write("*" * 100 + "\n")
            f.write("*" + f"             BREAKER REPORT - {date_str} " + "\n")
            f.write("*" * 100 + "\n")
            f.write("*" * 100 + "\n")
            f.write(f"* TOTAL RECORDS:  {total_records} "+ "\n" )
            f.write(f"* TOTAL MATCH:  {total_match}" + "\n")
            f.write(f"* TOTAL MISSING LEDGER DATA:  {total_miss_ledger} "+ "\n")
            f.write(f"* TOTAL MISSING NPCI DATA:   {total_miss_npci}"+ "\n")
            f.write(f"* TOTAL AMOUNT MISMATCH: {total_amt_mismatch} "+ "\n")
            f.write(f"* TOTAL STATUS MISMATCH:  {total_mis_status}"+ "\n")
            f.write("*" * 100 + "\n")

        print("Report generated Sucessfully")






def main():

    Date_in = sys.argv[1]
    project_dir = Path(__file__).resolve().parents[2]
    ledger_dir = project_dir / "data" / "silver" / "ledger"
    npci_dir = project_dir / "data" / "silver" / "npci"
    report_dir = project_dir / "Report" / "Breaker"

    ledger_path = ledger_dir / f"ledger{Date_in}.csv"
    npci_path = npci_dir / f"npci{Date_in}.csv"

    if not ledger_path.is_file():
        raise FileNotFoundError(f"Ledger file not found: ledger{Date_in}.csv")
    if not npci_path.is_file():
        raise FileNotFoundError(f"npci file not found: npci{Date_in}.csv")

    df_ledger = pd.read_csv(ledger_path)
    df_npci = pd.read_csv(npci_path)



    query = """
    SELECT 
        l.ledger_entry_id,
        l.upi_ref_no AS ledger_ref,
        n.rrn AS npci_ref,
        l.amount AS ledger_amount,
        n.txn_amt AS npci_amount,
        l.status_code AS ledger_status,
        n.response_code AS npci_status,
        CASE 
            WHEN l.upi_ref_no IS NULL THEN 'MISSING_IN_LEDGER'
            WHEN n.rrn IS NULL THEN 'MISSING_IN_NPCI'
            WHEN l.amount <> n.txn_amt THEN 'AMOUNT_DIFF'
            WHEN l.status_code<> n.response_code THEN 'STATUS_DIFF'
            ELSE 'MATCH'
        END AS break_type
    FROM df_ledger l
    FULL OUTER JOIN df_npci n ON l.upi_ref_no = n.rrn
    """

    merged_df = duckdb.sql(query).df()


    print("UPI reconcilation process completed")
    print("Generating Reports for Breaker....")
    Breaker(merged_df, report_dir,Date_in).breaker_report()
    pd.DataFrame(merged_df).to_csv(f"data/breaker_data/breaker{Date_in}.csv", index=False)
    print("Process Completed...")


if __name__ == "__main__":
    main()