import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import re

# Page configuration
st.set_page_config(
    page_title="Data-to-UI Magic",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #1f77b4;
    font-size: 3rem;
    margin-bottom: 0.5rem;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

.metric-container {
    background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #1f77b4;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.success-banner {
    background-color: #d4edda;
    color: #155724;
    padding: 0.75rem;
    border-radius: 5px;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Sample data for demo
SAMPLE_DATA = {
    "Sales Data": pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=50, freq='D'),
        'product': np.random.choice(['Widget A', 'Widget B', 'Widget C', 'Widget D'], 50),
        'sales': np.random.randint(800, 2000, 50),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 50),
        'price': np.random.uniform(10.0, 50.0, 50).round(2),
        'discount': np.random.uniform(0.0, 0.3, 50).round(2)
    }),
    "Customer Data": pd.DataFrame({
        'customer_id': range(1, 101),
        'name': [f'Customer {i}' for i in range(1, 101)],
        'age': np.random.randint(18, 80, 100),
        'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], 100),
        'annual_revenue': np.random.randint(20000, 150000, 100),
        'satisfaction_score': np.random.randint(1, 11, 100),
        'is_premium': np.random.choice([True, False], 100)
    }),
    "Survey Results": pd.DataFrame({
        'response_id': range(1, 201),
        'category': np.random.choice(['Technology', 'Marketing', 'Sales', 'Support', 'Management'], 200),
        'rating': np.random.randint(1, 6, 200),
        'feedback_length': np.random.randint(10, 500, 200),
        'department': np.random.choice(['Engineering', 'Marketing', 'Sales', 'HR', 'Finance'], 200),
        'experience_years': np.random.randint(0, 20, 200)
    })
}

# JSON and Text sample data (as raw strings to demonstrate processing)
SAMPLE_RAW_DATA = {
    "JSON API Response": """{
  "users": [
    {"id": 1, "name": "Alice Johnson", "email": "alice@company.com", "posts": 23, "followers": 1200, "verified": true},
    {"id": 2, "name": "Bob Smith", "email": "bob@company.com", "posts": 15, "followers": 890, "verified": false},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@company.com", "posts": 31, "followers": 2150, "verified": true},
    {"id": 4, "name": "Diana Prince", "email": "diana@company.com", "posts": 8, "followers": 567, "verified": false},
    {"id": 5, "name": "Edward Wilson", "email": "edward@company.com", "posts": 42, "followers": 3200, "verified": true}
  ],
  "metadata": {
    "total_users": 5,
    "active_users": 4,
    "last_updated": "2024-09-29T10:30:00Z",
    "api_version": "v2.1"
  }
}""",

    "Contact Information": """Team Contact Directory:

Alice Johnson - alice.johnson@company.com - (555) 123-4567 - Project Manager
Bob Smith - bob.smith@company.com - (555) 234-5678 - Senior Developer
Charlie Brown - charlie.brown@company.com - (555) 345-6789 - UX Designer
Diana Prince - diana.prince@company.com - (555) 456-7890 - Data Scientist
Edward Wilson - edward.wilson@company.com - (555) 567-8901 - DevOps Engineer

Meeting Schedule:
- Weekly standup: 2024-10-01 at 9:00 AM
- Sprint planning: 2024-10-03 at 2:00 PM
- Retrospective: 2024-10-15 at 3:30 PM

Budget Information:
Q1 2024 Budget: $75,000
Q2 2024 Budget: $82,000
Q3 2024 Budget: $78,500
Q4 2024 Budget: $90,000

Key Metrics:
- Team productivity increased by 25%
- Customer satisfaction: 4.2/5.0
- Code coverage: 87%
- Response time: <200ms"""
}

def detect_data_type(text):
    """Detect if input is CSV, JSON, or unstructured text"""
    if not text:
        return 'text'

    text = text.strip()

    if not text:
        return 'text'

    if text.startswith('{') or text.startswith('['):
        return 'json'
    elif ',' in text and '\n' in text:
        lines = text.split('\n')
        if len(lines) > 1 and len(lines[0].split(',')) > 1:
            return 'csv'
    elif '\t' in text and '\n' in text:
        return 'tsv'

    # Default to text for any unstructured data
    return 'text'

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
    phones = re.findall(r'\b(?:\(\d{3}\)|\d{3})[-.\\s]?\d{3}[-.\\s]?\d{4}\b', text)

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
    """Create an impressive data profile dashboard"""
    st.markdown("### 📊 Data Profile")

    # Calculate metrics
    total_rows = len(df)
    total_cols = len(df.columns)
    data_types = df.dtypes.nunique()
    missing_values = df.isnull().sum().sum()
    memory_kb = df.memory_usage(deep=True).sum() / 1024

    # Create four metric columns
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            label="📋 Total Rows",
            value=f"{total_rows:,}",
            delta="Loaded successfully",
            delta_color="normal"
        )

    with metric_col2:
        st.metric(
            label="📊 Columns",
            value=total_cols,
            delta=f"{data_types} data types",
            delta_color="normal"
        )

    with metric_col3:
        missing_pct = (missing_values / df.size) * 100
        st.metric(
            label="🔍 Missing Values",
            value=missing_values,
            delta=f"{missing_pct:.1f}% of data" if missing_values > 0 else "Complete dataset",
            delta_color="inverse" if missing_values > 0 else "normal"
        )

    with metric_col4:
        st.metric(
            label="💾 Memory Usage",
            value=f"{memory_kb:.1f} KB",
            delta="In memory",
            delta_color="normal"
        )

    st.markdown("---")

def generate_automatic_charts(df):
    """Generate professional automatic visualizations"""
    st.markdown("### 📈 Automatic Visualizations")

    # Identify column types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Create chart layout
    chart_col1, chart_col2 = st.columns(2)

    charts_created = 0

    # Histogram for first numeric column
    if len(numeric_cols) > 0:
        with chart_col1:
            col = numeric_cols[0]
            fig = px.histogram(
                df,
                x=col,
                title=f"📊 Distribution of {col}",
                color_discrete_sequence=["#1f77b4"],
                nbins=min(30, df[col].nunique())
            )

            fig.update_layout(
                height=400,
                title_x=0.5,
                title_font_size=16,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )

            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

            st.plotly_chart(fig, use_container_width=True)
            charts_created += 1

    # Bar chart for first categorical column (if reasonable number of categories)
    if len(categorical_cols) > 0:
        col = categorical_cols[0]
        unique_count = df[col].nunique()

        if unique_count <= 15:  # Only show if manageable number of categories
            with chart_col2:
                value_counts = df[col].value_counts().head(10)

                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"📊 Top Values in {col}",
                    color_discrete_sequence=["#ff7f0e"],
                    labels={'x': col, 'y': 'Count'}
                )

                fig.update_layout(
                    height=400,
                    title_x=0.5,
                    title_font_size=16,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )

                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

                st.plotly_chart(fig, use_container_width=True)
                charts_created += 1

    # Show correlation heatmap if multiple numeric columns
    if len(numeric_cols) > 1 and charts_created < 2:
        target_col = chart_col1 if charts_created == 1 else chart_col2

        with target_col:
            corr_matrix = df[numeric_cols].corr()

            fig = px.imshow(
                corr_matrix,
                title="🔗 Correlation Heatmap",
                color_continuous_scale="RdBu_r",
                aspect="auto"
            )

            fig.update_layout(
                height=400,
                title_x=0.5,
                title_font_size=16
            )

            st.plotly_chart(fig, use_container_width=True)

    # Show message if no charts could be generated
    if charts_created == 0:
        st.info("🔍 No suitable columns found for automatic visualization. Upload data with numeric or categorical columns for charts.")

    st.markdown("---")

def create_interactive_explorer(df):
    """Create an advanced interactive data explorer"""
    st.markdown("### 🔍 Interactive Data Explorer")

    # Expandable filter controls
    with st.expander("🎛️ Filters & Controls", expanded=False):
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        # Column selection for filtering
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        selected_filters = {}

        with filter_col1:
            if categorical_cols:
                filter_col = st.selectbox(
                    "🏷️ Filter by column:",
                    ["None"] + categorical_cols,
                    help="Choose a categorical column to filter by"
                )

                if filter_col != "None":
                    unique_values = sorted(df[filter_col].unique())
                    selected_values = st.multiselect(
                        f"Select {filter_col} values:",
                        unique_values,
                        default=unique_values[:min(5, len(unique_values))],
                        help=f"Choose which {filter_col} values to display"
                    )
                    if selected_values:
                        selected_filters[filter_col] = selected_values

        with filter_col2:
            if numeric_cols:
                numeric_filter_col = st.selectbox(
                    "📊 Numeric range filter:",
                    ["None"] + numeric_cols,
                    help="Choose a numeric column for range filtering"
                )

                if numeric_filter_col != "None":
                    min_val = float(df[numeric_filter_col].min())
                    max_val = float(df[numeric_filter_col].max())

                    if min_val != max_val:
                        range_values = st.slider(
                            f"{numeric_filter_col} range:",
                            min_val, max_val, (min_val, max_val),
                            help=f"Filter {numeric_filter_col} values"
                        )
                        selected_filters[numeric_filter_col] = range_values

        with filter_col3:
            # Display options
            max_rows = max(10, len(df))  # Ensure max is at least 10
            default_rows = min(100, len(df))
            rows_to_show = st.slider(
                "📋 Rows to display:",
                min_value=min(10, len(df)),
                max_value=min(1000, max_rows),
                value=default_rows,
                step=min(10, max(1, len(df) // 10)),
                help="Number of rows to show in the table"
            )

            sort_column = st.selectbox(
                "🔤 Sort by column:",
                ["None"] + df.columns.tolist(),
                help="Choose column to sort the data by"
            )

    # Apply filters
    filtered_df = df.copy()

    for col, values in selected_filters.items():
        if col in categorical_cols:
            filtered_df = filtered_df[filtered_df[col].isin(values)]
        elif col in numeric_cols:
            min_val, max_val = values
            filtered_df = filtered_df[
                (filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)
            ]

    # Apply sorting
    if sort_column != "None":
        filtered_df = filtered_df.sort_values(sort_column)

    # Show filtering results
    if len(filtered_df) != len(df):
        st.info(f"📋 Showing {len(filtered_df):,} of {len(df):,} rows after filtering")

    # Configure column display
    column_config = {}
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['price', 'cost', 'revenue', 'sales', 'amount']):
            column_config[col] = st.column_config.NumberColumn(
                format="$%.2f",
                help=f"Currency values for {col}"
            )
        elif 'date' in col_lower:
            column_config[col] = st.column_config.DatetimeColumn(
                format="YYYY-MM-DD",
                help=f"Date values for {col}"
            )
        elif df[col].dtype == 'bool':
            column_config[col] = st.column_config.CheckboxColumn(
                help=f"Boolean values for {col}"
            )

    # Display the data table
    st.dataframe(
        filtered_df.head(rows_to_show),
        use_container_width=True,
        height=400,
        column_config=column_config,
        hide_index=True
    )

    st.markdown("---")

def create_statistics_panel(df):
    """Create a comprehensive statistics panel"""
    with st.expander("📊 Detailed Statistics", expanded=False):
        stats_tab1, stats_tab2, stats_tab3 = st.tabs(["📈 Numeric", "🏷️ Categorical", "🔍 Overview"])

        with stats_tab1:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.markdown("**Numeric Columns Analysis:**")
                numeric_stats = df[numeric_cols].describe().round(2)
                st.dataframe(numeric_stats, use_container_width=True)

                # Additional insights
                st.markdown("**Key Insights:**")
                for col in numeric_cols[:3]:  # Limit to first 3 columns
                    col_data = df[col].dropna()
                    if len(col_data) > 0:
                        st.write(f"• **{col}**: Range {col_data.min():.2f} to {col_data.max():.2f}, "
                               f"Average {col_data.mean():.2f}")
            else:
                st.info("No numeric columns found in the dataset.")

        with stats_tab2:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                st.markdown("**Categorical Columns Analysis:**")
                cat_summary = pd.DataFrame({
                    'Column': categorical_cols,
                    'Unique Values': [df[col].nunique() for col in categorical_cols],
                    'Most Common': [df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'N/A'
                                  for col in categorical_cols],
                    'Most Common Count': [df[col].value_counts().iloc[0] if len(df[col]) > 0 else 0
                                        for col in categorical_cols],
                    'Missing Count': [df[col].isnull().sum() for col in categorical_cols]
                })
                st.dataframe(cat_summary, use_container_width=True)
            else:
                st.info("No categorical columns found in the dataset.")

        with stats_tab3:
            st.markdown("**Dataset Overview:**")
            overview_col1, overview_col2 = st.columns(2)

            with overview_col1:
                st.markdown(f"""
                **Basic Information:**
                - Total Rows: {len(df):,}
                - Total Columns: {len(df.columns)}
                - Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB
                - Data Types: {df.dtypes.nunique()} different types
                """)

            with overview_col2:
                st.markdown(f"""
                **Data Quality:**
                - Complete Rows: {len(df.dropna()):,} ({len(df.dropna())/len(df)*100:.1f}%)
                - Missing Values: {df.isnull().sum().sum():,}
                - Duplicate Rows: {df.duplicated().sum():,}
                - Unique Rows: {len(df.drop_duplicates()):,}
                """)

def handle_file_processing(uploaded_file):
    """Handle file processing with comprehensive error handling"""
    try:
        # Show processing state
        with st.spinner("🔄 Processing your data..."):
            # Read file content
            file_content = uploaded_file.getvalue().decode('utf-8')

            # Detect data type
            data_type = detect_data_type(file_content)

            # Show data type detection
            type_color = {"csv": "🟢", "json": "🔵", "tsv": "🟡", "text": "🟠"}
            st.info(f"{type_color.get(data_type, '⚪')} Detected data type: **{data_type.upper() if data_type else 'UNKNOWN'}**")

            # Process based on detected type
            df = None
            if data_type in ['csv', 'tsv']:
                # Try different separators for CSV
                for sep in [',', ';', '\t', '|']:
                    try:
                        from io import StringIO
                        df = pd.read_csv(StringIO(file_content), sep=sep)
                        if len(df.columns) > 1:  # Valid separation found
                            break
                    except:
                        continue

                if df is None:
                    df = pd.read_csv(StringIO(file_content))  # Fallback

            elif data_type == 'json':
                df = process_json_data(file_content)
            elif data_type == 'text':
                df = extract_entities_from_text(file_content)

            # Validate the data
            if df is None or df.empty:
                st.warning("⚠️ The uploaded file appears to be empty or could not be processed")
                st.markdown("Please try uploading a different file or use our sample data.")
                return None

            if len(df.columns) < 2 and data_type in ['csv', 'tsv']:
                st.warning("⚠️ The file has only one column. Please ensure your file has multiple columns for better insights.")

            # File size warning
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 10:
                st.warning(f"⚠️ Large file detected ({file_size_mb:.1f} MB). Processing may be slower.")

            return df

    except UnicodeDecodeError:
        st.error("❌ Error: Unable to read file encoding")
        st.info("💡 Please ensure your file is saved in UTF-8 encoding")
        return None

    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.info("💡 Please try a different file or contact support if the issue persists")
        return None

def show_success_message(filename):
    """Show a prominent success message"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <h4 style="margin: 0; color: #155724;">✅ Success!</h4>
        <p style="margin: 0.5rem 0 0 0;">Successfully loaded <strong>{filename}</strong></p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Main header
    st.markdown('<h1 class="main-header">🪄 Data-to-UI Magic</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle"><strong>Transform CSV, JSON, and unstructured text files into insights!</strong></p>', unsafe_allow_html=True)

    # Technology thumbnails
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <div style="background: #FF3621; color: white; padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold;">
                Databricks
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <div style="background: linear-gradient(135deg, #CC9B7A 0%, #D4A484 100%); color: white; padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold;">
                Claude Code
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <div style="background: linear-gradient(135deg, #0066FF 0%, #00BFFF 100%); color: white; padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold;">
                Cursor
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Initialize session state for data persistence
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'selected_sample' not in st.session_state:
        st.session_state.selected_sample = "None"
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    # Create three-column layout for upload, samples, and refresh
    upload_col1, upload_col2, upload_col3 = st.columns([3, 1, 0.5])

    with upload_col1:
        st.markdown("### 📁 Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV, JSON, or Text file",
            type=["csv", "json", "txt"],
            help="Drag and drop your CSV, JSON, or text file here, or click to browse",
            label_visibility="collapsed",
            key=f"uploader_{st.session_state.uploader_key}"
        )

        if uploaded_file:
            st.markdown(f'<div class="success-banner">✅ Successfully loaded: <strong>{uploaded_file.name}</strong></div>',
                       unsafe_allow_html=True)

    with upload_col2:
        st.markdown("### 🎯 Try Sample Data")
        sample_options = {
            "None": None,
            "Sales Data": "Sales Data",
            "Customer Data": "Customer Data",
            "Survey Results": "Survey Results",
            "JSON API Response": "JSON API Response",
            "Contact Information": "Contact Information"
        }

        selected_sample = st.selectbox(
            "Choose sample:",
            list(sample_options.keys()),
            help="Pre-loaded datasets to explore features",
            key="sample_selector",
            index=list(sample_options.keys()).index(st.session_state.selected_sample)
        )

        # Update session state with selected sample
        st.session_state.selected_sample = selected_sample

        if selected_sample != "None":
            st.info(f"📊 Loading {selected_sample}...")

    with upload_col3:
        st.markdown("### 🔄")
        if st.button("Reset", help="Clear all data and reset the app", use_container_width=True):
            # Clear all session state completely
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Reinitialize required session state
            st.session_state.df = None
            st.session_state.selected_sample = "None"
            st.session_state.uploader_key = st.session_state.get('uploader_key', 0) + 1
            # Force a rerun to reset everything
            st.rerun()

    # Process uploaded file or sample data
    if uploaded_file is not None:
        df = handle_file_processing(uploaded_file)
        if df is not None:
            st.session_state.df = df
            show_success_message(uploaded_file.name)
    elif selected_sample != "None":
        # Load sample data
        if selected_sample in SAMPLE_DATA:
            # CSV-like structured data (already DataFrames)
            df = SAMPLE_DATA[selected_sample]
            st.session_state.df = df
            show_success_message(f"{selected_sample} (Sample)")
        elif selected_sample in SAMPLE_RAW_DATA:
            # JSON or text data that needs processing
            raw_data = SAMPLE_RAW_DATA[selected_sample]
            data_type = detect_data_type(raw_data)

            # Show data type detection
            type_color = {"csv": "🟢", "json": "🔵", "tsv": "🟡", "text": "🟠"}
            st.info(f"{type_color.get(data_type, '⚪')} Detected data type: **{data_type.upper() if data_type else 'UNKNOWN'}**")

            # Process data based on type
            df = None
            if data_type == 'json':
                df = process_json_data(raw_data)
            elif data_type == 'text':
                df = extract_entities_from_text(raw_data)

            if df is not None and not df.empty:
                st.session_state.df = df
                show_success_message(f"{selected_sample} (Sample)")
            else:
                st.error("Could not process the sample data")

    # Display results if data is available
    if st.session_state.df is not None:
        df = st.session_state.df

        # Create all UI components
        create_data_profile(df)
        generate_automatic_charts(df)
        create_interactive_explorer(df)
        create_statistics_panel(df)

        # Footer with additional actions
        st.markdown("---")
        st.markdown("### 💾 Export Options")

        export_col1, export_col2, export_col3 = st.columns(3)

        with export_col1:
            csv_data = df.to_csv(index=False)
            st.download_button(
                "📄 Download as CSV",
                csv_data,
                f"processed_data.csv",
                "text/csv",
                help="Download the processed data as CSV"
            )

        with export_col2:
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                "📋 Download as JSON",
                json_data,
                f"processed_data.json",
                "application/json",
                help="Download the processed data as JSON"
            )

        with export_col3:
            summary = f"""Data Summary:

Rows: {len(df):,}
Columns: {len(df.columns)}
Data Types: {df.dtypes.value_counts().to_dict()}
Missing Values: {df.isnull().sum().sum()}
Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB

Generated by Data-to-UI Magic
"""
            st.download_button(
                "📝 Download Summary",
                summary,
                f"data_summary.txt",
                "text/plain",
                help="Download a text summary of the data"
            )
    else:
        # Welcome screen when no data is loaded
        st.markdown("""
        ### 🚀 Welcome to Data-to-UI Magic!

        This app transforms your CSV files into beautiful, interactive dashboards in seconds.

        **How it works:**
        1. **📁 Upload** your CSV file using the uploader above
        2. **⚡ Watch** as we instantly analyze and visualize your data
        3. **🔍 Explore** with interactive charts, filters, and statistics
        4. **💾 Export** your insights in multiple formats

        **Perfect for:**
        - 📊 Quick data exploration and analysis
        - 📈 Creating instant visualizations for presentations
        - 🔍 Understanding data patterns and relationships
        - 💼 Business intelligence and reporting

        **Try it now** → Use the sample data selector above to see it in action!
        """)

if __name__ == "__main__":
    main()
