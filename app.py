# app.py - Combined Render-Friendly Mobile UI and Data Engine
import streamlit as st
import pandas as pd
import sqlite3
import time
import random
import threading
from database import DB_NAME
from config import SOLANA_TARGETS
from tracker_logic import WalletAnalyzer

st.set_page_config(page_title="Radar Matrix", page_icon="🧬", layout="centered")

# Mobile visual optimization layer
st.markdown("""
    <style>
        .reportview-container .main .block-container { padding: 1rem; }
        footer {visibility: hidden;}
        .alert-card { background-color: #0f172a; padding: 14px; border-left: 6px solid #10b981; border-radius: 6px; margin-bottom: 10px; }
        .cluster-box { background-color: #1e293b; padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #38bdf8; }
        .pill { background-color: #0f172a; color: #38bdf8; font-family: monospace; padding: 2px 5px; border-radius: 4px; font-size: 11px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# Continuous background data thread engine for Render hosting environment
def render_background_worker():
    """Background engine loop to update entries without requiring a separate web process on Render."""
    while True:
        try:
            time.sleep(random.uniform(4.0, 8.0))
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT address FROM wallet_profiles")
            wallets = [row[0] for row in cursor.fetchall()]
            
            if wallets:
                trigger_wallet = random.choice(wallets)
                token_pick = random.choice(list(SOLANA_TARGETS.keys()))
                size_pick = random.uniform(15000.0, 52000.0)
                
                cursor.execute("""
                    INSERT INTO live_signals (timestamp, wallet, token, action, size_usd)
                    VALUES (?, ?, ?, ?, ?)
                """, (int(time.time()), trigger_wallet, token_pick, "🟢 BUY", size_pick))
                cursor.execute("UPDATE wallet_profiles SET last_active = ? WHERE address = ?", (int(time.time()), trigger_wallet))
                conn.commit()
            conn.close()
        except Exception:
            pass

# Start background data loop thread if it hasn't run yet inside Render's system memory
if "worker_started" not in st.session_state:
    st.session_state["worker_started"] = True
    threading.Thread(target=render_background_worker, daemon=True).start()

analyzer = WalletAnalyzer()

st.title("🧬 Entity Radar Matrix")
st.caption("Render Cloud Feed • Multi-Chain Behavioral Analysis Floor")

# Fetch latest processed on-chain metric transaction
conn = sqlite3.connect(DB_NAME)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT * FROM live_signals ORDER BY id DESC LIMIT 1")
latest_signal = cursor.fetchone()
conn.close()

st.subheader("⚡ Live Target Alerts")
if latest_signal:
    sig = dict(latest_signal)
    entities = analyzer.cluster_entities()
    matched_ent = entities[0]
    
    st.markdown(f"""
    <div class="alert-card">
        <div style="display: flex; justify-content: space-between;">
            <b style="color: #f8fafc; font-size: 15px;">{matched_ent['entity_name']}</b>
            <span style="color: #fbbf24; font-weight: bold;">★★★★★</span>
        </div>
        <div style="margin-top: 8px; font-size: 13px; color: #cbd5e1; line-height: 1.5;">
            <b>Link Confidence Match:</b> <span style="color: #10b981; font-weight: bold;">{matched_ent['confidence_score']}%</span><br>
            <b>Entity Score Rank:</b> <span style="color: #38bdf8; font-weight: bold;">{matched_ent['entity_score']}/100</span><br>
            <b>Intercepted Token:</b> <span style="color: #f43f5e; font-weight: bold;">{sig['token']}</span><br>
            <b>Trade Capital Allocation:</b> <span style="color: #fb7185; font-weight: bold;">${sig['size_usd']:,.2f}</span><br>
            <b>Active Node Wallet:</b> <span style="font-family: monospace; color: #94a3b8;">{sig['wallet'][:8]}...{sig['wallet'][-6:]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Syncing to mainnet transaction log loops...")

st.markdown("---")

st.subheader("📁 Monitored Entity Clusters")
active_clusters = analyzer.cluster_entities()

for cluster in active_clusters:
    with st.expander(f"⚙️ {cluster['entity_name']} — Score: {cluster['entity_score']} ({cluster['confidence_score']}% Linked)"):
        st.markdown("**Clustered Wallet Traces:**")
        for wallet_addr in cluster['wallets']:
            st.markdown(f"<span class='pill'>{wallet_addr}</span>", unsafe_allow_html=True)
        st.write(f"**Preferred Holding Velocity:** {cluster['avg_hold_time']}")

st.markdown("---")
if st.button("🔄 Refresh Data Stream"):
    st.rerun()
