import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.db import get_db, get_sales_with_rls


def render_reports():
    st.markdown("<h1 style='margin-bottom: 2rem;'>Reports</h1>", unsafe_allow_html=True)
    
    db = get_db()
    
    try:
        tab1, tab2, tab3 = st.tabs(["Sales Report", "Regional Analysis", "Export"])
        
        with tab1:
            render_sales_report(db)
        
        with tab2:
            render_regional_analysis(db)
        
        with tab3:
            render_export(db)
    
    finally:
        db.close()


def render_sales_report(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>Sales Performance Report</h3>", unsafe_allow_html=True)
    
    user_id = get_user_id(db, st.session_state.username)
    sales_df = get_sales_with_rls(db, st.session_state.user_role, user_id)
    
    if sales_df.empty:
        st.info("No sales data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        date_from = st.date_input(
            "From Date",
            value=sales_df["date"].min(),
            key="report_date_from"
        )
    
    with col2:
        date_to = st.date_input(
            "To Date",
            value=sales_df["date"].max(),
            key="report_date_to"
        )
    
    filtered_sales = sales_df[
        (pd.to_datetime(sales_df["date"]) >= pd.Timestamp(date_from)) &
        (pd.to_datetime(sales_df["date"]) <= pd.Timestamp(date_to))
    ]
    
    if filtered_sales.empty:
        st.warning("No data for selected date range")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Period Sales", f"${filtered_sales['total_amount'].sum():,.2f}")
    
    with col2:
        st.metric("Transactions", len(filtered_sales))
    
    with col3:
        st.metric("Average Sale", f"${filtered_sales['total_amount'].mean():,.2f}")
    
    with col4:
        st.metric("Units Sold", int(filtered_sales['quantity'].sum()))
    
    st.markdown("<h4 style='margin-top: 2rem; margin-bottom: 1rem;'>Daily Sales Trend</h4>", unsafe_allow_html=True)
    
    daily_sales = filtered_sales.groupby("date").agg({
        "total_amount": "sum",
        "quantity": "sum"
    }).reset_index().sort_values("date")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_sales["date"],
        y=daily_sales["total_amount"],
        mode="lines+markers",
        name="Sales Amount",
        line=dict(color="#1F77B4", width=2),
        marker=dict(size=6),
        yaxis="y"
    ))
    
    fig.add_trace(go.Bar(
        x=daily_sales["date"],
        y=daily_sales["quantity"],
        name="Units Sold",
        marker=dict(color="#FF7F0E"),
        opacity=0.3,
        yaxis="y2"
    ))
    
    fig.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(title="Sales Amount", color="#1F77B4"),
        yaxis2=dict(title="Units Sold", color="#FF7F0E", overlaying="y", side="right"),
        template="plotly_dark",
        paper_bgcolor="#161B22",
        plot_bgcolor="#161B22",
        font=dict(color="#E0E0E0"),
        hovermode="x unified",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<h4 style='margin-top: 2rem; margin-bottom: 1rem;'>Top Performing Products</h4>", unsafe_allow_html=True)
    
    product_performance = filtered_sales.groupby("product_name").agg({
        "quantity": "sum",
        "total_amount": "sum",
        "unit_price": "first"
    }).reset_index().sort_values("total_amount", ascending=False).head(10)
    
    fig_top = go.Figure(data=[
        go.Bar(
            x=product_performance["product_name"],
            y=product_performance["total_amount"],
            marker=dict(color="#1F77B4"),
            text=[f"${val:,.0f}" for val in product_performance["total_amount"]],
            textposition="outside"
        )
    ])
    
    fig_top.update_layout(
        xaxis_title="Product",
        yaxis_title="Sales Amount",
        template="plotly_dark",
        paper_bgcolor="#161B22",
        plot_bgcolor="#161B22",
        font=dict(color="#E0E0E0"),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_top, use_container_width=True)


def render_regional_analysis(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>Regional Analysis</h3>", unsafe_allow_html=True)
    
    user_id = get_user_id(db, st.session_state.username)
    sales_df = get_sales_with_rls(db, st.session_state.user_role, user_id)
    
    if sales_df.empty:
        st.info("No sales data available")
        return
    
    regional_stats = sales_df.groupby("region").agg({
        "total_amount": ["sum", "mean", "count"],
        "quantity": "sum"
    }).reset_index()
    
    regional_stats.columns = ["Region", "Total Sales", "Avg Sale", "Transactions", "Units Sold"]
    regional_stats = regional_stats.sort_values("Total Sales", ascending=False)
    
    st.dataframe(
        regional_stats.assign(**{
            "Total Sales": regional_stats["Total Sales"].apply(lambda x: f"${x:,.2f}"),
            "Avg Sale": regional_stats["Avg Sale"].apply(lambda x: f"${x:,.2f}"),
            "Transactions": regional_stats["Transactions"].astype(int),
            "Units Sold": regional_stats["Units Sold"].astype(int)
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<h4 style='margin-top: 2rem; margin-bottom: 1rem;'>Market Share by Region</h4>", unsafe_allow_html=True)
    
    fig_pie = go.Figure(data=[
        go.Pie(
            labels=regional_stats["Region"],
            values=regional_stats["Total Sales"],
            marker=dict(colors=["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728"])
        )
    ])
    
    fig_pie.update_layout(
        template="plotly_dark",
        paper_bgcolor="#161B22",
        font=dict(color="#E0E0E0"),
        height=400
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)


def render_export(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>Export Data</h3>", unsafe_allow_html=True)
    
    user_id = get_user_id(db, st.session_state.username)
    sales_df = get_sales_with_rls(db, st.session_state.user_role, user_id)
    
    if sales_df.empty:
        st.info("No data to export")
        return
    
    export_format = st.selectbox("Select Format", ["CSV", "Excel"])
    
    if export_format == "CSV":
        csv_data = sales_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    else:
        excel_data = sales_df.to_excel(index=False, engine="openpyxl")
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.info(f"Total records to export: {len(sales_df)}")


def get_user_id(db, username: str) -> int:
    result = db.execute("SELECT id FROM users WHERE username = ?", [username]).fetchall()
    return result[0][0] if result else 1