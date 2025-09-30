# CLAUDE.md - AI Assistant Context

This file provides context for AI assistants (like Claude) working on this project.

## Project Purpose

**Data-to-UI Magic** is a demonstration Streamlit application that automatically transforms uploaded data files (CSV, JSON, text) into interactive dashboards with visualizations, statistics, and data exploration tools.

The goal is to showcase rapid data-to-insight conversion without requiring users to write code or configure complex tools.

## High-Level Architecture

### System Overview

Data-to-UI Magic is built on **Streamlit** with a component-based architecture that processes data through distinct stages:

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ File Upload  │  │ Sample Data  │  │ Reset Button │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Data Processing Layer                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Data Type Detection (detect_data_type)                   │   │
│  │  - CSV/TSV: Separator detection, column parsing          │   │
│  │  - JSON: Nested structure flattening                     │   │
│  │  - Text: Entity extraction (emails, phones, dates)       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Session State Management                      │
│         st.session_state.df (pandas DataFrame)                   │
│         st.session_state.selected_sample                         │
│         st.session_state.uploader_key                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Visualization Layer                           │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Data Profile   │  │ Auto Charts    │  │ Statistics Panel │  │
│  │ - Row count    │  │ - Histograms   │  │ - Describe()     │  │
│  │ - Columns      │  │ - Bar charts   │  │ - Categorical    │  │
│  │ - Data types   │  │ - Heatmaps     │  │ - Quality metrics│  │
│  │ - Missing vals │  │ - Plotly       │  │                  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Interactive Data Explorer                                 │  │
│  │ - Column filtering (categorical & numeric ranges)         │  │
│  │ - Multi-column sorting                                    │  │
│  │ - Pagination (configurable rows per page)                │  │
│  │ - Smart formatting (currency, dates, booleans)           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Export Layer                               │
│    CSV Download  │  JSON Export  │  Text Summary                │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Data Detection & Processing** (`detect_data_type`, `process_json_data`, `extract_entities_from_text`, `handle_file_processing`)
   - Automatically identifies file format (CSV, JSON, TSV, unstructured text)
   - Intelligent separator detection for CSV files (`,`, `;`, `\t`, `|`)
   - Processes structured data into pandas DataFrames
   - Extracts entities from unstructured text using regex patterns
   - Comprehensive error handling with user-friendly messages

2. **Data Profiling** (`create_data_profile`)
   - Calculates key metrics: rows, columns, data types, missing values, memory usage
   - Displays metrics in a dashboard-style layout with visual cards
   - Real-time computation on data load

3. **Automatic Visualizations** (`generate_automatic_charts`)
   - Creates histograms for numeric columns (distribution analysis)
   - Generates bar charts for categorical columns (with cardinality limits)
   - Produces correlation heatmaps for multiple numeric columns
   - Uses Plotly for interactive, responsive charts
   - Automatic chart selection based on data types

4. **Interactive Explorer** (`create_interactive_explorer`)
   - Dynamic filtering by categorical columns (multi-select)
   - Numeric range filtering with sliders
   - Multi-column sorting capabilities
   - Configurable pagination (100/500/1000 rows)
   - Smart column formatting (currency, dates, booleans)
   - Real-time data updates as filters change

5. **Statistics Panel** (`create_statistics_panel`)
   - Detailed numeric statistics (min, max, mean, std, quartiles)
   - Categorical analysis (unique values, mode, value counts)
   - Data quality overview (completeness %, duplicates)
   - Organized in expandable sections

6. **Export Functionality**
   - CSV download (preserves current data state)
   - JSON export (structured format)
   - Text summary generation
   - One-click download buttons

7. **Reset Functionality**
   - Clears all session state
   - Resets file uploader (using dynamic key)
   - Resets sample selector to "None"
   - Returns app to initial state

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User Action: Upload File OR Select Sample Data             │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ File Processing: Read → Detect Type → Parse                │
│ - CSV/TSV: Auto-detect separator, create DataFrame         │
│ - JSON: Parse and flatten nested structures                │
│ - Text: Extract entities using regex patterns              │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Session State Storage: st.session_state.df = DataFrame     │
│ Persists across Streamlit reruns                           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Conditional Rendering (if st.session_state.df is not None) │
│                                                             │
│  1. create_data_profile(df)        → Metrics cards         │
│  2. generate_automatic_charts(df)  → Visual charts         │
│  3. create_interactive_explorer(df)→ Filterable table      │
│  4. create_statistics_panel(df)    → Statistical analysis  │
│  5. Export Options                 → Download buttons      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ User Actions: Filter, Sort, Export, or Reset               │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Session State Management
- Uses `st.session_state.df` to persist data across Streamlit reruns
- Allows users to switch between uploaded files and sample data

### 2. Automatic Intelligence
- No user configuration required for basic functionality
- Smart defaults for chart selection based on data types
- Automatic separator detection for CSV files

### 3. Error Handling
- Comprehensive try-catch blocks in `handle_file_processing`
- User-friendly error messages with actionable suggestions
- Graceful degradation (e.g., word frequency as fallback for text)

### 4. Performance Considerations
- Limits displayed rows to prevent UI lag (default: 100, max: 1000)
- Limits charts to avoid overwhelming the interface
- Efficient pandas operations

### 5. Visual Design
- Custom CSS for professional styling
- Consistent color scheme using Plotly defaults
- Responsive layout with Streamlit columns

## Sample Data

The app includes 6 pre-loaded sample datasets:

### Structured DataFrames
1. **Sales Data** - E-commerce sales with dates, products, regions, prices
2. **Customer Data** - Customer demographics and revenue
3. **Survey Results** - Employee survey responses

### Raw Data (requires processing)
4. **JSON API Response** - User data from a mock API
5. **Contact Information** - Text with emails, phones, dates, budgets
6. **Product Reviews** - Customer feedback with ratings

## Code Patterns to Follow

### Adding New Visualizations
```python
def create_new_chart(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        fig = px.line(df, x=col_x, y=col_y, title="Chart Title")
        fig.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)
```

### Adding New Data Processing
```python
def process_new_format(text):
    try:
        # Processing logic
        return pd.DataFrame(processed_data)
    except Exception as e:
        st.error(f"Error: {e}")
        return None
```

### Adding New Filters
```python
with st.expander("New Filter"):
    filter_value = st.selectbox("Options", options_list)
    if filter_value:
        df = df[df['column'] == filter_value]
```

## Common Tasks

### Adding a New Sample Dataset
1. Add to `SAMPLE_DATA` (for DataFrames) or `SAMPLE_RAW_DATA` (for strings)
2. Update `sample_options` dictionary in `main()`
3. Test with both upload and sample selection flows

### Enhancing Data Type Detection
1. Modify `detect_data_type()` to recognize new patterns
2. Add processing function (e.g., `process_xml_data()`)
3. Integrate into `handle_file_processing()` workflow

### Adding New Statistics
1. Create function following pattern: `def create_new_stats(df)`
2. Add to main display section after `create_statistics_panel()`
3. Use expanders for optional/detailed views

## Dependencies

The project uses `uv` for dependency management and virtual environment handling.

- **streamlit**: Web framework for data apps
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations
- **numpy**: Numerical operations
- **json**: JSON parsing (standard library)
- **re**: Regular expression pattern matching (standard library)

### Running Locally

```bash
cd /Users/jules/git-repos/databricks-apps/data_ui_app
uv run streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Testing Approach

When making changes:
1. Test with uploaded CSV, JSON, and text files
2. Test with all 6 sample datasets
3. Verify filtering, sorting, and pagination
4. Check export functionality (CSV, JSON, summary)
5. Validate error handling with malformed files
6. Test with edge cases (empty files, single column, large files)

## Future Enhancement Ideas

- Database connectivity (SQL, MongoDB)
- ML-powered insights and anomaly detection
- Custom chart builder with user-selected columns
- Data transformation pipeline (cleaning, aggregation)
- Multi-file upload and merging
- Scheduled data refreshes
- User authentication and saved dashboards
- API endpoints for programmatic access

## Performance Notes

- Large files (>10MB) trigger warning but still process
- Chart generation limited to prevent UI slowdown
- Pagination prevents rendering thousands of rows
- Use `.head()` for preview operations

## Styling Guidelines

- Use Streamlit's native components when possible
- Custom CSS in `<style>` tags for special cases
- Consistent emoji usage for visual markers
- Professional color palette (blues, grays, greens for success)
- Responsive design with column layouts

## Common Pitfalls to Avoid

1. Don't modify `st.session_state.df` without copying first
2. Always check for empty DataFrames before operations
3. Validate column existence before accessing
4. Use `use_container_width=True` for responsive charts
5. Limit regex operations on very large text files
6. Handle mixed data types in columns gracefully

## Questions to Consider When Modifying

- Does this change break existing sample data?
- Is error handling comprehensive?
- Will this work with edge cases (empty data, single column, etc.)?
- Is the UI still responsive on mobile?
- Are there performance implications for large files?
- Is the feature discoverable without instructions?

---

This context should help AI assistants understand the project structure and make informed decisions when assisting with development, debugging, or feature additions.
