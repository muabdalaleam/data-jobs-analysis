import os
import sqlite3
import pandas as pd
import glob
from pathlib import Path

DATABASE_PATH = "./data/raw_database.db"
FILES_PATTERN = "./data/[linkedin,upwork,guru]*.csv"

def get_table_name(csv_filename):
    return f"{Path(csv_filename).stem}"

def main():
    csv_files = glob.glob(FILES_PATTERN)
    
    if not csv_files:
        return
    
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        table_name = get_table_name(os.path.basename(csv_file))

        try:
            df.to_sql(table_name, conn, if_exists='fail', index=False)
            print("Created a new table: ", csv_file)
        except:
            print(f"Failed creating the table: {table_name}")
            continue
    
    conn.close()

if __name__ == "__main__":
    main()
