import streamlit as st
import pandas as pd
from src.db import get_db, get_sales_with_rls, get_products


def render_data_browser():
    st.markdown("<h1 style='margin-bottom: 2rem;'>Data Browser</h1>", unsafe_allow_html=True)
    
    db = get_db()
    
    try:
        tab1, tab2, tab3 = st.tabs(["Sales Data", "Products", "Statistics"])
        
        with tab1:
            render_sales_browser(db)
        
        with tab2:
            render_products_browser(db)
        
        with tab3:
            render_statistics(db)
    
    finally:
        db.close()


def render_sales_browser(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>Sales Records</h3>", unsafe_allow_html=True)
    
    user_id = get_user_id(db, st.session_state.username)
    sales_df = get_sales_with_rls(db, st.session_state.user_role, user_id)
    
    if sales_df.empty:
        st.info("No sales data available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.user_role != "user":
            selected_region = st.multiselect(
                "Filter by Region",
                options=sales_df["region"].unique(),
                default=sales_df["region"].unique().tolist()
            )
            sales_df = sales_df[sales_df["region"].isin(selected_region)]
    
    with col2:
        sort_column = st.selectbox("Sort by", ["date", "total_amount", "quantity"])
    
    with col3:
        sort_order = st.selectbox("Order", ["Descending", "Ascending"])
    
    sales_df = sales_df.sort_values(sort_column, ascending=(sort_order == "Ascending"))
    
    st.markdown("""
    <style>
        .dataframe-container {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        sales_df[["id", "date", "product_name", "quantity", "unit_price", "total_amount", "region"]],
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = sales_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="sales_data.csv",
            mime="text/csv"
        )
    
    with col2:
        st.metric("Total Records", len(sales_df))
    
    with col3:
        st.metric("Total Value", f"${sales_df['total_amount'].sum():,.2f}")


def render_products_browser(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>Product Inventory</h3>", unsafe_allow_html=True)
    
    products_df = get_products(db)
    
    if products_df.empty:
        st.info("No products available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        category_filter = st.multiselect(
            "Filter by Category",
            options=products_df["category"].unique(),
            default=products_df["category"].unique().tolist()
        )
        products_df = products_df[products_df["category"].isin(category_filter)]
    
    with col2:
        sort_column = st.selectbox("Sort by", ["name", "price", "stock_quantity"])
    
    products_df = products_df.sort_values(sort_column, ascending=True)
    
    st.dataframe(
        products_df[["id", "name", "category", "price", "stock_quantity"]],
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = products_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="products.csv",
            mime="text/csv"
        )
    
    with col2:
        st.metric("Total Products", len(products_df))
    
    with col3:
        total_value = (products_df["price"] * products_df["stock_quantity"]).sum()
        st.metric("Inventory Value", f"${total_value:,.2f}")


def render_statistics(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>Data Statistics</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_count = db.execute("SELECT COUNT(*) as cnt FROM users").fetchall()[0][0]
        st.metric("Total Users", user_count)
    
    with col2:
        product_count = db.execute("SELECT COUNT(*) as cnt FROM products").fetchall()[0][0]
        st.metric("Total Products", product_count)
    
    col1, col2 = st.columns(2)
    
    with col1:
        sales_count = db.execute("SELECT COUNT(*) as cnt FROM sales").fetchall()[0][0]
        st.metric("Total Transactions", sales_count)
    
    with col2:
        total_sales_value = db.execute("SELECT COALESCE(SUM(total_amount), 0) as total FROM sales").fetchall()[0][0]
        st.metric("Total Sales Value", f"${total_sales_value:,.2f}")
    
    st.markdown("<h4 style='margin-top: 2rem; margin-bottom: 1rem;'>Database Summary</h4>", unsafe_allow_html=True)
    
    stats = {
        "Metric": ["Users", "Active Users", "Products", "Sales Transactions", "Regions"],
        "Count": [
            user_count,
            db.execute("SELECT COUNT(*) as cnt FROM users WHERE is_active = TRUE").fetchall()[0][0],
            product_count,
            sales_count,
            db.execute("SELECT COUNT(DISTINCT region) as cnt FROM sales").fetchall()[0][0]
        ]
    }
    
    stats_df = pd.DataFrame(stats)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)


def get_user_id(db, username: str) -> int:
    result = db.execute("SELECT id FROM users WHERE username = ?", [username]).fetchall()
    return result[0][0] if result else 1