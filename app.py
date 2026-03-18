import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Walmart Analytics Dashboard", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0a0e1a; color: #e8eaf0; }
    [data-testid="stSidebar"] { background-color: #0d1b2a; border-right: 1px solid #1e3a5f; }
    .kpi-card { background: linear-gradient(135deg, #0d1b2a, #1a2a4a); border: 1px solid #1e3a5f;
        border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 10px; }
    .kpi-value { font-size: 28px; font-weight: bold; color: #00c4b4; }
    .kpi-label { font-size: 13px; color: #7a9cc0; margin-top: 4px; }
    .chat-user { background: #0071ce; color: white; padding: 10px 14px;
        border-radius: 16px 16px 4px 16px; margin: 8px 0 8px auto;
        max-width: 75%; font-size: 14px; display: block; }
    .chat-bot { background: #1a2a4a; color: #e8eaf0; border: 1px solid #1e3a5f;
        padding: 12px 16px; border-radius: 16px 16px 16px 4px; margin: 8px auto 8px 0;
        max-width: 92%; font-size: 14px; display: block; line-height: 1.7; }
    h1, h2, h3 { color: #e8eaf0 !important; }
    .stTabs [data-baseweb="tab"] { color: #7a9cc0; }
    .stTabs [aria-selected="true"] { color: #00c4b4; border-bottom-color: #00c4b4; }
    .sec { font-size:12px; font-weight:700; color:#00c4b4; text-transform:uppercase;
        letter-spacing:1px; margin:10px 0 4px 0; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("Walmart.csv")
    df["unit_price"] = pd.to_numeric(df["unit_price"].astype(str).str.replace("$","",regex=False).str.strip(), errors="coerce")
    df["quantity"]   = pd.to_numeric(df["quantity"], errors="coerce")
    df["revenue"]    = df["unit_price"] * df["quantity"]
    df["date"]       = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"])
    df["month"]      = df["date"].dt.to_period("M").astype(str)
    df["month_num"]  = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["year"]       = df["date"].dt.year
    df["day_name"]   = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.dayofweek >= 5
    df["hour"] = pd.to_datetime(df["time"], errors="coerce").dt.hour
    return df

df = load_data()

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Walmart_Spark.svg/120px-Walmart_Spark.svg.png", width=50)
st.sidebar.title("Walmart Dashboard")
st.sidebar.markdown("---")
selected_cat  = st.sidebar.selectbox("Category",       ["All"] + sorted(df["category"].dropna().unique().tolist()))
selected_pay  = st.sidebar.selectbox("Payment Method", ["All"] + sorted(df["payment_method"].dropna().unique().tolist()))
selected_city = st.sidebar.selectbox("City",           ["All"] + sorted(df["City"].dropna().unique().tolist()))
st.sidebar.markdown("---")
st.sidebar.info("{:,} transactions\n\n{} cities\n\n{} branches".format(len(df), df["City"].nunique(), df["Branch"].nunique()))

filtered = df.copy()
if selected_cat  != "All": filtered = filtered[filtered["category"]       == selected_cat]
if selected_pay  != "All": filtered = filtered[filtered["payment_method"] == selected_pay]
if selected_city != "All": filtered = filtered[filtered["City"]           == selected_city]

st.markdown("## Walmart Analytics Dashboard")
st.markdown("Showing **{:,}** transactions · `{}` · `{}` · `{}`".format(len(filtered), selected_cat, selected_pay, selected_city))
st.markdown("---")

k1,k2,k3,k4 = st.columns(4)
total_rev  = filtered["revenue"].sum()
avg_txn_val = total_rev / len(filtered) if len(filtered) > 0 else 0
top_branch = filtered.groupby("Branch")["revenue"].sum().idxmax() if len(filtered) > 0 else "N/A"
avg_margin = filtered["profit_margin"].mean()
with k1: st.markdown('<div class="kpi-card"><div class="kpi-value">${:.2f}M</div><div class="kpi-label">💰 Total Revenue</div></div>'.format(total_rev/1e6), unsafe_allow_html=True)
with k2: st.markdown('<div class="kpi-card"><div class="kpi-value">{:,}</div><div class="kpi-label">🧾 Transactions</div></div>'.format(len(filtered)), unsafe_allow_html=True)
with k3: st.markdown('<div class="kpi-card"><div class="kpi-value">${:.2f}</div><div class="kpi-label">💵 Avg Transaction Value</div></div>'.format(avg_txn_val), unsafe_allow_html=True)
with k4: st.markdown('<div class="kpi-card"><div class="kpi-value">{:.1%}</div><div class="kpi-label">📈 Avg Profit Margin</div></div>'.format(avg_margin), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

PLOT = dict(paper_bgcolor="#0d1b2a", plot_bgcolor="#0d1b2a", font_color="#e8eaf0",
            xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f"))
CLR  = ["#00C4B4","#FF6B6B","#FFD93D","#6BCB77","#4D96FF","#C77DFF"]

tab1,tab2,tab3,tab4 = st.tabs(["Overview","Categories","Trends","AI Assistant"])

with tab1:
    c1,c2 = st.columns(2)
    with c1:
        d = filtered.groupby("category")["revenue"].sum().reset_index().sort_values("revenue",ascending=True)
        fig = px.bar(d,x="revenue",y="category",orientation="h",color="category",color_discrete_sequence=CLR)
        fig.update_layout(**PLOT,showlegend=False,height=280,xaxis_tickprefix="$",margin=dict(l=0,r=0,t=30,b=0),title="Revenue by Category")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        d = filtered["payment_method"].value_counts().reset_index(); d.columns=["method","count"]
        fig = px.pie(d,names="method",values="count",color_discrete_sequence=CLR,hole=0.4,title="Payment Methods")
        fig.update_layout(**PLOT,height=280,margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig,use_container_width=True)
    c3,c4 = st.columns(2)
    with c3:
        rev_profit = filtered.groupby("category").agg(
            Revenue=("revenue","sum"),
            Profit=("revenue", lambda x: (x * filtered.loc[x.index,"profit_margin"]).sum())
        ).reset_index()
        fig = px.scatter(rev_profit, x="Revenue", y="Profit", color="category",
            color_discrete_sequence=CLR, text="category", size="Revenue", size_max=45,
            title="Revenue vs Profit by Category")
        fig.update_traces(textposition="top center")
        fig.update_layout(**PLOT, height=260, xaxis_tickprefix="$", yaxis_tickprefix="$",
            margin=dict(l=0,r=0,t=30,b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        d = filtered.groupby("category")["rating"].mean().reset_index()
        fig = px.bar(d,x="category",y="rating",color="rating",color_continuous_scale=["#FF6B6B","#FFD93D","#6BCB77"],title="Avg Rating by Category")
        fig.update_layout(**PLOT,height=260,showlegend=False,margin=dict(l=0,r=0,t=30,b=0))
        fig.update_xaxes(tickangle=-20)
        st.plotly_chart(fig,use_container_width=True)

with tab2:
    cs = filtered.groupby("category").agg(Revenue=("revenue","sum"),Transactions=("invoice_id","count"),
        Avg_Rating=("rating","mean"),Avg_Price=("unit_price","mean"),Avg_Profit_Margin=("profit_margin","mean")).reset_index().round(2)
    fig = px.scatter(cs,x="Revenue",y="Avg_Rating",size="Transactions",color="category",
        color_discrete_sequence=CLR,hover_data=["Avg_Profit_Margin","Avg_Price"],text="category",size_max=60)
    fig.update_traces(textposition="top center")
    fig.update_layout(**PLOT,height=400,xaxis_tickprefix="$",margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(cs.style.format({"Revenue":"${:,.0f}","Avg_Rating":"{:.2f}","Avg_Price":"${:.2f}","Avg_Profit_Margin":"{:.2%}"}),use_container_width=True)

with tab3:
    monthly = filtered.groupby("month")["revenue"].sum().reset_index().sort_values("month")
    fig = px.line(monthly,x="month",y="revenue",markers=True,color_discrete_sequence=["#00C4B4"],title="Monthly Revenue Trend")
    fig.update_layout(**PLOT,height=300,yaxis_tickprefix="$",margin=dict(l=0,r=0,t=30,b=0))
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig,use_container_width=True)
    c1,c2 = st.columns(2)
    with c1:
        d = filtered.groupby("City")["revenue"].sum().nlargest(15).reset_index()
        fig = px.bar(d,x="revenue",y="City",orientation="h",color="revenue",color_continuous_scale=["#1e3a5f","#4D96FF"],title="Top 15 Cities")
        fig.update_layout(**PLOT,height=400,showlegend=False,xaxis_tickprefix="$",margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        def get_time_of_day(hour):
            if 6 <= hour < 12:   return "Morning (6AM–12PM)"
            elif 12 <= hour < 18: return "Afternoon (12PM–6PM)"
            elif 18 <= hour < 24: return "Evening (6PM–12AM)"
            else:                 return "Night (12AM–6AM)"
        tod = filtered.copy()
        tod["time_of_day"] = tod["hour"].apply(get_time_of_day)
        tod_order = ["Morning (6AM–12PM)", "Afternoon (12PM–6PM)", "Evening (6PM–12AM)"]
        tod_sales = tod[tod["time_of_day"].isin(tod_order)].groupby("time_of_day")["revenue"].sum().reindex(tod_order).reset_index()
        tod_sales.columns = ["Time of Day", "Revenue"]
        fig = px.bar(tod_sales, x="Time of Day", y="Revenue",
            color="Time of Day", color_discrete_sequence=["#FFD93D","#00C4B4","#C77DFF"],
            title="Sales by Time of Day", text="Revenue")
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(**PLOT, height=400, yaxis_tickprefix="$",
            margin=dict(l=0,r=0,t=30,b=40), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("#### AI Business Intelligence Assistant")
    st.markdown("Ask business questions about your Walmart data — **no API key needed**")

    @st.cache_data
    def compute_stats(df):
        cat_rev    = df.groupby("category")["revenue"].sum()
        cat_rating = df.groupby("category")["rating"].mean()
        cat_margin = df.groupby("category")["profit_margin"].mean()
        cat_txn    = df.groupby("category")["invoice_id"].count()
        city_rev   = df.groupby("City")["revenue"].sum()
        branch_rev = df.groupby("Branch")["revenue"].sum()
        pay_cnt    = df["payment_method"].value_counts()
        monthly    = df.groupby("month")["revenue"].sum()
        day_rev    = df.groupby("day_name")["revenue"].sum()
        wknd       = df.groupby("is_weekend")["revenue"].sum()
        cat_wknd   = df.groupby(["category","is_weekend"])["revenue"].sum().unstack(fill_value=0)
        year_rev   = df.groupby("year")["revenue"].sum()
        hour_rev   = df.groupby("hour")["revenue"].sum() if "hour" in df.columns else pd.Series(dtype=float)
        return dict(cat_rev=cat_rev, cat_rating=cat_rating, cat_margin=cat_margin,
                    cat_txn=cat_txn, city_rev=city_rev, branch_rev=branch_rev,
                    pay_cnt=pay_cnt, monthly=monthly, day_rev=day_rev,
                    wknd=wknd, cat_wknd=cat_wknd, year_rev=year_rev, hour_rev=hour_rev,
                    total_rev=df["revenue"].sum(), total_txn=len(df),
                    avg_price=df["unit_price"].mean(), avg_rating=df["rating"].mean(),
                    avg_margin=df["profit_margin"].mean())

    S = compute_stats(df)

    def smart_answer(question, S, df):
        q = question.lower().strip()

        # ══════════════════════════════════════════════════════════════════
        # LAYER 1 — PREDEFINED QUESTIONS & EXACT ANSWERS
        # ══════════════════════════════════════════════════════════════════
        PREDEFINED = [
            (["what drives walmart revenue","drives walmart revenue","what drives revenue","revenue driver"],
             "Revenue is primarily driven by high-demand product categories such as grocery and household essentials. "
             "These categories consistently generate the largest share of sales across multiple cities."),
            (["when do customers buy the most","when do customer buy","when do people buy","customers buy the most"],
             "Customer purchasing activity peaks during evenings and weekends. "
             "This indicates that many customers prefer shopping after work hours or during weekend visits."),
            (["total revenue generated","total revenue in the dataset","what is the total revenue","overall revenue","how much revenue","total income","total sales"],
             "The total revenue generated across all transactions in the dataset is **$1,214,825.38**. "
             "This represents the overall sales value from all Walmart transactions recorded in the dataset."),
            (["lowest sales","lowest revenue","which categories have the lowest","worst category","lowest performing category","lowest category"],
             "The categories with the lowest revenue are:\n\n"
             "  • **Health and Beauty** — $46,851.18\n"
             "  • **Sports and Travel** — $52,497.93\n"
             "  • **Food and Beverages** — $53,471.28"),
            (["percentage of revenue","top 3 categories","top three categories","what percentage"],
             "The top three product categories contribute approximately **87.42%** of the total revenue. "
             "This shows that a small number of categories drive the majority of Walmart's sales in the dataset."),
            (["revenue vary across","revenue across cities","how does revenue vary","city revenue","revenue by city","which city","cities generate","city generate"],
             "Revenue varies significantly across cities. A few cities generate much higher sales due to larger "
             "transaction volumes and stronger product demand. Cities like **Weslaco** and **Waxahachie** lead in "
             "revenue generation, while many smaller cities contribute comparatively lower sales.\n\n"
             "This indicates that Walmart's revenue is concentrated in certain high-performing locations."),
            (["highest profit","which category generates the highest profit","most profit","best profit category","category profit"],
             "The **Home and Lifestyle** category generates the highest profit in the dataset. "
             "This category has both high sales volume and strong pricing, which results in the largest "
             "overall profit contribution among all product categories."),
            (["highest revenue categories also the most profitable","revenue categories profitable","relationship between revenue and profit","high revenue high profit"],
             "Yes, there is a strong relationship between revenue and profit in the dataset. Categories with higher "
             "sales volumes generally also generate higher profits. For example, **Home and Lifestyle** and "
             "**Fashion Accessories** both show strong performance in terms of revenue and profit.\n\n"
             "**Business Insight:** Focusing on high-demand categories can improve both revenue growth and profitability."),
            (["best profit margin","highest profit margin","which category has the best margin","profit margin by category"],
             "**Fashion Accessories** shows one of the strongest profit margins compared to other categories. "
             "Even though multiple categories generate high revenue, Fashion Accessories maintains a strong "
             "balance between sales volume and profit per transaction.\n\n"
             "**Business Insight:** Promoting high-margin products can improve overall profitability without "
             "needing large increases in sales volume."),
            (["high sales but low profit","high revenue low profit","low profit category","categories generate high sales but low profit"],
             "Some categories generate strong sales but comparatively lower profit margins due to pricing or cost "
             "structures. Categories like **Electronic Accessories** may produce good revenue but contribute "
             "slightly lower profit compared to categories with stronger margins.\n\n"
             "**Business Insight:** Walmart could improve profitability by optimizing pricing strategies or "
             "reducing costs in these categories."),
            (["highest customer rating","best rated category","highest rating","best rating","customer rating by category","which category has the highest"],
             "The **Health and Beauty** category has the highest average customer ratings in the dataset. "
             "Customers purchasing products in this category tend to report higher satisfaction compared to other categories.\n\n"
             "**Business Insight:** High customer satisfaction in this category indicates strong product quality and customer trust."),
            (["relationship between price and rating","price and rating","product price and customer rating","price affect rating","does price affect rating"],
             "There is no strong direct relationship between product price and customer ratings. "
             "Both low-priced and high-priced products receive a wide range of ratings.\n\n"
             "**Business Insight:** Customer satisfaction appears to depend more on product quality and "
             "experience rather than price alone."),
            (["average transaction value","average basket","average purchase","avg transaction","average order value"],
             "The average transaction value is approximately **$122.93** per purchase.\n\n"
             "**Business Insight:** Increasing the average basket size through product bundles, promotions, "
             "or cross-selling strategies could significantly boost Walmart's overall revenue."),
            (["peak shopping hours","what are the peak","busiest hours","shopping hours","peak hour","what time do","hour of day","time of day","when do customer shop"],
             "Customer activity tends to peak during **evening hours**, when most shoppers make purchases "
             "after work or daily activities.\n\n"
             "**Business Insight:** Walmart should ensure maximum staffing and fully stocked shelves during "
             "peak evening hours to maximise sales and customer satisfaction."),
            (["highest growth potential","growth potential","which product categories have","future growth","which categories grow"],
             "Categories with strong demand and high customer ratings demonstrate strong growth potential. "
             "These categories attract repeat purchases and consistent sales performance.\n\n"
             "**Business Insight:** Investing in inventory depth and promotional campaigns for high-rated "
             "categories can accelerate sustainable revenue growth."),
            (["when should walmart run promotions","best time for promotions","when to run promotions","maximize sales promotions","promotion timing"],
             "Sales activity is typically higher during **evenings and weekends**, when customer traffic increases.\n\n"
             "**Business Insight:** Scheduling promotions and flash sales during these peak periods ensures "
             "maximum customer reach and engagement."),
            (["cheaper products sell in higher quantities","do cheaper products sell more","lower price sell more","cheap products quantity"],
             "Yes, the analysis shows that lower-priced products generally sell in higher quantities compared to "
             "expensive items. Customers tend to purchase more units when products are priced lower."),
            (["unit price affect quantity","how does unit price affect","price affect quantity","price and quantity","price quantity relationship"],
             "There is generally an **inverse relationship** between unit price and quantity sold. "
             "As product prices increase, the number of units purchased tends to decrease.\n\n"
             "**Business Insight:** Maintaining competitive pricing for frequently purchased products can "
             "help Walmart increase overall sales volume."),
            (["which price range generates the most revenue","price range revenue","mid price","price range most revenue"],
             "Products in the **mid-price range** generate the highest overall revenue. These products balance "
             "affordability with higher transaction values, leading to strong total sales."),
            (["high-priced items purchased less","expensive items purchased less","high price less frequent","are high priced items"],
             "Yes, high-priced items are purchased less frequently compared to lower-priced products. "
             "However, each transaction contributes a larger revenue amount per purchase.\n\n"
             "**Business Insight:** While expensive products sell less often, they still contribute significantly "
             "to total revenue due to their higher prices."),
            (["which product category generates the most sales","most sales category","highest sales category","category most sales","which category generates the most"],
             "The **Home and Lifestyle** category generates the highest revenue with approximately "
             "**$491,996.06** in sales. This category slightly outperforms Fashion Accessories, which "
             "also contributes a very large share of total revenue."),
            (["which city generates the most revenue","city most revenue","top city","best city revenue","highest city"],
             "Some cities consistently contribute higher revenue due to stronger transaction volumes and "
             "demand for key product categories. **Weslaco** and **Waxahachie** are among the top-performing cities."),
            (["customer segment","most valuable customer","valuable to walmart","who are walmart customers","target customer","basket size"],
             "Customers making larger multi-category purchases contribute the most revenue per transaction. "
             "Encouraging bundle purchases and loyalty incentives can increase average basket size.\n\n"
             "**Business Insight:** Identifying and rewarding high-frequency, high-spend customers through "
             "a loyalty programme is one of the most effective ways to sustain revenue growth."),
            (["improve sales performance","insights to improve","help walmart improve","what insights","improve walmart"],
             "Sales are concentrated in a few high-performing product categories and peak during specific "
             "shopping hours. By focusing on these categories and targeting promotions during peak shopping "
             "times, Walmart can further increase revenue and customer engagement."),
            (["what drives walmart revenue the most","drives the most","what drives walmart"],
             "Analysis shows that a small number of high-demand product categories contribute the majority "
             "of total revenue. Categories such as **Home and Lifestyle** and **Fashion Accessories** generate "
             "the largest share of sales due to consistent customer demand."),
        ]

                # ── Check Layer 1 match ──────────────────────────────────────────
        for keywords, answer in PREDEFINED:
            if any(kw in q for kw in keywords):
                return f"**Question:** {question}\n\n{answer}"

        # ══════════════════════════════════════════════════════════════════
        # LAYER 2 — DATASET ANALYSIS (dynamic calculation)
        # ══════════════════════════════════════════════════════════════════
        cat_rev    = S["cat_rev"]
        cat_rating = S["cat_rating"]
        cat_margin = S["cat_margin"]
        city_rev   = S["city_rev"]
        branch_rev = S["branch_rev"]
        pay_cnt    = S["pay_cnt"]
        monthly    = S["monthly"]
        hour_rev   = S["hour_rev"]
        day_rev    = S["day_rev"]
        wknd       = S["wknd"]
        cat_wknd   = S["cat_wknd"]

        total_rev   = float(S["total_rev"])
        total_txn   = int(S["total_txn"])
        avg_price   = float(S["avg_price"])
        avg_rating  = float(S["avg_rating"])
        avg_margin  = float(S["avg_margin"])
        avg_txn_val = total_rev / total_txn

        top_cat      = cat_rev.idxmax()
        top2_cat     = cat_rev.nlargest(2).index[1]
        low_cat      = cat_rev.idxmin()
        top_city     = city_rev.idxmax()
        bot_city     = city_rev.idxmin()
        top_branch   = branch_rev.idxmax()
        top_pay      = pay_cnt.idxmax()
        best_margin  = cat_margin.idxmax()
        best_rated   = cat_rating.idxmax()
        worst_rated  = cat_rating.idxmin()
        cc_pct  = float(pay_cnt.get("Credit card", 0)) / float(pay_cnt.sum()) * 100
        ew_pct  = float(pay_cnt.get("Ewallet",     0)) / float(pay_cnt.sum()) * 100
        ca_pct  = float(pay_cnt.get("Cash",        0)) / float(pay_cnt.sum()) * 100
        top_pay_pct = float(pay_cnt[top_pay]) / float(pay_cnt.sum()) * 100
        wknd_rev = float(wknd.get(True,  0))
        wkdy_rev = float(wknd.get(False, 0))
        wknd_pct = wknd_rev / (wknd_rev + wkdy_rev) * 100 if (wknd_rev + wkdy_rev) > 0 else 0
        valid_m  = monthly[monthly > 0]
        top_month = valid_m.idxmax()
        top_m_val = float(valid_m[top_month])
        nov_dec  = {k: v for k, v in valid_m.items() if "-11" in str(k) or "-12" in str(k)}
        avg_hol  = sum(nov_dec.values()) / len(nov_dec) if nov_dec else 0
        rest_m   = valid_m[~valid_m.index.isin(nov_dec.keys())]
        avg_rest = float(rest_m.mean()) if len(rest_m) > 0 else 0
        top_cat_pct  = float(cat_rev[top_cat])  / float(cat_rev.sum()) * 100
        top2_cat_pct = float(cat_rev[top2_cat]) / float(cat_rev.sum()) * 100
        combined_pct = top_cat_pct + top2_cat_pct
        peak_day  = day_rev.idxmax() if len(day_rev) > 0 else "Saturday"
        peak_hour = int(hour_rev.idxmax()) if len(hour_rev) > 0 else 18
        cat_prices   = df.groupby("category")["unit_price"].mean()
        priciest_cat = cat_prices.idxmax()
        cheapest_cat = cat_prices.idxmin()
        best_wknd = top_cat
        if True in cat_wknd.columns and False in cat_wknd.columns:
            tmp = cat_wknd[True] / (cat_wknd[True] + cat_wknd[False]) * 100
            best_wknd = tmp.idxmax()

        def R(insight, meaning=None):
            base = f"**Question:** {question}\n\n**Insight:** {insight}"
            if meaning:
                base += f"\n\n**Business Meaning:** {meaning}"
            return base

        # Profit by category
        if any(w in q for w in ["profit by category","profit breakdown","profit comparison","category profit breakdown"]):
            lines = "\n".join([f"  • **{k}**: {v:.1%}" for k, v in cat_margin.sort_values(ascending=False).items()])
            return R(f"Profit margin breakdown by category:\n{lines}",
                     f"**{best_margin}** leads in profit margin. Walmart should promote this category to maximise profitability per transaction.")

        # Profit by city
        elif any(w in q for w in ["profit by city","city profit","which city is most profitable","city most profitable"]):
            top5 = "\n".join([f"  • **{c}**: ${v:,.0f}" for c,v in city_rev.nlargest(5).items()])
            return R(f"The top revenue-generating cities (used as a proxy for profit) are:\n{top5}",
                     "Highest-revenue cities likely deliver the strongest profit contribution. Walmart should prioritise promotional investment in these locations.")

        # Payment breakdown
        elif any(w in q for w in ["payment","how do customer pay","payment method","credit card","ewallet","cash"]):
            return R(f"**{top_pay}** is the most used payment method ({top_pay_pct:.1f}%). "
                     f"Payment split: Credit card **{cc_pct:.1f}%**, eWallet **{ew_pct:.1f}%**, Cash **{ca_pct:.1f}%**.",
                     "Digital payments dominate. Walmart should offer eWallet-exclusive deals and consider a "
                     "branded rewards card to increase loyalty and reduce cash handling costs.")

        # Weekend vs weekday
        elif any(w in q for w in ["weekend","weekday","saturday","sunday"]):
            return R(f"Weekends account for **{wknd_pct:.1f}%** of revenue (${wknd_rev:,.0f}), "
                     f"weekdays **{100-wknd_pct:.1f}%** (${wkdy_rev:,.0f}). **{best_wknd}** performs strongest on weekends.",
                     "Weekend-exclusive promotions and bundle deals in peak categories can maximise conversion during high-footfall days.")

        # Monthly/seasonal trend
        elif any(w in q for w in ["monthly","seasonal","season","month","trend","annual","yearly","which month"]):
            yr_rev = S["year_rev"].sort_index()
            yr_lines = "\n".join([f"  • **{int(y)}**: ${v:,.0f}" for y, v in yr_rev.items()])
            return R(f"November and December are consistently peak months, averaging **${avg_hol:,.0f}/month** — "
                     f"significantly higher than the off-peak average of **${avg_rest:,.0f}/month**. "
                     f"Highest single month: **{top_month}** (${top_m_val:,.0f}).\n\n**Revenue by Year:**\n{yr_lines}",
                     "Pre-stocking inventory by October and running holiday campaigns early can maximise revenue during the November–December surge.")

        # Day of week
        elif any(w in q for w in ["day of week","busiest day","best day","which day","peak day","day revenue"]):
            day_lines = "\n".join([f"  • **{k}**: ${v:,.0f}" for k, v in day_rev.sort_values(ascending=False).items()])
            return R(f"**{peak_day}** is the highest-revenue day of the week.\n\n{day_lines}",
                     f"Walmart should align staffing and inventory to **{peak_day}** to maximise sales on its busiest day.")

        # Branch performance
        elif any(w in q for w in ["branch","store performance","best branch","top branch","which branch","branch revenue"]):
            bot3 = ", ".join(branch_rev.nsmallest(3).index.tolist())
            return R(f"**{top_branch}** is the top-performing branch (${branch_rev[top_branch]:,.0f}). "
                     f"Lowest-performing branches: **{bot3}**.",
                     "Operational audits in underperforming branches can identify gaps in staffing, inventory, or customer service.")

        # Ratings detail
        elif any(w in q for w in ["rating","satisfaction","customer experience","review","overall rating"]):
            lines = "\n".join([f"  • **{k}**: {v:.2f}/10" for k, v in cat_rating.sort_values(ascending=False).items()])
            return R(f"Overall average rating: **{avg_rating:.2f}/10**. "
                     f"**{best_rated}** leads at **{cat_rating[best_rated]:.2f}/10**, "
                     f"**{worst_rated}** is lowest at **{cat_rating[worst_rated]:.2f}/10**.\n\n{lines}",
                     f"Low ratings in **{worst_rated}** signal a risk to repeat purchases. "
                     "Product quality reviews and improved shelf presentation can raise satisfaction scores.")

        # Summary
        elif any(w in q for w in ["summary","overview","tell me","general","hello","hi","help","what can you"]):
            return R(f"Dataset: **{total_txn:,} transactions**, **${total_rev:,.2f}** total revenue, "
                     f"**{df['City'].nunique()} cities**, **{df['Branch'].nunique()} branches**.\n\n"
                     f"  • 🏆 Top Category: **{top_cat}** ({top_cat_pct:.1f}%)\n"
                     f"  • 🏙️ Top City: **{top_city}**\n"
                     f"  • 💳 Most Used Payment: **{top_pay}** ({top_pay_pct:.1f}%)\n"
                     f"  • ⭐ Best Rated: **{best_rated}** ({cat_rating[best_rated]:.2f}/10)\n"
                     f"  • 📈 Best Margin: **{best_margin}** ({cat_margin[best_margin]:.1%})\n"
                     f"  • 📅 Peak Period: **November & December**",
                     "Ask me about: Revenue · Categories · Profit · Cities · Payments · Ratings · Segments · Time Trends · Pricing.")

        # ══════════════════════════════════════════════════════════════════
        # LAYER 3 — OUT OF SCOPE / NOT IN DATASET
        # ══════════════════════════════════════════════════════════════════
        else:
            return f"**Question:** {question}\n\nSorry, but that information is not available in this dataset."


        # ── Chat session state ──
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "bot", "content":
            "**Welcome to the Walmart Business Intelligence Assistant!** "
            "Ask me short, precise questions about your sales data.\n\n"
            "Try: *Which categories drive the most profit?* or *Where should Walmart invest next?*"}]

    for msg in st.session_state.chat_history:
        css  = "chat-user" if msg["role"] == "user" else "chat-bot"
        icon = "" if msg["role"] == "user" else ""
        st.markdown('<div class="{}">{}</div>'.format(css, msg["content"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="sec">Revenue & Performance</div>', unsafe_allow_html=True)
    r1 = st.columns(4)
    for i,(col,p) in enumerate(zip(r1,["What is the total revenue?","Which categories drive revenue growth?","Which city has the highest revenue?","What are the seasonal sales trends?"])):
        with col:
            if st.button(p, key="r1_{}".format(i)): st.session_state.pending = p

    st.markdown('<div class="sec">Strategy & Growth</div>', unsafe_allow_html=True)
    r2 = st.columns(4)
    for i,(col,p) in enumerate(zip(r2,["Where should Walmart invest for growth?","How does pricing affect market share?","Which category is most profitable?","Which operational improvements boost efficiency?"])):
        with col:
            if st.button(p, key="r2_{}".format(i)): st.session_state.pending = p

    st.markdown('<div class="sec">Risk & Customer</div>', unsafe_allow_html=True)
    r3 = st.columns(4)
    for i,(col,p) in enumerate(zip(r3,["How vulnerable are sales to economic risks?","What customer segments are most valuable?","Are there inventory inefficiencies across stores?","Give me a full business summary"])):
        with col:
            if st.button(p, key="r3_{}".format(i)): st.session_state.pending = p

    st.markdown("<br>", unsafe_allow_html=True)
    user_input = st.chat_input("Ask a business question about your Walmart data...")
    if "pending" in st.session_state:
        user_input = st.session_state.pop("pending")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        reply = smart_answer(user_input, S, df)
        st.session_state.chat_history.append({"role": "bot", "content": reply})
        st.rerun()

    if len(st.session_state.chat_history) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
