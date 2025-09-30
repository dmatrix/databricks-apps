import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import re
from io import StringIO

# Configure page
st.set_page_config(
    page_title="Data-to-UI Magic",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample data for quick testing
SAMPLE_DATA = {
    "Sales Data": """date,product,sales,region
2024-01-01,Widget A,1200,North
2024-01-02,Widget B,800,South
2024-01-03,Widget A,1500,East
2024-01-04,Widget C,900,West
2024-01-05,Widget B,1100,North
2024-01-06,Widget A,1300,South""",

    "User Database": """name,email,age,department,salary
John Smith,john@company.com,28,Engineering,75000
Jane Doe,jane@company.com,32,Marketing,68000
Bob Johnson,bob@company.com,45,Sales,82000
Alice Brown,alice@company.com,29,Engineering,77000
Charlie Wilson,charlie@company.com,36,Marketing,71000""",

    "JSON API Response": """{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@test.com", "posts": 23},
    {"id": 2, "name": "Bob", "email": "bob@test.com", "posts": 15},
    {"id": 3, "name": "Charlie", "email": "charlie@test.com", "posts": 31}
  ],
  "metadata": {"total_users": 3, "active": true}
}""",

    "Contact List": """Contact our team:
John Smith - john.smith@company.com - (555) 123-4567
Jane Doe - jane.doe@company.com - (555) 234-5678
Bob Johnson - bob.johnson@company.com - (555) 345-6789
Meeting scheduled for 2024-03-15 at 2:00 PM
Budget: $50,000 for Q1 2024
Revenue target: $120,000"""
}

def detect_data_type(text):
    """Detect if input is CSV, JSON, or unstructured text"""
    text = text.strip()

    if text.startswith('{') or text.startswith('['):
        return 'json'
    elif ',' in text and '\n' in text:
        lines = text.split('\n')
        if len(lines) > 1 and len(lines[0].split(',')) > 1:
            return 'csv'
    elif '\t' in text and '\n' in text:
        return 'tsv'
    else:
        return 'text'

def process_csv_data(text):
    """Process CSV data"""
    try:
        # Try different separators
        for sep in [',', ';', '\t', '|']:
            try:
                df = pd.read_csv(StringIO(text), sep=sep)
                if len(df.columns) > 1:  # Valid separation found
                    return df
            except:
                continue

        # Fallback: treat as comma-separated
        return pd.read_csv(StringIO(text))
    except Exception as e:
        st.error(f"Error processing CSV: {e}")
        return None

def process_json_data(text):
    """Process JSON data"""
    try:
        data = json.loads(text)

        # Handle different JSON structures
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a dict with arrays, try to create DataFrame
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], dict):
                        return pd.DataFrame(value)

            # Otherwise, create a simple key-value DataFrame
            return pd.DataFrame(list(data.items()), columns=['Key', 'Value'])
        else:
            return pd.DataFrame([{'Value': data}])

    except Exception as e:
        st.error(f"Error processing JSON: {e}")
        return None

def extract_entities_from_text(text):
    """Extract structured data from unstructured text"""

    # Extract emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

    # Extract phone numbers
    phones = re.findall(r'\b(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b', text)

    # Extract dates
    dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b', text)

    # Extract money amounts
    money = re.findall(r'\$[\d,]+(?:\.\d{2})?', text)

    # Extract names (simple pattern - words that start with capital letters)
    names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)

    # Create structured data
    entities = []

    for email in emails[:10]:  # Limit to 10
        entities.append({'Type': 'Email', 'Value': email, 'Context': 'Contact Information'})

    for phone in phones[:10]:
        entities.append({'Type': 'Phone', 'Value': phone, 'Context': 'Contact Information'})

    for date in dates[:10]:
        entities.append({'Type': 'Date', 'Value': date, 'Context': 'Timeline'})

    for amount in money[:10]:
        entities.append({'Type': 'Money', 'Value': amount, 'Context': 'Financial'})

    for name in names[:10]:
        entities.append({'Type': 'Name', 'Value': name, 'Context': 'Person'})

    if entities:
        return pd.DataFrame(entities)
    else:
        # If no entities found, create word frequency table
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = pd.Series(words).value_counts().head(10)
        return pd.DataFrame({
            'Word': word_freq.index,
            'Frequency': word_freq.values,
            'Type': 'Word Analysis'
        })

def create_data_profile(df):
    """Create data profiling section"""
    if df is None or df.empty:
        return

    st.subheader("📊 Data Profile")

    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Rows", f"{len(df):,}")

    with col2:
        st.metric("Total Columns", len(df.columns))

    with col3:
        missing_values = df.isnull().sum().sum()
        st.metric("Missing Values", missing_values)

    with col4:
        memory_usage = df.memory_usage(deep=True).sum() / 1024
        st.metric("Memory Usage", f"{memory_usage:.1f} KB")

    # Data types
    with st.expander("📋 Column Information", expanded=False):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': [df[col].count() for col in df.columns],
            'Null Count': [df[col].isnull().sum() for col in df.columns],
            'Unique Values': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)

def generate_automatic_charts(df):
    """Generate charts automatically based on data types"""
    if df is None or df.empty:
        return

    st.subheader("📈 Automatic Visualizations")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    charts_created = 0
    max_charts = 6

    # Create charts in a grid
    chart_cols = st.columns(2)
    col_idx = 0

    # Histograms for numeric columns
    for col in numeric_cols[:3]:  # Max 3 numeric charts
        if charts_created >= max_charts:
            break

        with chart_cols[col_idx % 2]:
            fig = px.histogram(
                df,
                x=col,
                title=f"Distribution of {col}",
                nbins=20
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            charts_created += 1
            col_idx += 1

    # Bar charts for categorical columns
    for col in categorical_cols[:3]:  # Max 3 categorical charts
        if charts_created >= max_charts:
            break

        if df[col].nunique() <= 20:  # Only if not too many categories
            with chart_cols[col_idx % 2]:
                value_counts = df[col].value_counts().head(10)
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Top Values in {col}",
                    labels={'x': col, 'y': 'Count'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                charts_created += 1
                col_idx += 1

    # Correlation heatmap if we have multiple numeric columns
    if len(numeric_cols) > 1 and charts_created < max_charts:
        with chart_cols[col_idx % 2]:
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(
                corr_matrix,
                title="Correlation Heatmap",
                color_continuous_scale='RdBu_r',
                aspect='auto'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            charts_created += 1

    if charts_created == 0:
        st.info("No suitable columns found for automatic visualization. Try uploading data with numeric or categorical columns.")

def create_interactive_table(df):
    """Create interactive data table with filters"""
    if df is None or df.empty:
        return

    st.subheader("🔍 Interactive Data Explorer")

    # Simple filtering
    if len(df.columns) > 0:
        with st.expander("🎛️ Filters", expanded=False):
            filter_col1, filter_col2 = st.columns(2)

            with filter_col1:
                # Column selector for filtering
                columns_to_filter = st.multiselect(
                    "Select columns to filter:",
                    df.columns.tolist(),
                    default=[]
                )

            filtered_df = df.copy()

            # Apply filters
            for col in columns_to_filter:
                if df[col].dtype in ['object', 'category']:
                    unique_values = df[col].unique().tolist()
                    selected_values = st.multiselect(
                        f"Filter {col}:",
                        unique_values,
                        default=unique_values
                    )
                    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

                elif df[col].dtype in ['int64', 'float64']:
                    min_val, max_val = float(df[col].min()), float(df[col].max())
                    selected_range = st.slider(
                        f"Filter {col}:",
                        min_val, max_val, (min_val, max_val)
                    )
                    filtered_df = filtered_df[
                        (filtered_df[col] >= selected_range[0]) &
                        (filtered_df[col] <= selected_range[1])
                    ]

        # Display filtered data
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} rows after filtering")

        # Display the dataframe with some styling
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )

        # Quick stats on filtered data
        if len(filtered_df) > 0:
            numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                with st.expander("📊 Quick Statistics", expanded=False):
                    st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)

def main():
    # Header
    st.title("🪄 Data-to-UI Magic")
    st.markdown("**Transform any data into an instant interactive interface!**")
    st.markdown("---")

    # Sidebar for input options
    with st.sidebar:
        st.header("📥 Data Input")

        input_method = st.radio(
            "Choose input method:",
            ["Upload File", "Paste Data", "Use Sample Data"]
        )

        data_text = ""

        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload your file",
                type=['csv', 'json', 'txt'],
                help="Supports CSV, JSON, and text files"
            )

            if uploaded_file is not None:
                data_text = uploaded_file.getvalue().decode('utf-8')
                st.success(f"Loaded {uploaded_file.name}")

        elif input_method == "Paste Data":
            data_text = st.text_area(
                "Paste your data here:",
                height=200,
                placeholder="Paste CSV, JSON, or any text data..."
            )

        elif input_method == "Use Sample Data":
            sample_choice = st.selectbox(
                "Choose sample data:",
                [""] + list(SAMPLE_DATA.keys())
            )

            if sample_choice:
                data_text = SAMPLE_DATA[sample_choice]
                st.code(data_text[:200] + "..." if len(data_text) > 200 else data_text)

    # Main content area
    if data_text:
        # Detect data type
        data_type = detect_data_type(data_text)

        # Show data type detection
        type_color = {"csv": "🟢", "json": "🔵", "tsv": "🟡", "text": "🟠"}
        st.info(f"{type_color.get(data_type, '⚪')} Detected data type: **{data_type.upper()}**")

        # Process data based on type
        df = None

        if data_type in ['csv', 'tsv']:
            df = process_csv_data(data_text)
        elif data_type == 'json':
            df = process_json_data(data_text)
        elif data_type == 'text':
            df = extract_entities_from_text(data_text)

        if df is not None and not df.empty:
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Visualizations", "🔍 Data Explorer"])

            with tab1:
                create_data_profile(df)

                # Show first few rows
                st.subheader("👀 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)

            with tab2:
                generate_automatic_charts(df)

            with tab3:
                create_interactive_table(df)

            # Export options
            st.markdown("---")
            st.subheader("💾 Export Options")

            col1, col2, col3 = st.columns(3)

            with col1:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    "📄 Download CSV",
                    csv_data,
                    "processed_data.csv",
                    "text/csv"
                )

            with col2:
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    "📋 Download JSON",
                    json_data,
                    "processed_data.json",
                    "application/json"
                )

            with col3:
                # Simple summary
                summary = f"""
Data Summary:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Data Types: {df.dtypes.value_counts().to_dict()}
"""
                st.download_button(
                    "📝 Download Summary",
                    summary,
                    "data_summary.txt",
                    "text/plain"
                )
        else:
            st.error("Could not process the provided data. Please check the format and try again.")

    else:
        # Welcome message
        st.markdown("""
        ### 🚀 Welcome to Data-to-UI Magic!

        This app instantly transforms your raw data into interactive interfaces. Here's how:

        1. **📁 Upload** a CSV/JSON file, **📝 paste** data, or **🎯 try** sample data
        2. **🔍 Watch** as we automatically detect and process your data
        3. **📊 Explore** instant visualizations and interactive tables
        4. **💾 Export** processed data in multiple formats

        **Supported formats:**
        - 📊 CSV files (any delimiter)
        - 🔧 JSON data (arrays or objects)
        - 📝 Unstructured text (extracts entities)

        **Try it now** → Use the sidebar to get started!
        """)

        # Show sample data preview
        st.markdown("### 🎯 Sample Data Available:")
        for name, data in SAMPLE_DATA.items():
            with st.expander(f"📋 {name}"):
                st.code(data[:300] + "..." if len(data) > 300 else data)

if __name__ == "__main__":
    main()