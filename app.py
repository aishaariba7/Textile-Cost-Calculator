import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(
    page_title="Textile Cost Calculator",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Textile & Garment Cost Calculator")
st.caption("Calculate exact FOB costs, breakdowns, and profit margins for textile production.")

# Sidebar - Master Parameters
st.sidebar.header("📋 General Order Details")
order_quantity = st.sidebar.number_input("Order Quantity (Units)", min_value=1, value=1000, step=100)
target_margin_pct = st.sidebar.slider("Target Profit Margin (%)", min_value=0.0, max_value=50.0, value=20.0, step=0.5)

# Tabs for Sectional Inputs
tab1, tab2, tab3 = st.tabs(["💵 1. Cost Inputs", "📊 2. Cost Analysis", "📄 3. Summary & Export"])

with tab1:
    st.subheader("Raw Materials & Fabric Stage")
    col1, col2 = st.columns(2)
    
    with col1:
        yarn_price = st.number_input("Yarn Rate ($ / kg)", min_value=0.0, value=4.50, step=0.10)
        fabric_consumption = st.number_input("Fabric Consumption per Garment (kg)", min_value=0.0, value=0.25, step=0.01)
        yarn_wastage_pct = st.number_input("Yarn Process Loss / Wastage (%)", min_value=0.0, value=5.0, step=0.5)

    with col2:
        knitting_weaving_cost = st.number_input("Knitting / Weaving Cost ($ / kg)", min_value=0.0, value=0.80, step=0.05)
        dyeing_finishing_cost = st.number_input("Dyeing & Finishing Cost ($ / kg)", min_value=0.0, value=1.50, step=0.10)

    st.markdown("---")
    st.subheader("Garment Manufacturing & CMT Stage")
    col3, col4 = st.columns(2)

    with col3:
        cmt_cost = st.number_input("Cut, Make & Trim (CMT) per Unit ($)", min_value=0.0, value=2.20, step=0.10)
        trims_cost = st.number_input("Trims & Accessories per Unit ($)", min_value=0.0, value=0.60, step=0.05)

    with col4:
        packaging_logistics = st.number_input("Packaging & Freight per Unit ($)", min_value=0.0, value=0.35, step=0.05)
        overhead_pct = st.number_input("Factory Overhead Allowance (%)", min_value=0.0, value=8.0, step=0.5)

# --- CALCULATIONS ---
# 1. Effective Fabric Cost per KG
fabric_cost_per_kg = (yarn_price * (1 + yarn_wastage_pct / 100)) + knitting_weaving_cost + dyeing_finishing_cost

# 2. Fabric Cost per Unit
fabric_cost_per_unit = fabric_cost_per_kg * fabric_consumption

# 3. Direct Costs per Unit
direct_unit_cost = fabric_cost_per_unit + cmt_cost + trims_cost + packaging_logistics

# 4. Total Cost with Overheads
total_unit_cost = direct_unit_cost * (1 + overhead_pct / 100)

# 5. Pricing & Profit
target_selling_price = total_unit_cost / (1 - target_margin_pct / 100) if target_margin_pct < 100 else 0
profit_per_unit = target_selling_price - total_unit_cost

total_order_cost = total_unit_cost * order_quantity
total_order_revenue = target_selling_price * order_quantity
total_order_profit = profit_per_unit * order_quantity

# --- DISPLAY ANALYSIS ---
with tab2:
    st.subheader("Unit Economics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fabric Cost / Unit", f"${fabric_cost_per_unit:.2f}")
    m2.metric("Total Unit Cost", f"${total_unit_cost:.2f}")
    m3.metric("Target Selling Price (FOB)", f"${target_selling_price:.2f}")
    m4.metric("Profit / Unit", f"${profit_per_unit:.2f}")

    st.markdown("---")
    
    # Cost Breakdown Visualization
    cost_data = pd.DataFrame({
        "Component": ["Fabric Material", "CMT (Labor/Stitching)", "Trims & Accessories", "Packaging & Freight", "Overheads"],
        "Cost_Per_Unit": [
            fabric_cost_per_unit,
            cmt_cost,
            trims_cost,
            packaging_logistics,
            total_unit_cost - direct_unit_cost
        ]
    })

    col_chart, col_table = st.columns([3, 2])
    with col_chart:
        fig = px.pie(cost_data, names="Component", values="Cost_Per_Unit", title="Cost Breakdown per Unit", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_table:
        st.write("### Detailed Cost Breakdown")
        cost_data["Percentage"] = (cost_data["Cost_Per_Unit"] / total_unit_cost) * 100
        cost_data["Cost_Per_Unit"] = cost_data["Cost_Per_Unit"].apply(lambda x: f"${x:.2f}")
        cost_data["Percentage"] = cost_data["Percentage"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(cost_data, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Order Level Summary")
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Order Cost", f"${total_order_cost:,.2f}")
    s2.metric("Total Projected Revenue", f"${total_order_revenue:,.2f}")
    s3.metric("Total Estimated Profit", f"${total_order_profit:,.2f}")

    st.markdown("---")
    
    # Prepare CSV Download
    summary_df = pd.DataFrame([{
        "Order Quantity": order_quantity,
        "Fabric Cost/Unit": round(fabric_cost_per_unit, 2),
        "Total Cost/Unit": round(total_unit_cost, 2),
        "FOB Price/Unit": round(target_selling_price, 2),
        "Total Order Revenue": round(total_order_revenue, 2),
        "Total Order Profit": round(total_order_profit, 2)
    }])
    
    csv_data = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Quotation Summary (CSV)",
        data=csv_data,
        file_name="textile_cost_quotation.csv",
        mime="text/csv"
    )