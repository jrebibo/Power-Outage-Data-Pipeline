# DOE-417 Power Outage Data Pipeline

This repository contains a data pipeline that ingests, cleans, normalizes, and aggregates
annual power outage incident reports from the U.S. Department of Energy (DOE) **OE-417 Electric Emergency and Disturbance Events** dataset.

---

## Data Information

Source: https://doe417.pnnl.gov/

### Fields (based on DOE Annual Summary Excel files)
Each file contains ~300–400 outage incident records and typically includes:

| Column Name | Description |
|-------------|-------------|
| `Event Month` | Month the outage occured as a string |
| `Date Event Began` | Outage start date (MM/DD/YYYY) |
| `Time Event Began` | Outage start time (hh:mm AM/PM) |
| `Date of Restoration` | Outage end date |
| `Time of Restoration` | Outage end time |
| `Area Affected` | State / County information, semi-structured text (e.g., `"California: Riverside County;"`) |
| `NERC Region` | Reliability region(s) involved (e.g., `"MRO/RF"`, `"SERC, MRO"`) |
| `Alert Criteria` | Free-text narrative describing the event |
| `Event Type` | Categorized outage/incident type (vandalism, severe weather, cyber event, etc.) |
| `Demand Loss (MW)` | Megawatts lost (if reported) |
| `Number of Customers Affected` | Total customers affected (if reported) |

### Data Considerations

- **Inconsistent formatting**
  - Event types may include prefixes (`"- Vandalism"`) or combined labels (`"Actual Physical Attack/Vandalism"`).
  - NERC regions may use commas, slashes, or spaces as delimiters (`"MRO/RF"`, `"SERC, MRO"`, `"SERC / RF"`).

- **Incomplete/Null Values**
  - ~40% of incidents contain `0` MW loss **and** `0` customers affected.
  - Some fields are `Unknown`, empty, or inconsistently structured across years.

- **Date & Time Formatting**
  - Dates and times appear in **separate columns** and require merging into a timestamp.

- **Geospatial components**
  - `Area Affected` contains state + county information but is not split into separate columns.

The goal of the pipeline is to normalize these inconsistencies into clean, analysis-ready data.

---

## Data Directory

To add and analyze additional data, place the downloaded DOE Excel files in the *doe_147_data*:

/doe_147_data/2023_Annual_Summary.xlsx

## Data Directory

To add and analyze additional data, place the downloaded DOE Excel files in the *doe_147_data*:

/doe_147_data/2023_Annual_Summary.xls

Update the hardcoded file list in power_outage_data_pipeline.py to process addtional data from this directory. Future state should read in any files automatically and determine if they can be processed. 

---

## Running the Application (MacOS Terminal)

```sh
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# or (if not using a requirements file)
pip install pandas numpy

# Run the Power Outage Pipeline
python3 pipeline/power_outage_data_pipeline.py

# Exit the virtual environment
deactivate
```

## Future State & Features

- **Programatic Fucntionality/Data Access**
  - Provide processed outage data via a lightweight REST API endpoint
  - Expose simplified get_outages(start_date, end_date, state) functions
    - /api/outages
    - /api/events/:id

- **Database + Storage Evolution**
  - Store normalized data in  PostgreSQL / BigQuery

- **AI/RAG (Retrieval-Augmented Generation)**
  - Naive RAG - Q&A over outage events using LLM (Ollama) + vector search

- **Analytics & Insights**
  - Trend analysis (outages over time, cause attribution)
  - Cost estimation of outages (optional: integrate EIA rate data)

## NERC Regions (North American Electric Reliability Corporation)

| Code     | Region Name                               | Coverage Summary |
|----------|--------------------------------------------|------------------|
| **WECC** | Western Electricity Coordinating Council   | CA, AZ, NV, OR, WA, UT, ID, MT, WY, CO + parts of Canada/Mexico |
| **MRO**  | Midwest Reliability Organization           | MN, ND, SD, NE, IA, WI + parts of Canada |
| **TRE**  | Texas Reliability Entity (ERCOT)           | Most of Texas; independent grid with limited ties to Eastern/Western Interconnect |
| **SERC** | SERC Reliability Corporation               | Southeast + mid-Atlantic (TN, GA, FL, AL, NC, SC, VA, KY, MS) |
| **RF**   | ReliabilityFirst                           | Mid-Atlantic + Midwest (PA, NJ, OH, MD, MI, parts of IN/IL) |
| **NPCC** | Northeast Power Coordinating Council       | NY, New England + eastern Canada |
| **FRCC** *(historical)* | Florida Reliability Coordinating Council | Former Florida footprint — merged into **SERC** in 2019 |
| **SPP RE** *(historical)* | Southwest Power Pool Regional Entity     | Former SPP oversight area — compliance oversight transferred to **MRO/SERC** |
