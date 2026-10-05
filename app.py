import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Nassau Candy | Route Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Theme / CSS
# -----------------------------
st.markdown("""
<style>
:root {
    --bg: #0b1020;
    --card: #121a2f;
    --card2: #17213a;
    --text: #ffffff;
    --muted: #d6deee;
    --accent: #6ee7f9;
    --accent2: #8b7cff;
    --good: #49d49d;
    --warn: #ffcb6b;
    --bad: #ff6b7a;
}
.stApp {
    background: radial-gradient(circle at 10% 0%, #17234a 0%, #0b1020 36%, #080c18 100%);
}
.block-container {padding-top: 1.3rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #10182e 0%, #0b1020 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}
.hero {
    padding: 28px 32px;
    border-radius: 24px;
    background: linear-gradient(120deg, rgba(110,231,249,.16), rgba(139,124,255,.16));
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 15px 50px rgba(0,0,0,.22);
    margin-bottom: 22px;
}
.hero h1 {margin:0; font-size: 2.4rem; letter-spacing:-1px;}
.hero p {color:#b9c4dc; margin:8px 0 0; font-size:1rem;}
.kpi {
    padding: 20px 20px;
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(23,33,58,.96), rgba(14,21,39,.96));
    border: 1px solid rgba(255,255,255,.08);
    min-height: 126px;
    box-shadow: 0 8px 28px rgba(0,0,0,.18);
}
.kpi .label {color:#9aa8c7; font-size:.82rem; text-transform:uppercase; letter-spacing:.08em;}
.kpi .value {font-size:1.85rem; font-weight:800; margin-top:8px;}
.kpi .sub {color:#9aa8c7; font-size:.78rem; margin-top:5px;}
.section {
    margin: 28px 0 12px;
    font-size: 1.25rem;
    font-weight: 800;
}
.insight {
    padding: 15px 18px;
    border-radius: 15px;
    background: rgba(110,231,249,.07);
    border-left: 4px solid #6ee7f9;
    color: #dbe7ff;
    margin: 8px 0;
}
.warning {
    padding: 15px 18px;
    border-radius: 15px;
    background: rgba(255,203,107,.08);
    border-left: 4px solid #ffcb6b;
    color: #ffe8b1;
    margin: 10px 0 18px;
}
.small-note {color:#8f9db8; font-size:.78rem;}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.03);
    border-radius: 15px;
    padding: 10px 14px;
}
/* Make Streamlit text bright on dark background */

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6 {
    color: #ffffff;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Hero text */
.hero h1 {
    color: #ffffff !important;
}

.hero p {
    color: #e5eaff !important;
}

/* KPI text */
.kpi .label {
    color: #FFE8A3 !important;
    font-weight:600;
}

.kpi .value {
    color: #FFFFFF !important;
}

.kpi .sub {
    color: #C3CDE1 !important;
}

/* Section headings */
.section {
    color: #ffffff !important;
}

/* Small notes */
.small-note {
    color: #c3cde1 !important;
}

/* Streamlit widgets */
.stSelectbox label,
.stMultiSelect label,
.stDateInput label,
.stSlider label {
    color: #ffffff !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    color: #ffffff !important;
}

/* Dataframe text */
[data-testid="stDataFrame"] {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Constants
# -----------------------------
FACTORIES = {
    "Lot's O' Nuts": (32.881893, -111.768036),
    "Wicked Choccy's": (32.076176, -81.088371),
    "Sugar Shack": (48.119140, -96.181150),
    "Secret Factory": (41.446333, -90.565487),
    "The Other Factory": (35.117500, -89.971107),
}

PRODUCT_FACTORY = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory",
}

# -----------------------------
# Data
# -----------------------------
@st.cache_data
def load_data():
    base = Path(__file__).parent
    candidates = [
        base / "data" / "Nassau Candy Distributor.csv",
        base / "Nassau Candy Distributor.csv",
    ]
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p)
            break
    else:
        raise FileNotFoundError("Dataset not found. Put the CSV inside the data folder.")

    # Normalize names while retaining original fields
    df.columns = [c.strip() for c in df.columns]

    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True, errors="coerce")

    numeric_cols = ["Sales", "Units", "Gross Profit", "Cost", "Postal Code", "Customer ID", "Row ID"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df["Factory"] = df["Product Name"].map(PRODUCT_FACTORY).fillna("Unknown Factory")
    df["Factory Latitude"] = df["Factory"].map(lambda x: FACTORIES.get(x, (np.nan, np.nan))[0])
    df["Factory Longitude"] = df["Factory"].map(lambda x: FACTORIES.get(x, (np.nan, np.nan))[1])

    df["Lead Time (Days)"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Route"] = df["Factory"] + " → " + df["State/Province"].astype(str)
    df["Regional Route"] = df["Factory"] + " → " + df["Region"].astype(str)
    df["Shipment Month"] = df["Ship Date"].dt.to_period("M").astype(str)
    df["Ship Year"] = df["Ship Date"].dt.year

    # Validity flags
    df["Valid Lead Time"] = df["Lead Time (Days)"].notna() & (df["Lead Time (Days)"] >= 0)
    df["Data Quality Issue"] = ~df["Valid Lead Time"]

    return df

df = load_data()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown("## 🚚 Nassau Candy")
st.sidebar.caption("Route Intelligence & Logistics Analytics")

pages = [
    "🏠 Executive Overview",
    "🛣️ Route Efficiency",
    "🗺️ Geographic Bottlenecks",
    "🚀 Ship Mode Comparison",
    "🔎 Route Drill-Down",
    "🧹 Data Quality",
]
page = st.sidebar.radio("Navigate", pages)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

regions = sorted(df["Region"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

states = sorted(df["State/Province"].dropna().unique())
selected_states = st.sidebar.multiselect("State / Province", states)

modes = sorted(df["Ship Mode"].dropna().unique())
selected_modes = st.sidebar.multiselect("Ship mode", modes, default=modes)

factories = sorted(df["Factory"].dropna().unique())
selected_factories = st.sidebar.multiselect("Factory", factories, default=factories)

valid_for_slider = df.loc[df["Valid Lead Time"], "Lead Time (Days)"]
lt_min = int(max(0, valid_for_slider.min()))
lt_max = int(valid_for_slider.max())
default_threshold = int(valid_for_slider.median())
threshold = st.sidebar.slider(
    "Delay threshold (days)",
    min_value=0,
    max_value=lt_max,
    value=default_threshold,
    step=1,
)

filtered = df[
    (df["Order Date"].dt.date >= start_date) &
    (df["Order Date"].dt.date <= end_date) &
    (df["Region"].isin(selected_regions)) &
    (df["Ship Mode"].isin(selected_modes)) &
    (df["Factory"].isin(selected_factories))
].copy()

if selected_states:
    filtered = filtered[filtered["State/Province"].isin(selected_states)].copy()

filtered["Delayed"] = filtered["Lead Time (Days)"] > threshold

# -----------------------------
# Helpers
# -----------------------------
def money(x):
    return f"${x:,.2f}"

def kpi_card(label, value, sub=""):
    st.markdown(
        f'<div class="kpi"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True
    )

def route_table(data):
    r = (
        data[data["Valid Lead Time"]]
        .groupby(["Factory", "State/Province"], as_index=False)
        .agg(
            Shipments=("Order ID", "count"),
            Avg_Lead_Time=("Lead Time (Days)", "mean"),
            Lead_Time_Std=("Lead Time (Days)", "std"),
            Delayed=("Delayed", "sum"),
            Sales=("Sales", "sum"),
        )
    )
    r["Lead_Time_Std"] = r["Lead_Time_Std"].fillna(0)
    r["Delay_%"] = np.where(r["Shipments"] > 0, r["Delayed"] / r["Shipments"] * 100, 0)
    if len(r):
        mn, mx = r["Avg_Lead_Time"].min(), r["Avg_Lead_Time"].max()
        r["Efficiency Score"] = 100 if mx == mn else 100 * (mx - r["Avg_Lead_Time"]) / (mx - mn)
    else:
        r["Efficiency Score"] = []
    r["Route"] = r["Factory"] + " → " + r["State/Province"]
    return r.sort_values("Avg_Lead_Time")

def plotly_layout(fig, height=430):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe4f5"),
        legend=dict(orientation="h", y=1.08),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)")
    return fig

# -----------------------------
# Hero
# -----------------------------
st.markdown("""
<div class="hero">
<h1>🚚 Nassau Candy Route Intelligence</h1>
<p>Factory-to-customer shipping efficiency, delay detection and geographic bottleneck analytics.</p>
</div>
""", unsafe_allow_html=True)

if len(filtered) == 0:
    st.error("No records match the current filters. Please broaden the selections.")
    st.stop()

valid = filtered[filtered["Valid Lead Time"]].copy()

# Data quality banner
bad_dates = int((~filtered["Valid Lead Time"]).sum())
if bad_dates:
    st.markdown(
        f'<div class="warning">⚠️ <b>{bad_dates:,}</b> filtered records have missing or invalid lead times and are excluded from lead-time KPIs.</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# PAGE: Overview
# -----------------------------
if page == "🏠 Executive Overview":
    avg_lt = valid["Lead Time (Days)"].mean()
    delayed = int(valid["Delayed"].sum())
    delay_pct = delayed / len(valid) * 100 if len(valid) else 0
    route_count = valid.groupby(["Factory", "State/Province"]).ngroups
    sales = valid["Sales"].sum()

    cols = st.columns(5)
    with cols[0]: kpi_card("Shipments", f"{len(filtered):,}", "Orders in current view")
    with cols[1]: kpi_card("Avg Lead Time", f"{avg_lt:,.1f} d", "Order → shipment")
    with cols[2]: kpi_card("Delay Frequency", f"{delay_pct:.1f}%", f">{threshold} days")
    with cols[3]: kpi_card("Active Routes", f"{route_count:,}", "Factory → state")
    with cols[4]: kpi_card("Sales Covered", money(sales), "Filtered records")

    st.markdown('<div class="section">📊 Network performance</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    monthly = valid.groupby("Shipment Month", as_index=False).agg(
        Avg_Lead_Time=("Lead Time (Days)", "mean"),
        Shipments=("Order ID", "count")
    )
    with c1:
        fig = px.line(monthly, x="Shipment Month", y="Avg_Lead_Time",
                      markers=True, title="Average Lead Time by Shipment Month")
        st.plotly_chart(plotly_layout(fig), use_container_width=True)

    region_perf = valid.groupby("Region", as_index=False).agg(
        Avg_Lead_Time=("Lead Time (Days)", "mean"),
        Shipments=("Order ID", "count")
    ).sort_values("Avg_Lead_Time")
    with c2:
        fig = px.bar(region_perf, x="Region", y="Avg_Lead_Time",
                     color="Avg_Lead_Time", title="Average Lead Time by Region")
        st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.markdown('<div class="section">🏆 Route leaderboard</div>', unsafe_allow_html=True)
    rt = route_table(filtered)
    a, b = st.columns(2)
    with a:
        st.markdown("**Top 10 fastest routes**")
        st.dataframe(
            rt.head(10)[["Route", "Shipments", "Avg_Lead_Time", "Delay_%", "Efficiency Score"]]
            .style.format({"Avg_Lead_Time":"{:.1f}", "Delay_%":"{:.1f}%", "Efficiency Score":"{:.1f}"}),
            use_container_width=True, hide_index=True
        )
    with b:
        st.markdown("**Bottom 10 slowest routes**")
        st.dataframe(
            rt.tail(10).sort_values("Avg_Lead_Time", ascending=False)
            [["Route", "Shipments", "Avg_Lead_Time", "Delay_%", "Efficiency Score"]]
            .style.format({"Avg_Lead_Time":"{:.1f}", "Delay_%":"{:.1f}%", "Efficiency Score":"{:.1f}"}),
            use_container_width=True, hide_index=True
        )

    worst = rt.sort_values(["Avg_Lead_Time", "Shipments"], ascending=[False, False]).iloc[0]
    best = rt.iloc[0]
    st.markdown(
        f'<div class="insight">💡 <b>Decision signal:</b> The fastest route in the current view is '
        f'<b>{best["Route"]}</b> at {best["Avg_Lead_Time"]:.1f} days, while the slowest is '
        f'<b>{worst["Route"]}</b> at {worst["Avg_Lead_Time"]:.1f} days. '
        f'Use route volume alongside lead time before changing network policy.</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# PAGE: Route Efficiency
# -----------------------------
elif page == "🛣️ Route Efficiency":
    st.markdown('<div class="section">🛣️ Route Efficiency Benchmarking</div>', unsafe_allow_html=True)
    rt = route_table(filtered)

    if rt.empty:
        st.warning("No valid routes under the current filters.")
        st.stop()

    top_n = st.slider("Routes to display", 5, min(30, len(rt)), min(10, len(rt)))

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(rt.head(top_n).sort_values("Avg_Lead_Time"),
                     x="Avg_Lead_Time", y="Route", orientation="h",
                     color="Efficiency Score", title=f"Top {top_n} Most Efficient Routes")
        st.plotly_chart(plotly_layout(fig, 520), use_container_width=True)
    with c2:
        bottom = rt.tail(top_n).sort_values("Avg_Lead_Time", ascending=False)
        fig = px.bar(bottom, x="Avg_Lead_Time", y="Route", orientation="h",
                     color="Delay_%", title=f"Bottom {top_n} Least Efficient Routes")
        st.plotly_chart(plotly_layout(fig, 520), use_container_width=True)

    st.markdown("### Route performance matrix")
    display = rt[[
        "Route", "Factory", "State/Province", "Shipments",
        "Avg_Lead_Time", "Lead_Time_Std", "Delay_%", "Efficiency Score", "Sales"
    ]].copy()
    st.dataframe(
        display.style.format({
            "Avg_Lead_Time":"{:.1f}",
            "Lead_Time_Std":"{:.1f}",
            "Delay_%":"{:.1f}%",
            "Efficiency Score":"{:.1f}",
            "Sales":"${:,.2f}",
        }),
        use_container_width=True, hide_index=True
    )

    csv = display.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download route analysis CSV", csv, "route_analysis.csv", "text/csv")

# -----------------------------
# PAGE: Geographic
# -----------------------------
elif page == "🗺️ Geographic Bottlenecks":
    st.markdown('<div class="section">🗺️ Geographic Shipping Performance</div>', unsafe_allow_html=True)

    state_perf = valid.groupby("State/Province", as_index=False).agg(
        Avg_Lead_Time=("Lead Time (Days)", "mean"),
        Shipments=("Order ID", "count"),
        Delayed=("Delayed", "sum"),
        Sales=("Sales", "sum")
    )
    state_perf["Delay_%"] = state_perf["Delayed"] / state_perf["Shipments"] * 100

    us = state_perf[state_perf["State/Province"].isin([
        "Alabama","Arizona","Arkansas","California","Colorado","Connecticut","Delaware",
        "District of Columbia","Florida","Georgia","Idaho","Illinois","Indiana","Iowa",
        "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan",
        "Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire",
        "New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio",
        "Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota",
        "Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia",
        "Wisconsin","Wyoming"
    ])].copy()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.choropleth(
            us, locations="State/Province", locationmode="USA-states",
            color="Avg_Lead_Time", scope="usa",
            color_continuous_scale="Turbo",
            hover_data={"Shipments":True, "Delay_%":":.1f", "Avg_Lead_Time":":.1f"},
            title="US Average Lead Time Heatmap"
        )
        st.plotly_chart(plotly_layout(fig, 520), use_container_width=True)

    with c2:
        fig = px.scatter(
            state_perf.sort_values("Shipments", ascending=False).head(25),
            x="Shipments", y="Avg_Lead_Time", size="Sales",
            color="Delay_%", hover_name="State/Province",
            title="High-volume vs. High-lead-time States",
            color_continuous_scale="Turbo"
        )
        st.plotly_chart(plotly_layout(fig, 520), use_container_width=True)

    st.markdown("### 🚨 Bottleneck states")
    volume_cutoff = state_perf["Shipments"].quantile(.75)
    bottlenecks = state_perf[
        (state_perf["Shipments"] >= volume_cutoff) &
        (state_perf["Avg_Lead_Time"] >= state_perf["Avg_Lead_Time"].median())
    ].sort_values(["Avg_Lead_Time", "Shipments"], ascending=[False, False])

    st.dataframe(
        bottlenecks.style.format({
            "Avg_Lead_Time":"{:.1f}",
            "Delay_%":"{:.1f}%",
            "Sales":"${:,.2f}"
        }),
        use_container_width=True, hide_index=True
    )

    canada = state_perf[~state_perf["State/Province"].isin(us["State/Province"])]
    if not canada.empty:
        st.markdown("### 🇨🇦 Canadian provinces")
        st.dataframe(
            canada.sort_values("Avg_Lead_Time", ascending=False)
            .style.format({"Avg_Lead_Time":"{:.1f}", "Delay_%":"{:.1f}%", "Sales":"${:,.2f}"}),
            use_container_width=True, hide_index=True
        )

# -----------------------------
# PAGE: Ship Mode
# -----------------------------
elif page == "🚀 Ship Mode Comparison":
    st.markdown('<div class="section">🚀 Ship Mode Performance & Cost-Time Tradeoff</div>', unsafe_allow_html=True)

    mode_perf = valid.groupby("Ship Mode", as_index=False).agg(
        Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (Days)", "mean"),
        Median_Lead_Time=("Lead Time (Days)", "median"),
        Lead_Time_Std=("Lead Time (Days)", "std"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
    )
    mode_perf["Delay_%"] = [
        valid.loc[valid["Ship Mode"].eq(m), "Delayed"].mean() * 100
        for m in mode_perf["Ship Mode"]
    ]
    mode_perf["Profit Margin %"] = np.where(
        mode_perf["Sales"] != 0,
        mode_perf["Gross_Profit"] / mode_perf["Sales"] * 100, 0
    )

    cols = st.columns(len(mode_perf))
    for col, (_, row) in zip(cols, mode_perf.iterrows()):
        with col:
            kpi_card(row["Ship Mode"], f'{row["Avg_Lead_Time"]:.1f} d',
                     f'{int(row["Shipments"]):,} shipments • {row["Delay_%"]:.1f}% delayed')

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(mode_perf, x="Ship Mode", y="Avg_Lead_Time",
                     color="Avg_Lead_Time", title="Average Lead Time by Ship Mode")
        st.plotly_chart(plotly_layout(fig), use_container_width=True)
    with c2:
        fig = px.bar(mode_perf, x="Ship Mode", y="Delay_%",
                     color="Delay_%", title=f"Delay Frequency (>{threshold} days)")
        st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.markdown("### Mode comparison table")
    st.dataframe(
        mode_perf.style.format({
            "Avg_Lead_Time":"{:.1f}",
            "Median_Lead_Time":"{:.1f}",
            "Lead_Time_Std":"{:.1f}",
            "Delay_%":"{:.1f}%",
            "Sales":"${:,.2f}",
            "Cost":"${:,.2f}",
            "Gross_Profit":"${:,.2f}",
            "Profit Margin %":"{:.1f}%"
        }),
        use_container_width=True, hide_index=True
    )

    fastest = mode_perf.loc[mode_perf["Avg_Lead_Time"].idxmin()]
    most_used = mode_perf.loc[mode_perf["Shipments"].idxmax()]
    st.markdown(
        f'<div class="insight">📌 <b>Tradeoff view:</b> {fastest["Ship Mode"]} has the lowest average lead time '
        f'({fastest["Avg_Lead_Time"]:.1f} days), while {most_used["Ship Mode"]} has the highest shipment volume '
        f'({int(most_used["Shipments"]):,}). Compare cost and service objectives before switching modes.</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# PAGE: Drill Down
# -----------------------------
elif page == "🔎 Route Drill-Down":
    st.markdown('<div class="section">🔎 Route & Order Drill-Down</div>', unsafe_allow_html=True)

    route_options = sorted(valid["Route"].dropna().unique())
    if not route_options:
        st.warning("No valid routes available.")
        st.stop()

    chosen_route = st.selectbox("Select a factory → customer-state route", route_options)
    route_df = filtered[filtered["Route"].eq(chosen_route)].copy()
    route_valid = route_df[route_df["Valid Lead Time"]].copy()

    cols = st.columns(5)
    with cols[0]: kpi_card("Orders", f"{len(route_df):,}")
    with cols[1]: kpi_card("Avg Lead Time", f'{route_valid["Lead Time (Days)"].mean():.1f} d')
    with cols[2]: kpi_card("Median", f'{route_valid["Lead Time (Days)"].median():.1f} d')
    with cols[3]: kpi_card("Delay %", f'{route_valid["Delayed"].mean()*100:.1f}%')
    with cols[4]: kpi_card("Sales", money(route_valid["Sales"].sum()))

    c1, c2 = st.columns(2)
    with c1:
        hist = px.histogram(route_valid, x="Lead Time (Days)", nbins=25,
                            title="Lead-time distribution")
        hist.add_vline(x=threshold, line_dash="dash", annotation_text="Delay threshold")
        st.plotly_chart(plotly_layout(hist), use_container_width=True)

    with c2:
        timeline = route_valid.sort_values("Order Date").copy()
        timeline["Cumulative Shipments"] = np.arange(1, len(timeline) + 1)
        fig = px.scatter(
            timeline, x="Order Date", y="Lead Time (Days)",
            size="Sales", color="Ship Mode",
            hover_data=["Order ID", "Product Name", "City", "State/Province"],
            title="Order-level shipment timeline"
        )
        fig.add_hline(y=threshold, line_dash="dash", annotation_text="Threshold")
        st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.markdown("### Order-level details")
    cols_to_show = [
        "Order ID", "Order Date", "Ship Date", "Ship Mode", "Product Name",
        "City", "State/Province", "Lead Time (Days)", "Sales", "Units",
        "Gross Profit", "Cost", "Delayed"
    ]
    order_view = route_df[cols_to_show].sort_values("Order Date", ascending=False)
    st.dataframe(
        order_view.style.format({
            "Sales":"${:,.2f}", "Gross Profit":"${:,.2f}", "Cost":"${:,.2f}"
        }),
        use_container_width=True, hide_index=True
    )

    csv = order_view.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download route orders", csv, "route_orders.csv", "text/csv")

# -----------------------------
# PAGE: Data Quality
# -----------------------------
else:
    st.markdown('<div class="section">🧹 Data Quality & Validation</div>', unsafe_allow_html=True)

    total = len(df)
    missing = int(df.isna().sum().sum())
    invalid_dates = int(df[["Order Date", "Ship Date"]].isna().any(axis=1).sum())
    negative = int((df["Lead Time (Days)"] < 0).sum())
    unknown_factory = int((df["Factory"] == "Unknown Factory").sum())

    cols = st.columns(4)
    with cols[0]: kpi_card("Rows", f"{total:,}")
    with cols[1]: kpi_card("Missing Cells", f"{missing:,}")
    with cols[2]: kpi_card("Invalid Date Rows", f"{invalid_dates:,}")
    with cols[3]: kpi_card("Unknown Factory", f"{unknown_factory:,}")

    st.markdown("### Validation checks")
    checks = pd.DataFrame({
        "Check": [
            "Missing values",
            "Missing/invalid dates",
            "Negative lead times",
            "Products without factory mapping",
            "Duplicate Row IDs",
            "Duplicate Order IDs"
        ],
        "Result": [
            "PASS" if missing == 0 else "REVIEW",
            "PASS" if invalid_dates == 0 else "REVIEW",
            "PASS" if negative == 0 else "REVIEW",
            "PASS" if unknown_factory == 0 else "REVIEW",
            "PASS" if df["Row ID"].duplicated().sum() == 0 else "REVIEW",
            "INFO — multiple line items may share an order"
        ]
    })
    st.dataframe(checks, use_container_width=True, hide_index=True)

    st.markdown("### ⚠️ Lead-time distribution warning")
    st.markdown(
        f'<div class="warning">The source data produces an average calculated lead time of '
        f'<b>{df["Lead Time (Days)"].mean():,.1f} days</b> (median {df["Lead Time (Days)"].median():,.0f} days). '
        f'This is driven by the source dates: order records are dated before shipment records by roughly 2–4.5 years. '
        f'The dashboard preserves the source data and does not fabricate or overwrite dates.</div>',
        unsafe_allow_html=True
    )

    st.markdown("### Source date ranges")
    date_info = pd.DataFrame({
        "Field": ["Order Date", "Ship Date"],
        "Minimum": [df["Order Date"].min(), df["Ship Date"].min()],
        "Maximum": [df["Order Date"].max(), df["Ship Date"].max()],
    })
    st.dataframe(date_info, use_container_width=True, hide_index=True)

    st.markdown("### Factory mapping coverage")
    mapping = pd.DataFrame({
        "Product": list(PRODUCT_FACTORY.keys()),
        "Factory": list(PRODUCT_FACTORY.values())
    })
    st.dataframe(mapping, use_container_width=True, hide_index=True)

st.sidebar.markdown("---")
st.sidebar.caption("Nassau Candy • Logistics Intelligence")
st.sidebar.caption("Built with Streamlit + Pandas + Plotly")
