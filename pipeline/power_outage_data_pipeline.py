from pathlib import Path
import pandas as pd

from utils.data_utils import Utils
from utils.normalize_utils import Normalization
from utils.insight_utils import Insights



DATA_DIRECTORY = Path("doe_147_data")         
DEFAULT_SHEET = "Sheet1"

class PowerOutageDataPipeline:


    def __init__(
        self,
        data_dir: Path = Path("doe_147_data"),
        file_list: list[str] = None,
        sheet_name: str = "Sheet1",
    ):
        # Data location and naming
        self.data_dir = data_dir
        self.file_list = file_list or []
        self.sheet_name = sheet_name

        # Data Frams for each stage of the data
        '''
        Can save raw or cleaned data for auditability or debugging.
        '''
        self.raw_df: pd.DataFrame | None = None         # raw data df (read_raw())
        self.cleaned_df: pd.DataFrame | None = None     # cleaned data df (clean())
        self.normalized_df: pd.DataFrame | None = None  # normalized data df (normalize())

    

    """
    Step 1: READ RAW
    Reads only the files defined in file_list.
    """
    def read_raw(self) -> pd.DataFrame:
        if not self.file_list:
            print("No files provided in file_list")
            return pd.DataFrame()

        dataframes = []

        print(f"Reading {len(self.file_list)} files from {self.data_dir}...")
        for filename in self.file_list:
            file_path = self.data_dir / filename
            print(f" - {file_path.name}")

            df = Utils.load_excel_with_fixed_headers(file_path, sheet_name=self.sheet_name)
            if not df.empty:
                dataframes.append(df)

        if not dataframes:
            print("No non-empty sheets loaded.")
            return pd.DataFrame()

        self.raw_df = pd.concat(dataframes, ignore_index=True)
        return self.raw_df



    """
    # Step 2: CLEAN
    """
    def clean(self) -> pd.DataFrame:
        if self.raw_df is None or self.raw_df.empty:
            raise RuntimeError("clean() called before read_raw()")

        df = self.raw_df.copy()
        df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]

        self.cleaned_df = df
        return self.cleaned_df



    """
    # Step 3: NORMALIZE
    """
    def normalize(self) -> pd.DataFrame:
        if self.cleaned_df is None or self.cleaned_df.empty:
            raise RuntimeError("normalize() called before clean()")

        # Copy cleaned_df to keep record and setup normalized_df
        normalized_df = self.cleaned_df.copy()

        area_affected = Normalization.untangle_area_affected(normalized_df["Area Affected"])
        
        normalized_df = (
            normalized_df.reset_index(drop=True)
                .reset_index(names="row_index")
                .merge(area_affected, on="row_index", how="left")
                .drop(columns=["row_index"])
)

        # Apply combine_date_time normalization to create datetime stamp for 'event_start'
        normalized_df["Event Start"] = Normalization.combine_date_time(
            normalized_df["Date Event Began"],
            normalized_df["Time Event Began"]
        )

        # Apply combine_date_time normalization to create datetime stamp for 'event_end'
        normalized_df["Event End"] = Normalization.combine_date_time(
            normalized_df["Date of Restoration"],
            normalized_df["Time of Restoration"]
        )
        # TODO: Implement Normalization.combine_date_time(): Map County/State to timezone and convert to UTC


        normalized_df["NERC Region (N)"] = Normalization.normalize_nerc(normalized_df["NERC Region"])
        # TODO: Implement Normalization.normalize_nerc_region_to_county(): Map County/State to NERC Region for each entery

        normalized_df["Alert Criteria (N)"] = Normalization.normalize_alert_criteria(normalized_df["Alert Criteria"])
        normalized_df["Event Type (N)"] = Normalization.normalize_event_type(normalized_df["Event Type"])



        self.normalized_df = normalized_df[[
            "Event Month",
            "Event Start",
            "Event End",
            "State",
            "County",
            "NERC Region (N)",
            "Alert Criteria (N)",
            "Event Type (N)",
            "Demand Loss (MW)",
            "Number of Customers Affected",
        ]]

        return self.normalized_df



    """
    # Step 4: SAVE
    Save the data - for now this is a simple .csv export but sets up a larger data storage to a cloud based backend
    """
    def save(self, output_path: Path) -> None:
        if self.normalized_df is None or self.normalized_df.empty:
            raise RuntimeError("save() called before normalize()")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.normalized_df.to_csv(output_path, index=False)

        print(f"Saved dataset to: {output_path}")



    """
    # Step 5: INSIGHTS
    Quick Look Statistics & Insights - Generates basic statistics/insights
    """
    def insights(self) -> None:
        if self.normalized_df is None or self.normalized_df.empty:
            raise RuntimeError("insights() called before normalize()")
        
        insights = Insights(self.normalized_df)
        insights.print_summary()



if __name__ == "__main__":
    data_files=[
        "2021_Annual_Summary.xls",
        "2022_Annual_Summary.xls",
        "2023_Annual_Summary.xls",
    ]

    pipeline = PowerOutageDataPipeline(
        data_dir=Path("doe_147_data"),
        file_list=data_files
    )

    # Use to take a look at the data that has been read in
    df_raw = pipeline.read_raw()
    print("\nPreview of data:\n")
    print(df_raw.head())          # First 5 rows
    print(df_raw.columns.tolist()) 

    pipeline.clean()
    pipeline.normalize()
    pipeline.save(Path("data_output/combined_outages.csv"))
    pipeline.insights()