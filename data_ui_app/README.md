# 🪄 Data-to-UI Magic

Transform CSV, JSON, and text files into beautiful, interactive dashboards instantly.

## Overview

Data-to-UI Magic is a Streamlit-powered application that automatically analyzes, visualizes, and provides insights from your data files. Simply upload your data and watch as the app creates professional dashboards with charts, statistics, and interactive exploration tools.

## Features

### 📊 Automatic Data Profiling
- Total rows and columns analysis
- Data type detection
- Missing value identification
- Memory usage tracking

### 📈 Smart Visualizations
- Automatic histogram generation for numeric data
- Bar charts for categorical data
- Correlation heatmaps
- Professional styling with Plotly

### 🔍 Interactive Data Explorer
- Multi-column filtering
- Numeric range sliders
- Sorting and pagination
- Smart column formatting (currency, dates, booleans)

### 📋 Comprehensive Statistics
- Numeric column analysis (min, max, mean, std)
- Categorical column insights
- Data quality metrics
- Duplicate and missing value detection

### 💾 Export Options
- Download processed data as CSV
- Export as JSON
- Generate text summaries

### 🎯 Sample Data
Pre-loaded sample datasets including:
- Sales Data
- Customer Data
- Survey Results
- JSON API Response
- Contact Information
- Product Reviews

## Installation

1. Clone the repository:
```bash
cd /Users/jules/git-repos/databricks-apps/data_ui_app
```

2. Install required dependencies:
```bash
uv pip install streamlit pandas plotly numpy
```

## Usage

Run the Streamlit app:
```bash
uv run streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Supported File Formats

- **CSV** - Comma-separated values (auto-detects separators: `,`, `;`, `\t`, `|`)
- **JSON** - Automatically processes arrays and nested objects
- **TXT** - Extracts structured entities (emails, phone numbers, dates, currency, names)

## Data Processing Capabilities

### Structured Data (CSV/JSON)
- Automatic separator detection
- Nested JSON flattening
- Data type inference

### Unstructured Text
Uses regex pattern matching to extract:
- Email addresses
- Phone numbers
- Dates
- Currency amounts
- Names
- Word frequency analysis

## How It Works

1. **Upload**: Drag and drop or select a file
2. **Detect**: Automatically identifies data type and structure
3. **Process**: Parses and cleans the data
4. **Analyze**: Generates statistics and profiles
5. **Visualize**: Creates automatic charts and graphs
6. **Explore**: Provides interactive filtering and sorting
7. **Export**: Download results in multiple formats

## Technical Details

- **Framework**: Streamlit
- **Visualization**: Plotly Express
- **Data Processing**: Pandas, NumPy
- **Pattern Matching**: Python regex (re module)

## File Structure

```
data_ui_app/
├── app.py                  # Main Streamlit application
├── README.md               # This file
└── CLAUDE.md              # AI assistant context file
```

## Requirements

```
streamlit
pandas
plotly
numpy
```

## Use Cases

- Quick data exploration and analysis
- Creating instant visualizations for presentations
- Understanding data patterns and relationships
- Business intelligence and reporting
- Data quality assessment
- Educational demonstrations

## License

This project is open source and available for educational and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
