# Nassau Candy — Factory-to-Customer Shipping Route Efficiency

Interactive Streamlit dashboard for route-level logistics intelligence.

## Features

- Executive KPI overview
- Factory → customer state route benchmarking
- Top 10 and bottom 10 routes
- Route efficiency score
- US shipping efficiency heatmap
- Geographic bottleneck detection
- Ship-mode performance comparison
- Cost / sales / gross-profit context
- Route drill-down
- Order-level shipment timeline
- Date, region, state, ship-mode, factory and delay-threshold filters
- Data-quality validation
- CSV downloads

## Project structure

```text
Nassau_Candy_Logistics/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── Nassau Candy Distributor.csv
└── assets/
```

## Run in VS Code

Open the project folder in VS Code.

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

### 2. Install libraries

```powershell
pip install -r requirements.txt
```

### 3. Start the dashboard

```powershell
streamlit run app.py
```

Streamlit will show a local address, normally:

```text
http://localhost:8501
```

Open that address in your browser.

## Important data-quality finding

The supplied CSV contains order dates before shipment dates by a very large amount. The application calculates:

```text
Shipping Lead Time = Ship Date - Order Date
```

and intentionally does not modify the original dates.

This is surfaced in the Data Quality page because it materially affects every lead-time KPI.

## Methodology

1. Load and validate data
2. Parse order and ship dates
3. Map products to factories
4. Add factory coordinates
5. Calculate lead time
6. Define Factory → State and Factory → Region routes
7. Aggregate shipment volume and lead-time statistics
8. Calculate delay frequency
9. Normalize route efficiency score
10. Identify efficient routes and bottlenecks
11. Compare ship modes
12. Provide drill-down analytics

## Route efficiency score

For the current filtered view:

```text
Efficiency Score =
100 × (Maximum route average lead time − route average lead time)
      / (Maximum route average lead time − Minimum route average lead time)
```

Higher score means faster average route performance within the selected view.

## Suggested research-paper sections

- Abstract
- Introduction
- Problem Statement
- Dataset Description
- Data Cleaning
- Feature Engineering
- Route Definition
- Exploratory Data Analysis
- Route Efficiency Benchmarking
- Geographic Bottleneck Analysis
- Ship Mode Analysis
- Dashboard Architecture
- Results and Insights
- Recommendations
- Limitations / Data Quality
- Conclusion
