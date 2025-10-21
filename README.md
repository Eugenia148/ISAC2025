# ISAC 2025 - Liga MX Analysis Project

This project analyzes Liga MX football data using StatsBomb's API for the ISAC 2025 competition.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- StatsBomb API credentials (optional, for premium data access)

### Installation
1. Clone this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Required Libraries
The project uses the following Python libraries:
- `statsbombpy` - StatsBomb API client
- `python-dotenv` - Environment variable management
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `matplotlib` - Data visualization
- `seaborn` - Statistical data visualization
- `scikit-learn` - Machine learning tools
- `pyarrow` - Fast columnar data storage (for Parquet files)

### Usage
1. Set up your `.env` file with StatsBomb credentials (optional):
   ```
   SB_USERNAME=your_username
   SB_PASSWORD=your_password
   ```

2. Run the data loading notebook:
   ```bash
   jupyter notebook src/pull_data.ipynb
   ```

3. For offline analysis, use the data analyzer:
   ```bash
   python src/data_analyzer.py
   ```

## 📁 ESTRUCTURA DE LOS ARCHIVOS

1. src/:

1.1 get_data.py

It will be responsible for connecting to the API, downloading the data, and saving them in the data/ folder.
