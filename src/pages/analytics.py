import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.db import get_db, get_sales_with_rls


def render_analytics():
    st.markdown("<h1 style='margin-bottom: 2rem;'>Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    db = get_db()
    
    try:
        user_id = get_user_id(db, st.session_state.username)
        sales_df = get_sales_with_rls(db, st.session_state.user_role, user_id)
        
        if sales_df.empty:
            st.info("No sales data available for your role")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = sales_df["total_amount"].sum()
            st.metric("Total Sales", f"${total_sales:,.2f}", delta=f"+{total_sales*0.1:,.0f}")
        
        with col2:
            total_transactions = len(sales_df)
            st.metric("Transactions", f"{total_transactions:,}", delta=f"+{int(total_transactions*0.15)}")
        
        with col3:
            avg_transaction = sales_df["total_amount"].mean()
            st.metric("Avg. Transaction", f"${avg_transaction:,.2f}")
        
        with col4:
            total_quantity = sales_df["quantity"].sum()
            st.metric("Units Sold", f"{total_quantity:,}")
        
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3 style='margin-bottom: 1rem;'>Sales by Region</h3>", unsafe_allow_html=True)
            region_data = sales_df.groupby("region")["total_amount"].sum().sort_values(ascending=False)
            
            fig_region = go.Figure(data=[
                go.Bar(
                    x=region_data.index,
                    y=region_data.values,
                    marker=dict(color="#1F77B4"),
                    text=[f"${val:,.0f}" for val in region_data.values],
                    textposition="outside"
                )
            ])
            
            fig_region.update_layout(
                xaxis_title="Region",
                yaxis_title="Sales Amount",
                template="plotly_dark",
                paper_bgcolor="#161B22",
                plot_bgcolor="#161B22",
                font=dict(color="#E0E0E0"),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig_region, use_container_width=True)
        
        with col2:
            st.markdown("<h3 style='margin-bottom: 1rem;'>Top Products</h3>", unsafe_allow_html=True)
            product_data = sales_df.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(8)
            
            fig_products = go.Figure(data=[
                go.Bar(
                    y=product_data.index,
                    x=product_data.values,
                    orientation="h",
                    marker=dict(color="#1F77B4"),
                    text=[f"{val:,}" for val in product_data.values],
                    textposition="outside"
                )
            ])
            
            fig_products.update_layout(
                xaxis_title="Units Sold",
                yaxis_title="Product",
                template="plotly_dark",
                paper_bgcolor="#161B22",
                plot_bgcolor="#161B22",
                font=dict(color="#E0E0E0"),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig_products, use_container_width=True)
        
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='margin-bottom: 1rem;'>Sales Trend</h3>", unsafe_allow_html=True)
        
        daily_sales = sales_df.groupby("date")["total_amount"].sum().reset_index().sort_values("date")
        
        fig_trend = go.Figure(data=[
            go.Scatter(
                x=daily_sales["date"],
                y=daily_sales["total_amount"],
                mode="lines+markers",
                line=dict(color="#1F77B4", width=2),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(31, 119, 180, 0.2)"
            )
        ])
        
        fig_trend.update_layout(
            xaxis_title="Date",
            yaxis_title="Sales Amount",
            template="plotly_dark",
            paper_bgcolor="#161B22",
            plot_bgcolor="#161B22",
            font=dict(color="#E0E0E0"),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.markdown("<h3 style='margin-bottom: 1rem; margin-top: 2rem;'>Sales by Product Category</h3>", unsafe_allow_html=True)
        
        category_data = sales_df.groupby("product_name")["quantity"].sum().head(12)
        
        colors = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", "#8C564B"]
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=category_data.index,
                values=category_data.values,
                marker=dict(colors=colors * 2)
            )
        ])
        
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161B22",
            font=dict(color="#E0E0E0"),
            height=400
        )
        
        col1, col2 = st.columns([1.2, 0.8])
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("<h4 style='margin-bottom: 1rem;'>Summary Statistics</h4>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 1rem;'>
                <p style='color: #8B949E; margin: 0.5rem 0;'>Average Transaction: <span style='color: #58A6FF; font-weight: bold;'>${sales_df['total_amount'].mean():,.2f}</span></p>
                <p style='color: #8B949E; margin: 0.5rem 0;'>Median Transaction: <span style='color: #58A6FF; font-weight: bold;'>${sales_df['total_amount'].median():,.2f}</span></p>
                <p style='color: #8B949E; margin: 0.5rem 0;'>Max Transaction: <span style='color: #58A6FF; font-weight: bold;'>${sales_df['total_amount'].max():,.2f}</span></p>
                <p style='color: #8B949E; margin: 0.5rem 0;'>Min Transaction: <span style='color: #58A6FF; font-weight: bold;'>${sales_df['total_amount'].min():,.2f}</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    finally:
        db.close()


def get_user_id(db, username: str) -> int:
    result = db.execute("SELECT id FROM users WHERE username = ?", [username]).fetchall()
    return result[0][0] if result else 1