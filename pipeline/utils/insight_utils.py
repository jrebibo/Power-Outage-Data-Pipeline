import pandas as pd


class Insights:

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

        if "restoration_hours" not in self.df.columns:
            self.df["restoration_hours"] = (
                self.df["Event End"] - self.df["Event Start"]
            ).dt.total_seconds() / 3600 # Convert to hours


    """
    Returns a sorted list of unique years present in the dataset,
    based on the Event Start timestamp.
    """
    def observed_years(self) -> list[int]:
        if "Event Start" not in self.df.columns:
            return []

        return sorted(self.df["Event Start"]
                      .dt.year
                      .dropna()
                      .unique()
                      .astype(int)
                      .tolist())

    
    """
    Average restoration time (hours) by NERC Region.
    Returns a Series indexed by region, descending by mean hours.
    """
    def avg_restoration_by_nerc(self, round_to: int = 2) -> pd.Series:

        return (
            self.df.groupby("NERC Region (N)")["restoration_hours"]
                   .mean()
                   .round(round_to)
                   .sort_values(ascending=False)
                   .dropna() # Dropping NaN
        )

    """
    Average restoration time (hours) by NERC Region.
    Returns a Series indexed by region, descending by mean hours.
    """
    def avg_restoration_by_state(self, round_to: int = 2) -> pd.Series:

        return (
            self.df.groupby("State")["restoration_hours"]
                   .mean()
                   .round(round_to)
                   .sort_values(ascending=False)
                   .dropna() # Dropping NaN 
        )
    
    """
    Count of events by Event Type.
    Returns a Series sorted by count (descending).
    """
    def count_events_by_type(self) -> pd.Series:
        return (
            self.df["Event Type (N)"]
                .value_counts()
                .sort_values(ascending=False)
                .dropna()
        )
    
    """
    Seasonal Trends: Median restoration time (hours) by Event Month.
    Helps show seasonal patterns in restoration duration (ex: winter storms, summer heat).
    """
    def seasonal_trends_by_month(self, round_to: int = 2) -> pd.Series:

        # Ensure the month column order is correct (Jan → Dec)
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        df = self.df.copy()

        df["Event Month"] = pd.Categorical(df["Event Month"], categories=month_order, ordered=True)

        result = (
            df.groupby("Event Month", observed=True)["restoration_hours"]
              .median()                        
              .round(round_to)
              .dropna()
        )
        
        return result

    """
    Convenience printer
    """
    def print_summary(self) -> None:
        print("\n--- Quick Look Statistics & Insights ---")

        print("\nYears Observed in Dataset:")
        print(self.observed_years())

        print("\nAverage Restoration Time (hours) by NERC Region:")
        print(self.avg_restoration_by_nerc().to_string())

        print("\nAverage Restoration Time (hours) by State:")
        print(self.avg_restoration_by_state().to_string())

        print("\nTop 10 Event Type Frequency (Number of Outages):")
        print(self.count_events_by_type().head(10).to_string())
        # TODO: Not perfectly accurate because of cells with multiple Event Types (Severe Weather,Transmisison Interruption)

        print("\nSeasonal Trend — Median Restoration Time (hours) by Month:")
        print(self.seasonal_trends_by_month().to_string())

        # TODO: Other options: Average MW Demand Loss by Event Type, Percent of Events Impacting Multiple States, etc.