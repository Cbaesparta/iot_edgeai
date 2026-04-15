from datetime import datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Jetson AI IoT Dashboard", layout="wide")

st.title("Edge AI Smart Surveillance Dashboard")

backend_base = st.sidebar.text_input("Backend URL", value="http://127.0.0.1:5000")
auto_refresh_sec = st.sidebar.slider("Auto refresh (sec)", min_value=1, max_value=15, value=2)


def fetch_json(path: str):
    try:
        res = requests.get(f"{backend_base}{path}", timeout=3)
        res.raise_for_status()
        return res.json()
    except Exception:
        return None


live_tab, analytics_tab, alerts_tab = st.tabs(["Live View", "Analytics", "Alerts"])

with live_tab:
    st.subheader("Live Camera Stream")
    st.markdown(f"[Open Stream in New Tab]({backend_base}/video)")
    st.components.v1.html(
        f"<img src='{backend_base}/video' width='100%' style='border-radius: 10px; border: 1px solid #333;'/>",
        height=560,
        scrolling=False,
    )

    status = fetch_json("/api/status") or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("FPS", status.get("fps", 0))
    c2.metric("CPU %", status.get("cpu_percent", 0))
    c3.metric("Memory %", status.get("memory_percent", 0))
    c4.metric("Frames", status.get("frame_count", 0))

with analytics_tab:
    st.subheader("Detection Analytics")
    detections = fetch_json("/api/detections") or {"history": [], "latest_counts": {}}

    latest_counts = detections.get("latest_counts", {})
    if latest_counts:
        st.write("Current object counts")
        st.json(latest_counts)

    history = detections.get("history", [])
    if history:
        rows = []
        for item in history:
            ts = item.get("time")
            counts = item.get("counts", {})
            row = {"time": ts, **counts}
            rows.append(row)

        df = pd.DataFrame(rows).fillna(0)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce")
            df = df.sort_values("time")
            plot_df = df.set_index("time")
            st.line_chart(plot_df)
        else:
            st.info("History exists but no timestamps were found.")
    else:
        st.info("No detection history yet.")

with alerts_tab:
    st.subheader("Alerts")
    alerts = fetch_json("/api/alerts") or {"alerts": []}
    data = alerts.get("alerts", [])

    if not data:
        st.success("No alerts yet.")
    else:
        for item in reversed(data[-20:]):
            severity = item.get("severity", "low").upper()
            st.warning(f"[{severity}] {item.get('time')} - {item.get('message')}")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Refresh every {auto_refresh_sec}s")
st.markdown(
    f"""
    <script>
      setTimeout(function() {{
        window.location.reload();
      }}, {auto_refresh_sec * 1000});
    </script>
    """,
    unsafe_allow_html=True,
)
