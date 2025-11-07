import pandas as pd
from pathlib import Path


class Utils: 

    HEADERS = [
        "Event Month",
        "Date Event Began",
        "Time Event Began",
        "Date of Restoration",
        "Time of Restoration",
        "Area Affected",
        "NERC Region",
        "Alert Criteria",
        "Event Type",
        "Demand Loss (MW)",
        "Number of Customers Affected",
    ]

    """
    Load an CSV (.csv) file into a pandas DataFrame using pd.read_csv.
    """
    @staticmethod
    def load_csv(file_path: Path) -> pd.DataFrame:
        data = pd.DataFrame()
        try:
            data = pd.read_csv(file_path)
        except FileNotFoundError as e:
            print(f"[ERROR] File not found: {file_path}")
            print(e)
        except Exception as e:
            # Catch-all for any other pandas/IO issues
            print(f"[ERROR] Failed to read Excel file: {file_path}")
            print(e)

        return data
    

    """
    Load an Excel (.xlsx) file into a pandas DataFrame using pd.read_excel.
    """
    @staticmethod
    def load_excel(file_path: Path, sheet_name: str = "Sheet1", headers: int = 1 ) -> pd.DataFrame:

        data = pd.DataFrame()

        try:
            data = pd.read_excel(file_path, sheet_name=sheet_name, header=headers)

        except FileNotFoundError as e:
            print(f"[ERROR] File not found: {file_path}")
            print(e)
        except ValueError as e:
            # Handles missing sheet names or invalid sheet references
            print(f"[ERROR] Invalid sheet name when reading: {file_path}")
            print(e)
        except Exception as e:
            # Catch-all for any other pandas/IO issues
            print(f"[ERROR] Failed to read Excel file: {file_path}")
            print(e)

        return data
    
    """
    Load an Excel (.xlsx) file into a pandas DataFrame using pd.read_excel fixed headers.
    """
    @staticmethod
    def load_excel_with_fixed_headers(file_path: Path, sheet_name: str = "Sheet1", skiprows: int = 2 ) -> pd.DataFrame:

        data = pd.DataFrame()

        try:
            data = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)
                # TODO: Use parse_dates to normalize
                # parse_dates={
                #     "Event Start": ["Date Event Began", "Time Event Began"],
                #     "Event End":   ["Date of Restoration", "Time of Restoration"],
                # }


            # Apply fixed headers to normalize them across data set years
            data.columns = Utils.HEADERS  

        except FileNotFoundError as e:
            print(f"[ERROR] File not found: {file_path}")
            print(e)
        except ValueError as e:
            # Handles missing sheet names or invalid sheet references
            print(f"[ERROR] Invalid sheet name when reading: {file_path}")
            print(e)
        except Exception as e:
            # Catch-all for any other pandas/IO issues
            print(f"[ERROR] Failed to read Excel file: {file_path}")
            print(e)

        return data