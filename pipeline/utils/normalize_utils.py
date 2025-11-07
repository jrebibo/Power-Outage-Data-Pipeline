
import pandas as pd
import re
from typing import List, Tuple, Optional


class Normalization: 

    """
    UTC Timestamps: Combine date + time into a pandas datetime64.
    Returns a datetime Series with NaT where conversion fails.
    """
    @staticmethod
    def combine_date_time(date_series: pd.Series, time_series: pd.Series, county_series: pd.Series=[]) -> pd.Series:
        # Convert to pandas datetime 
        date_series = pd.to_datetime(
            date_series.astype(str).str.strip() + " " + time_series.astype(str).str.strip(),
            errors="coerce"
        )

        # TODO: Map county_series to timezones and convert to UTC
        # TODO: Debug missing timestamps

        return date_series
    
    """
    Normalize NERC Region values by uppercasing, replacing delimiters,
    removing unnecessary spaces, and deduping.
    """
    @staticmethod
    def normalize_nerc(series: pd.Series) -> pd.Series:

        # Clean NERC Region Strings
        def clean(region: str) -> str:
            if not isinstance(region, str):
                return ""

            # Uppercase, standardize delimiters
            clean = region.upper().replace("/", ",").replace(" ", "").replace(" ", ",").replace(";", ",")


            # Split on commas, drop blanks, dedupe while preserving order
            parts = [p for p in clean.split(",") if p]
            unique = list(dict.fromkeys(parts))  # preserve order

            return ",".join(unique)

        # Apply to entire series, return new series
        return series.apply(clean)
    

    """
    NERC regions: Map NERC Region to counties to merge with normalized data
    Returns a Series with a single NERC Region to merge
    """
    @staticmethod
    def normalize_nerc_region_to_county(nerc_series: pd.Series, state_series: pd.Series, county_series: pd.Series) -> pd.Series:

        # TODO: Implement mapping of county to proper NERC Region for entries with multiple regions (e.g. MRO/SERC)
        # Fallback: Use state if there is not county
        # Issue: Some states are in multiple timzones and there is not enough information

        return nerc_series
    
    """
    Event Type: Normalize values
    - remove leading dashes, split on dash, Title Case each entry
    """
    @staticmethod
    def normalize_event_type(series: pd.Series) -> pd.Series:

        def clean(value: str) -> str:
            if not isinstance(value, str):
                return ""

            # Remove leading dashes, surrounding whitespace
            value = value.lstrip("-").strip()

            value = value.replace("-", ",")
            value = value.replace("/", ",")

            # Split on dash to remove spaces, preserve spaces inside event type
            parts = []
            for p in value.split(","):
                cleaned = p.strip()
                if cleaned:
                    parts.append(cleaned.title())

            # Join with comma delimiter
            return ",".join(parts)

        return series.apply(clean)

    """
    Alert Criter: Cleans leading special characters and whitespace from the column.
    """ 
    @staticmethod
    def normalize_alert_criteria(series: pd.Series) -> pd.Series:

        def clean(value: str) -> str:
            if not isinstance(value, str):
                return ""

            # Normalize spaces and trim
            return value.strip()

        return series.apply(clean)


    """
    Affected Area: Parse an Affected Area Cell
        Area Affected: State: County, County;  
    Parse a single 'Area Affected' cell into a list of (state, county-or-None).
    """
    @staticmethod
    def parse_affected_area_cell(cell: str) -> List[Tuple[str, Optional[str]]]:
        if not isinstance(cell, str):
            return []

        cell = cell.strip()
        if not cell:
            return []

        items: List[Tuple[str, Optional[str]]] = []

        # Find each 'State:' marker and its span
        # State names can include spaces and periods (e.g., 'District of Columbia')
        matches = list(re.finditer(r"\s*([^:;]+?)\s*:\s*", cell))
        if not matches:
            # No 'State:' pattern; treat the whole cell as a bare state
            return [(cell, None)]

        # For each state marker, counties block is – from end of this match to start of next match (or end of string)
        for i, m in enumerate(matches):
            state = m.group(1).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(cell)
            counties_block = cell[start:end].strip()

            # If counties_block is empty (or just a trailing delimiter), it's a state with no counties
            if not counties_block:
                items.append((state, None))
                continue

            # Trim any trailing semicolons/commas
            counties_block = counties_block.rstrip(";, ").strip()

            if not counties_block:
                items.append((state, None))
                continue

            # Split by commas into individual counties; keep full names like 'Anderson County'
            for county in counties_block.split(","):
                name = county.strip()
                if name:
                    items.append((state, name))

        return items

    
    """
    Area Affected: Convert a Series of 'Area Affected' strings into a normalized DataFrame:
        index (original row index), state, county
    One output row per (state, county) pair; state or county can be None if absent.

    Data Example: Kentucky: Oldham County, Jefferson County, Fayette County, Franklin County; Virginia: Wise County;
    """
    @staticmethod
    def untangle_area_affected(series: pd.Series) -> pd.DataFrame:
        records = []

        for idx, cell in series.fillna("").items():
            pairs = Normalization.parse_affected_area_cell(cell)

            if not pairs:
                records.append({"row_index": idx, "State": None, "County": None})

            else:
                for state, county in pairs:
                    records.append({
                        "row_index": idx, 
                        "State": state or None, 
                        "County": county or None
                        })

        return pd.DataFrame.from_records(records, columns=["row_index", "State", "County"])
    


