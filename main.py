import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).with_name("reconnect.db")

st.set_page_config(
    page_title="ReConnect | Campus Lost & Found",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                location TEXT NOT NULL,
                report_date TEXT NOT NULL,
                contact TEXT,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_item(report_type, item_name, category, description, location, report_date, contact):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO items
            (report_type, item_name, category, description, location, report_date, contact, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Open')
        """, (report_type, item_name.strip(), category, description.strip(),
              location.strip(), report_date.isoformat(), contact.strip()))
        conn.commit()

def load_items():
    with get_connection() as conn:
        return pd.read_sql_query(
            """SELECT item_id, report_type, item_name, category, description,
                      location, report_date, status
               FROM items ORDER BY item_id DESC""", conn
        )

def update_status(item_id, status):
    with get_connection() as conn:
        conn.execute("UPDATE items SET status = ? WHERE item_id = ?", (status, int(item_id)))
        conn.commit()

initialize_database()

st.markdown("""
<style>
    .stApp { background: #f5f7fb; }
    .block-container { padding-top: 1.7rem; padding-bottom: 2rem; }
    .hero {
        background: linear-gradient(120deg, #102a43 0%, #1d4e89 100%);
        padding: 2rem 2.2rem; border-radius: 18px; color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 { color: white; font-size: 2.5rem; margin: 0; }
    .hero p { color: #dbeafe; font-size: 1.05rem; margin-bottom: 0; }
    div[data-testid="stMetric"] {
        background: white; padding: 16px; border-radius: 14px;
        border: 1px solid #e5eaf1;
    }
    .small-note { color: #64748b; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

pages = ["Dashboard", "Report Lost", "Report Found", "Search Items", "Manage Records"]
if "nav_target" not in st.session_state:
    st.session_state["nav_target"] = "Dashboard"

with st.sidebar:
    st.markdown("## 🔎 ReConnect")
    st.caption("Smart Campus Lost & Found")
    page = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state["nav_target"]),
        key="navigation",
        label_visibility="visible",
    )
    st.session_state["nav_target"] = page
    st.divider()
    st.caption("Python • Streamlit • SQLite")
    st.caption("Campus project prototype")

items = load_items()
total = len(items)
lost_count = int((items["report_type"] == "Lost").sum()) if total else 0
found_count = int((items["report_type"] == "Found").sum()) if total else 0
open_count = int((items["status"] == "Open").sum()) if total else 0

if page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <h1>Welcome to ReConnect 👋</h1>
      <p>Lost something on campus? Found something? Let's help it get back to its owner.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Reports", total)
    c2.metric("Lost Items", lost_count)
    c3.metric("Found Items", found_count)
    c4.metric("Open Reports", open_count)

    st.subheader("What would you like to do?")
    a, b = st.columns(2)
    with a:
        st.info("### 📌 Report a Lost Item\nTell the campus community what you misplaced.")
        if st.button("Go to Report Lost", use_container_width=True):
            st.session_state["nav_target"] = "Report Lost"
            st.rerun()
    with b:
        st.success("### 🎒 Report a Found Item\nHelp someone recover an item you found.")
        if st.button("Go to Report Found", use_container_width=True):
            st.session_state["nav_target"] = "Report Found"
            st.rerun()

    st.subheader("Recent Reports")
    if items.empty:
        st.info("No reports yet. Add a lost or found item to get started.")
    else:
        display = items.head(5)[["item_id", "report_type", "item_name", "category", "location", "report_date", "status"]]
        st.dataframe(display, use_container_width=True, hide_index=True)

elif page in ("Report Lost", "Report Found"):
    report_type = "Lost" if page == "Report Lost" else "Found"
    st.title("📌 Report a " + report_type + " Item")
    st.write("Enter the details below. Fields marked with * are required.")
    with st.form("report_form", clear_on_submit=True):
        item_name = st.text_input("Item name *", placeholder="e.g. Black wallet, student ID card")
        category = st.selectbox("Category *", [
            "Electronics", "ID Card", "Books & Notes", "Bags", "Clothing",
            "Keys", "Bottle", "Wallet / Purse", "Other"
        ])
        description = st.text_area(
            "Description",
            placeholder="Mention colour or general features. Keep unique identifying details private.",
            height=90,
        )
        location = st.text_input("Campus location *", placeholder="e.g. Library, Block B, Cafeteria")
        report_date = st.date_input(
            "Date " + ("lost" if report_type == "Lost" else "found"),
            value=date.today(),
            max_value=date.today(),
        )
        contact = st.text_input("Contact detail (optional)", placeholder="Email or phone; kept out of public listings")
        submitted = st.form_submit_button("Submit Report", type="primary", use_container_width=True)

    if submitted:
        if not item_name.strip() or not location.strip():
            st.error("Please enter the item name and campus location.")
        else:
            add_item(report_type, item_name, category, description, location, report_date, contact)
            st.success(f"Your {report_type.lower()} item report has been saved successfully!")
            st.balloons()

elif page == "Search Items":
    st.title("🔍 Search Campus Items")
    st.write("Find possible matches by keyword, report type, category, or status.")
    col1, col2, col3 = st.columns(3)
    with col1:
        keyword = st.text_input("Search keyword", placeholder="e.g. bottle, black, library")
    with col2:
        type_filter = st.selectbox("Report type", ["All", "Lost", "Found"])
    with col3:
        status_filter = st.selectbox("Status", ["All", "Open", "Claimed", "Returned"])

    category_filter = st.selectbox("Category", ["All"] + [
        "Electronics", "ID Card", "Books & Notes", "Bags", "Clothing",
        "Keys", "Bottle", "Wallet / Purse", "Other"
    ])

    results = items.copy()
    if keyword.strip() and not results.empty:
        searchable = results[["item_name", "category", "description", "location"]].fillna("").astype(str).agg(" ".join, axis=1)
        results = results[searchable.str.contains(keyword.strip(), case=False, na=False)]
    if type_filter != "All" and not results.empty:
        results = results[results["report_type"] == type_filter]
    if status_filter != "All" and not results.empty:
        results = results[results["status"] == status_filter]
    if category_filter != "All" and not results.empty:
        results = results[results["category"] == category_filter]

    st.caption(f"{len(results)} matching record(s)")
    if results.empty:
        st.info("No matching records found. Try another keyword or filter.")
    else:
        st.dataframe(
            results[["item_id", "report_type", "item_name", "category", "description", "location", "report_date", "status"]],
            use_container_width=True, hide_index=True
        )
    st.warning("For safety, contact details are not shown in public search results. Verify ownership before returning an item.")

elif page == "Manage Records":
    st.title("🗂️ Manage Reports")
    st.write("Review submitted reports and update their status after verification.")
    if items.empty:
        st.info("There are no records to manage yet.")
    else:
        st.dataframe(items, use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("Update item status")
        ids = items["item_id"].tolist()
        selected_id = st.selectbox("Select report ID", ids)
        current_status = items.loc[items["item_id"] == selected_id, "status"].iloc[0]
        statuses = ["Open", "Claimed", "Returned"]
        selected_status = st.selectbox(
            "New status", statuses,
            index=statuses.index(current_status) if current_status in statuses else 0
        )
        if st.button("Save Status", type="primary"):
            update_status(selected_id, selected_status)
            st.success(f"Report #{selected_id} updated to {selected_status}.")
            st.rerun()

st.divider()
st.markdown(
    '<p class="small-note">ReConnect is an academic prototype. Do not publish sensitive contact details or '
    "hand over an item without verifying the claimant's ownership.</p>",
    unsafe_allow_html=True
)
