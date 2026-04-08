README – Synthetic Used Car Financial Assets Dataset & Dashboard

1. Overview
This project generates and analyzes a synthetic dataset representing used car financial assets.
The dataset is designed to simulate real-world automotive finance scenarios and supports:
- Exploratory Data Analysis (EDA)
- Visualization (Plotly)
- Dashboard development (Streamlit)

2. Python Version
Recommended:
Python 3.10 – 3.12

3. Required Libraries
Install before running:

pip install pandas numpy plotly matplotlib seaborn streamlit

4. Dataset Structure
The dataset is split into 3 parts for GitHub upload compatibility:

- used_car_financial_assets_800k_part1.csv
- used_car_financial_assets_800k_part2.csv
- used_car_financial_assets_800k_part3.csv

5. Combine Dataset Files
To recreate the full dataset:

python combine_files.py

This will generate:
used_car_financial_assets_800k.csv

6. Running the Notebook
- Open the Jupyter notebook
- Run all cells in order
- The dataset will be generated or combined

7. Running the Dashboard
Run locally:

streamlit run app_used_car_dashboard.py

Then open:
http://localhost:8501

8. Key Features
- 800K synthetic records
- Depreciation modeling
- Exposure analysis
- Negative equity insights
- Interactive dashboard with filters and drill-down

9. Notes
- Dataset is fully synthetic (no PII)
- Designed for portfolio and interview readiness
- Supports scalable and chunked processing

10. Author
Portia Daniels-Blaylock
