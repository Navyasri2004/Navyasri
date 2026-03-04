import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set up the page configuration
st.set_page_config(page_title="🌈 Interactive and Colorful Data Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF6347;'>🚀 Supercharged Interactive Data Dashboard</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 📁 Upload & Options", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload your data file", type=["csv", "xlsx", "xls", "json", "txt"])
st.sidebar.info("Supported: CSV, Excel, JSON, TXT (tab-separated)")

# Toggle for Dark Mode
dark_mode = st.sidebar.radio("🌓 Theme", ["Light", "Dark"])

# Load data
df = None
if uploaded_file:
    file_name = uploaded_file.name
    file_ext = file_name.split('.')[-1].lower()
    try:
        if file_ext == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_ext in ["xlsx", "xls"]:
            df = pd.read_excel(uploaded_file)
        elif file_ext == "json":
            df = pd.read_json(uploaded_file)
        elif file_ext == "txt":
            df = pd.read_csv(uploaded_file, delimiter="\t")
        else:
            st.error("❌ Unsupported file format")
    except Exception as e:
        st.error(f"🚫 Error loading file: {e}")

# Main logic
if df is not None:
    st.success("✅ File uploaded successfully!")

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Numeric Columns", len(numeric_cols), delta_color="inverse")
    col2.metric("🔠 Categorical Columns", len(cat_cols), delta_color="inverse")
    col3.metric("📦 Total Rows", len(df), delta_color="inverse")

    # Enhanced Filters Section
    st.sidebar.markdown("### 🧰 Advanced Filters", unsafe_allow_html=True)
    filters_df = df.copy()

    # Text search filter
    if cat_cols:
        text_search_col = st.sidebar.selectbox("🔎 Search Text in Column", [None] + cat_cols)
        if text_search_col:
            text_query = st.sidebar.text_input(f"Search in '{text_search_col}'")
            if text_query:
                filters_df = filters_df[filters_df[text_search_col].astype(str).str.contains(text_query, case=False, na=False)]

    # Multi-category filters
    for cat in cat_cols[:3]:
        selected_values = st.sidebar.multiselect(f"Filter {cat}", df[cat].dropna().unique())
        if selected_values:
            filters_df = filters_df[filters_df[cat].isin(selected_values)]

    # Date filters
    date_cols = df.select_dtypes(include=['datetime64', 'datetime', 'object']).columns.tolist()
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            continue

    date_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    if date_cols:
        date_col = st.sidebar.selectbox("🗓️ Filter by Date", date_cols)
        if date_col:
            min_date = df[date_col].min()
            max_date = df[date_col].max()
            start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
            if start_date and end_date:
                filters_df = filters_df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]

    # Numeric filters
    for col in numeric_cols[:5]:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        sel_min, sel_max = st.sidebar.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
        filters_df = filters_df[(filters_df[col] >= sel_min) & (filters_df[col] <= sel_max)]

    st.markdown("### 📋 Filtered Data Preview")
    st.dataframe(filters_df.style.highlight_max(axis=0, color='lightgreen').highlight_min(axis=0, color='lightcoral'), use_container_width=True)

    # Chart Options
    st.sidebar.markdown("### 📊 Chart Options", unsafe_allow_html=True)
    chart_type = st.sidebar.selectbox("Select Visualization Type", ["Scatter", "Line", "Histogram", "Box", "Heatmap", "Pie", "Bar", "Area", "Violin", "Treemap"])
    chart_title = st.sidebar.text_input("Chart Title", value="📊 Interactive Data Chart")
    chart_size = st.sidebar.selectbox("Chart Size", ["Small", "Medium", "Large"])

    chart_width = {"Small": 400, "Medium": 700, "Large": 1000}[chart_size]
    chart_height = {"Small": 300, "Medium": 500, "Large": 700}[chart_size]

    fig = None

    if chart_type == "Scatter":
        x = st.sidebar.selectbox("X-axis", numeric_cols)
        y = st.sidebar.selectbox("Y-axis", numeric_cols)
        color = st.sidebar.selectbox("Color by", [None] + cat_cols)
        fig = px.scatter(filters_df, x=x, y=y, color=color, title=chart_title)

    elif chart_type == "Line":
        x = st.sidebar.selectbox("X-axis", numeric_cols + cat_cols)
        y = st.sidebar.selectbox("Y-axis", numeric_cols)
        color = st.sidebar.selectbox("Color by", [None] + cat_cols)
        fig = px.line(filters_df, x=x, y=y, color=color, title=chart_title)

    elif chart_type == "Histogram":
        col = st.sidebar.selectbox("Column", numeric_cols)
        bins = st.sidebar.slider("Bins", 5, 100, 30)
        fig = px.histogram(filters_df, x=col, nbins=bins, title=chart_title)

    elif chart_type == "Box":
        y = st.sidebar.selectbox("Y-axis", numeric_cols)
        x = st.sidebar.selectbox("Group by", cat_cols)
        color = st.sidebar.selectbox("Color by", [None] + cat_cols)
        fig = px.box(filters_df, x=x, y=y, color=color, title=chart_title)

    elif chart_type == "Heatmap":
        corr = filters_df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title=chart_title)

    elif chart_type == "Pie":
        labels = st.sidebar.selectbox("Labels", cat_cols)
        values = st.sidebar.selectbox("Values", numeric_cols)
        fig = px.pie(filters_df, names=labels, values=values, title=chart_title)

    elif chart_type == "Bar":
        x = st.sidebar.selectbox("X-axis", cat_cols)
        y = st.sidebar.selectbox("Y-axis", numeric_cols)
        color = st.sidebar.selectbox("Color by", [None] + cat_cols)
        fig = px.bar(filters_df, x=x, y=y, color=color, title=chart_title)

    elif chart_type == "Area":
        x = st.sidebar.selectbox("X-axis", numeric_cols + cat_cols)
        y = st.sidebar.selectbox("Y-axis", numeric_cols)
        color = st.sidebar.selectbox("Color by", [None] + cat_cols)
        fig = px.area(filters_df, x=x, y=y, color=color, title=chart_title)

    elif chart_type == "Violin":
        y = st.sidebar.selectbox("Y-axis", numeric_cols)
        x = st.sidebar.selectbox("Category (X-axis)", cat_cols)
        color = st.sidebar.selectbox("Color by", [None] + cat_cols)
        fig = px.violin(filters_df, y=y, x=x, color=color, box=True, points="all", title=chart_title)

    elif chart_type == "Treemap":
        path_col = st.sidebar.multiselect("Hierarchy (top to bottom)", cat_cols)
        value_col = st.sidebar.selectbox("Size by", numeric_cols)
        if path_col:
            fig = px.treemap(filters_df, path=path_col, values=value_col, title=chart_title)

    if fig:
        fig.update_layout(width=chart_width, height=chart_height)
        if dark_mode == "Dark":
            fig.update_layout(template="plotly_dark", plot_bgcolor="rgba(0, 0, 0, 1)", paper_bgcolor="rgba(0, 0, 0, 1)")
        else:
            fig.update_layout(template="plotly_white", plot_bgcolor="rgba(255, 255, 255, 1)", paper_bgcolor="rgba(255, 255, 255, 1)")

        st.plotly_chart(fig, use_container_width=True)

    st.download_button("⬇️ Download Filtered Data", filters_df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")

    if st.sidebar.button("🔄 Reset Filters"):
        st.experimental_rerun()

else:
    st.info("📂 Please upload a data file to begin.")
