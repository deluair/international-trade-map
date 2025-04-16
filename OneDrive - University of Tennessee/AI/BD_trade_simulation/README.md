# Bangladesh Trade Dynamics Simulation and Analysis

This project analyzes historical Bangladesh trade data and simulates future trade dynamics under different scenarios (Baseline, Optimistic, Pessimistic) for the period 2024-2030.

## Overview

The project provides tools to:
- Analyze historical Bangladesh trade data (exports, imports, top products, partners).
- Simulate future trade projections based on structural transformation models.
- Compare different future scenarios (baseline, optimistic, pessimistic).
- Generate HTML reports summarizing the analysis and projections.

## Installation

1.  **Clone the repository:**
    ```bash
    # Replace with the actual repository URL
    git clone https://github.com/deluair/BD_trade_simulation.git 
    cd BD_trade_simulation
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Project Structure

```
BD_trade_simulation/
|-- config/                   # (Potentially unused) Configuration files
|-- data/
|   |-- bd_trade_data.csv     # Main trade dataset (Value in $1000 USD, Quantity in Tons)
|   |-- country_codes_V*.csv  # Country code mapping
|   |-- product_codes_HS*.csv # Product code mapping
|   |-- data_handler.py       # Data loading utility
|   `-- sector_mapper.py      # (Potentially used by models)
|-- models/                   # Simulation sub-models (e.g., structural_transformation)
|-- reports/                  # Output directory for HTML/PDF reports
|-- results/                  # Output directory for JSON simulation results
|-- scenarios/
|   |-- baseline.json         # Parameters for the baseline scenario
|   |-- optimistic.json       # Parameters for the optimistic scenario
|   `-- pessimistic.json      # Parameters for the pessimistic scenario
|-- simulation/               # (Potentially unused) Simulation engine code
|-- visualization/
|   `-- plot_utils.py         # Plotting utilities (used by reports)
|-- utils/                    # (Potentially unused) Utility functions
|-- analysis/                 # (Potentially unused) Analysis tools
|-- run_real_data_report.py   # Script to generate report from historical data
|-- run_future_projection.py  # Script to run future scenario projections
|-- generate_comparison_report.py # Script to compare scenario results (PDF output)
|-- combine_reports.py        # Script to generate a combined HTML report (Real + Scenarios)
|-- bd_trade_report.py        # Core logic for real data processing and reporting
|-- generate_html_report.py   # Utility for generating HTML reports from results
|-- requirements.txt          # Project dependencies
`-- README.md                 # This file
```

## Usage

Ensure your virtual environment is activated before running scripts.

1.  **Generate Report from Real Historical Data:**
    This loads `data/bd_trade_data.csv`, processes it, and generates an HTML report (`reports/bd_trade_simulation_real_data_report.html`) with analysis of historical trends, top products, and partners.
    ```bash
    python run_real_data_report.py
    ```

2.  **Run Future Scenario Projections (2024-2030):**
    This script runs the simulation for a specific scenario, projecting from 2024 to 2030 based on 2023 data and scenario parameters. It saves detailed results to a JSON file in the `results/` directory.
    ```bash
    # Run baseline scenario
    python run_future_projection.py --scenario baseline
    
    # Run optimistic scenario
    python run_future_projection.py --scenario optimistic

    # Run pessimistic scenario
    python run_future_projection.py --scenario pessimistic
    ```
    *Note: This script also currently triggers the generation of `reports/bd_trade_simulation_real_data_report.html` at the end, which might be redundant if you ran step 1 separately.* 

3.  **Generate Scenario Comparison Report (PDF):**
    After running the projections for different scenarios (step 2), this script finds the latest result files for baseline, optimistic, and pessimistic scenarios and generates a PDF report (`reports/scenario_comparison_report_*.pdf`) comparing key metrics.
    ```bash
    python generate_comparison_report.py 
    ```

4.  **Generate Combined HTML Report (Real Data + Scenarios):**
    This script combines the real data analysis and the comparison of the latest scenario projections into a single, comprehensive HTML report (`reports/combined_trade_report_*.html`). Ensure you have run steps 1 and 2 first.
    ```bash
    python combine_reports.py
    ```

## Scenarios

The following scenarios are defined in the `scenarios/` directory:

-   **`baseline.json`**: Assumes moderate growth based on recent trends, with gradual diversification and capability improvements. Includes a moderate growth decay factor.
-   **`optimistic.json`**: Assumes stronger growth in key emerging sectors (IT, Pharma, Light Engineering), faster diversification, and higher capability gains. Includes a slower growth decay factor.
-   **`pessimistic.json`**: Assumes slower overall growth, less effective diversification, and slower capability improvements. Includes a faster growth decay factor.

You can modify the parameters within these JSON files (e.g., `it_services_growth`, `capability_index`, `growth_decay_rate`) to customize the simulations.

## Data

-   The primary input data is expected in `data/bd_trade_data.csv`.
-   **Units:** The raw data uses **Thousands of US Dollars** for value ('v') and **Metric Tons** for quantity ('q'). Reports convert values to Billions USD where appropriate.
-   Country and Product codes are mapped using the corresponding CSV files in the `data/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
