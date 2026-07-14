# -------------------------
# Displaying the processed data
# -------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import analyse



st.markdown("""
<style>

/* -------------------------------- Main*/
            
.block-container {
    padding-top: 1.5rem !important;
}

/* -------------------------------- Sidebar */
            
[data-testid="stSidebarContent"] {
    padding-top: 0rem !important;
}

[data-testid="stSidebarContent"] h1,
[data-testid="stSidebarContent"] h2,
[data-testid="stSidebarContent"] h3 {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* -------------------------------- Information Boxes (TOP) */
            
div[data-testid="stMetric"] {
    background-color: #0b1620;
    border: 1px solid #1f3344;
    padding: 16px;
    border-radius: 12px;
    color: #6e5c27;
}

div[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 700;
}

/* -------------------------------- GPS Text Map */

.strecke-gps {
    color: white;
    background-color: #0d171f;

    border-top: 1px solid #1f3344;
    border-left: 1px solid #1f3344;
    border-right: 1px solid #1f3344;
    border-bottom: none;

    border-radius: 10px 10px 0 0;

    padding: 12px 16px;

    width: 100%;
    box-sizing: border-box;

    min-height: 48px;

    display: flex;
    align-items: center;

    font-size: 23px;
    font-weight: 600;
}

/* -------------------------------- GPS Map */

div[data-testid="stElementContainer"]:has(iframe) {
    background-color: #0d171f;

    border-top: none;
    border-left: 1px solid #1f3344;
    border-right: 1px solid #1f3344;
    border-bottom: 1px solid #1f3344;

    border-radius: 0 0 10px 10px;

    padding: 0px 12px 12px 12px;

    width: 100%;
    box-sizing: border-box;
}


div[data-testid="stElementContainer"]:has(iframe) iframe {
    display: block;
    width: 100% !important;
    border-radius: 6px;
}
.st-key-drive_box,
.st-key-bme_box{
    background-color: #0b1620;
    border: 1px solid #1f3344;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
}

.st-key-design_box, .st-key-design_box1, .st-key-design_box2{
    background-color: #0b1620;
    border: 1px solid #1f3344;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Telemetrie Dashboard",
    layout="wide",
    page_icon="",
)
st.sidebar.title("Telemetry Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Data"]
)

header1, header2, header3, header4 = st.columns([5, 0.8, 2.5, 2])

with header1:
    if page == "Overview":
        st.header("Overview")
    else:
        st.header("Analysis")
    st.text("Trip analysis and telemetry")

fahrten = analyse.fahrten()



with header2:
    st.markdown(
        "<div style='transform: translateY(28px);font-size:18px;font-weight:600;'>View:</div>",
        unsafe_allow_html=True
    )

#----------------------------------------------------- Choose whether to include all data or only specific data

with header3:
    time_range = st.segmented_control(
        "",
    ["Entire trip", "Short-Term"],
    default="Entire trip"
    )

#----------------------------------------------------- Choose the ride to show

with header4:
    name = st.selectbox(
        "Select trip",
        fahrten.keys(),
        width=200
    )

trip_id = fahrten[name]

if trip_id == 99:
    st.write("Demo Data: All displayed sensor and GPS data is artificially generated for demonstration, testing, and development purposes. They do not represent real-world measurements or actual vehicle trips.")

start = 0
if time_range == "Short-Term":
    dauer = analyse.get_trip_dauer(trip_id)
    if dauer > 2:

        start = st.slider(
            "Select time period",
            min_value=0,
            max_value=dauer - 1,
            value=0,
            step=1
        )

        ende = start + 1
        

        st.write(f"Time period: {start}–{ende} Minuten")

#----------------------------------------------------- Retrieve all data stored in the database

gps_data = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["gps"]
mpu_data = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["mpu"]
bme_data = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["bme"]
time_data = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["time"]
raw_data = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["raw_data"]




st.sidebar.markdown("""
<style>
.sidebar-title {
    font-size: 19px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 8px;
}

.sidebar-box {
    background-color: #0d171f;
    padding: 12px;
    margin: 10px;
    border: 1px solid #1f3344;
    border-radius: 14px;
}

.sidebar-label {
    font-size: 14px;
    font-weight: 600;
    color: white;
    margin-top: 8px;
    margin-bottom: 1px;
}

.sidebar-value {
    font-size: 13px;
    color: #d0d0d0;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    f"""<div class="sidebar-box">
<div class="sidebar-title">Current ride</div>
<div class="sidebar-label">Ride ID</div>
<div style="color: #dcff41;" class="sidebar-value">#{trip_id}</div>
<div class="sidebar-label">Start time</div>
<div class="sidebar-value">{time_data["start"]}</div>
<div class="sidebar-label">End time</div>
<div class="sidebar-value">{time_data["end"]}</div>
<div class="sidebar-label">Duration</div>
<div class="sidebar-value">{time_data["duration"]}</div>
<div class="sidebar-label">Data points</div>
<div class="sidebar-value">GPS: {len(gps_data)} <br>MPU: {len(mpu_data)} <br>BME: {len(bme_data)} </div>

</div>""",
    unsafe_allow_html=True
)

st.sidebar.markdown(
    f"""<div class="sidebar-box">
<div class="sidebar-title">System tatus</div>
<div class="sidebar-value">🟢GPS Status:    OK</div>
<div class="sidebar-value">🟢MPU Status     OK</div>
<div class="sidebar-value">🟢BME Status     OK</div>
</div>""",
    unsafe_allow_html=True
)

#----------------------------------------------------- Page Overview
if page == "Overview":

    avg_speed = gps_data["avg_speed"]
    max_speed = gps_data["max_speed"]
    min_speed = gps_data["min_speed"]
    avg_accuracy = gps_data["gps_accuracy_avg"]
    avg_satellites = gps_data["avg_satellites"]

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Ø Speed", f"{avg_speed:.1f} km/h")
    col2.metric("Max Speed", f"{max_speed:.1f} km/h")
    col3.metric("Min Speed", f"{min_speed:.1f} km/h")
    col4.metric("Ø Satellites", f"{avg_satellites:.0f}")
    col5.metric("Ø Accuracy", f"{avg_accuracy:.1f} m")

    # GPS MAP

    st.markdown("""
<style>
.summary-box {
    background-color: #0d171f;
    border: 1px solid #1f3344;
    border-radius: 10px;
    padding: 18px 20px;
    width: 100%;
}
.summary-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    margin-bottom: 15px;
}
.summary-row_no_margin {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}
.summary-left {
    display: flex;
    flex-direction: row;
}

.summary-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 14px;
    color: #ffffff;
}

.summary-label {
    font-size: 16px;
    color: #d1d5db;
}

.summary-value {
    font-size: 17px;
    font-weight: 700;
}

.summary-divider{
    height:1px;
    background:#2d3748;
    margin:20px 0
}
</style>
""", unsafe_allow_html=True)

    map_col, summary_col = st.columns([1.3, 0.7])

    with summary_col:

        vibration_level = mpu_data["vibration_level"]
        if vibration_level < 100:
            vibration_text = "Very Smooth"
        elif vibration_level < 300:
            vibration_text = "Smooth"
        elif vibration_level < 600:
            vibration_text = "Moderate"
        elif vibration_level < 1000:
            vibration_text = "Rough"
        else:
            vibration_text = "Very Rough"

        time_range_show = f"Short-term Drive {trip_id}"

        html = ""

        icons = {
            "Hard braking": "🛑",
            "Strong acceleration": "🚀",
            "Left turn": "⬅️",
            "Right turn": "➡️",
            "Strong impact": "⚠️"
        }

        html = ""

        for event in mpu_data["last_events"][:5]:
            event_type = event["type"]
            timestamp = event["timestamp"]

            html += f"""<div class="summary-row_no_margin">
    <div class="summary-left">
    <div class="summary-icon">{icons.get(event_type, "❓")}</div>
    <div class="summary-label">{timestamp}</div>
    </div>
    <div class="summary-value">{event_type}</div>
    </div>
    <div class="summary-divider"></div>
    """

        st.markdown(f"""<div class="summary-box">
<div class="summary-title">Driving behavior (MPU)</div>

<div class="summary-row">
<div class="summary-left">
<div class="summary-label">Hard braking</div>
</div>
<div class="summary-value" style="color:#22c55e;">{mpu_data["hard_brake_count"]}</div>
</div>

<div class="summary-row">
<div class="summary-left">
<div class="summary-label">Strong acceleration</div>
</div>
<div class="summary-value" style="color:#f59e0b;">{mpu_data["hard_accel_count"]}</div>
</div>

<div class="summary-row">
<div class="summary-left">
<div class="summary-label">Left turns</div>
</div>
<div class="summary-value" style="color:#38bdf8;">{mpu_data["turn_left_count"]}</div>
</div>

<div class="summary-row_no_margin">
<div class="summary-left">
<div class="summary-label">Right turns</div>
</div>
<div class="summary-value" style="color:#ff5df1;">{mpu_data["turn_right_count"]}</div>
</div>

<div class="summary-divider"></div>

<div class="summary-row">
<div class="summary-left">
<div class="summary-label">Max Impact</div>
</div>
<div class="summary-value" style="color:#bd3d3c;">{mpu_data["max_impact"]:.1f}</div>
</div>

<div class="summary-row">
<div class="summary-left">
<div class="summary-label">Ø Vibration level</div>
</div>
<div class="summary-value" style="color:#22c55e;">{mpu_data["vibration_level"]:.1f}</div>
</div>

<div class="summary-row">
<div class="summary-left">
<div class="summary-label">Ride Comfort</div>
</div>
<div class="summary-value" style="color:#f59e0b;">{vibration_text}</div>
</div>

</div> <br>""", unsafe_allow_html=True)
    
        st.markdown(f"""<div class="summary-box">

<div class="summary-row">
<div class="summary-left">
<div class="summary-title">Events</div>
</div>
<div class="summary-value" style="color:white; text-decoration: underline;">{time_range_show if time_range == "Short-Term" else ""}</div>
</div>

{html}


</div>""", unsafe_allow_html=True) 

    def show_map(gps_data):
        df = pd.DataFrame(gps_data["points"])
        df = df.rename(columns={"long": "lon"})
        df = df.dropna(subset=["lat", "lon"])

        if df.empty:
            st.warning("No GPS data available.")
            return

        center_lat = df.iloc[-1]["lat"]
        center_lon = df.iloc[-1]["lon"]

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=15,
            tiles="OpenStreetMap"
        )

        points = df[["lat", "lon"]].values.tolist()

        folium.PolyLine(
            points,
            weight=5,
            color="blue",
            opacity=0.8
        ).add_to(m)

        folium.Marker(
            points[0],
            tooltip="Start",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)

        folium.Marker(
            points[-1],
            tooltip="Ende",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(m)

        st_folium(
            m,
            height=400,
            use_container_width=True
        )

    with map_col:
        st.markdown(
            """
            <div class="strecke-gps">
                GPS-Route
            </div>
            """,
            unsafe_allow_html=True
        )

        show_map(gps_data)

        graph1, graph2 = st.columns([1, 1])

#----------------------------------------------------- Speed Graph
        with graph1:
            speed_length = min(
                len(raw_data["timestamp_gps"]),
                len(raw_data["speed"])
            )

            speed_timestamps = raw_data["timestamp_gps"][:speed_length]
            speed_values = raw_data["speed"][:speed_length]

            fig_speed = px.line(
                x=speed_timestamps,
                y=speed_values,
                title="Speed over time",
                labels={
                    "x": "Time",
                    "y": "Speed (km/h)"
                }
            )

            fig_speed.update_traces(
                line=dict(
                    color="#4da3ff",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Speed:</b> %{y:.1f} km/h"
                    "<extra></extra>"
                )
            )

            fig_speed.update_layout(
                height=380,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Speed over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

            fig_speed.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

            fig_speed.update_yaxes(
                title="Speed (km/h)",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

            st.plotly_chart(
                fig_speed,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )

#----------------------------------------------------- Vibration Graph
        with graph2:
            vib_data = raw_data.get("vib", [])

            vib_timestamps = [
                point.get("timestamp")
                for point in vib_data
                if point.get("timestamp") is not None
                and point.get("impact") is not None
            ]

            vib_impacts = [
                point.get("impact")
                for point in vib_data
                if point.get("timestamp") is not None
                and point.get("impact") is not None
            ]

            vib_length = min(
                len(vib_timestamps),
                len(vib_impacts)
            )

            vib_timestamps = vib_timestamps[:vib_length]
            vib_impacts = vib_impacts[:vib_length]

            fig_vib = px.line(
                x=vib_timestamps,
                y=vib_impacts,
                title="Vibration over time",
                labels={
                    "x": "Time",
                    "y": "Impact"
                }
            )

            fig_vib.update_traces(
                line=dict(
                    color="#ff9f43",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Impact:</b> %{y:.1f}"
                    "<extra></extra>"
                )
            )

            fig_vib.update_layout(
                height=380,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Vibration over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

            fig_vib.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

            fig_vib.update_yaxes(
                title="Impact",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

            st.plotly_chart(
                fig_vib,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )

    left_col, right_col = st.columns([2, 1])

    with left_col:
        drive_box = st.container(key="drive_box")

        with drive_box:
            time_standing = round(gps_data["time_standing"])
            time_moving = round(gps_data["time_moving"])
            distance_m = float(gps_data.get("distance_total", 0))
            height_sea_lvl = round(gps_data["avg_height"])

            if distance_m >= 1000:
                distance_text = f"{distance_m / 1000:.2f} km"
            else:
                distance_text = f"{distance_m:.1f} m"

            st.subheader("Driving stats")

            stat1, stat2, stat3, stat4, stat5 = st.columns([2,2,3,3,3])

            with stat1:
                st.write("Distance")
                st.write(distance_text)

            with stat2:
                st.write("Travel time")
                st.write(time_data["duration"])

            with stat3:
                st.write(f"Time moving: **{time_moving}%**")
                st.progress(time_moving)

            with stat4:
                st.write(f"Time standing: **{time_standing}%**")
                st.progress(time_standing)

            with stat5:
                st.write("Height above sea level")
                st.write(f"{height_sea_lvl} m")

    with right_col:
        bme_box = st.container(key="bme_box")

        with bme_box:
            st.subheader("Environmental data")

            bem1, bme2, bme3 = st.columns([2,2,2])

            with bem1:
                st.write("Temperature")
                st.write(f"{bme_data["avg_temp"]:.1f}")

            with bme2:
                st.write("Pressure")
                st.write(f"{bme_data["avg_press"]:.1f}")

            with bme3:
                st.write("Humidity")
                st.write(f"{bme_data["avg_humidity"]:.1f}")


#----------------------------------------------------- Page Data
else: 
    #----------------------------------------------------- Retrieve all raw data stored in the database

    raw_data_gps = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["all_data"]["gps"]
    raw_data_mpu = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["all_data"]["mpu"]
    raw_data_bme = analyse.analyse(term="short" if time_range == "Short-Term" else "full", minute=start, tripid=trip_id)["all_data"]["bme"]

    dataframe, graph = st.columns([2,1])
    
    with dataframe:

        design_box1 = st.container(key="design_box")
        design_box2 = st.container(key="design_box1")
        design_box3 = st.container(key="design_box2")

        with design_box1:
            st.subheader("GPS Data")
            st.dataframe(
                raw_data_gps,
                use_container_width=True,
                height=300
            )
            st.caption(f"Showing {len(raw_data_gps)} entries")

        
        with design_box2:
            st.subheader("MPU Data")
            st.dataframe(
                raw_data_mpu,
                use_container_width=True,
                height=300
            )
            st.caption(f"Showing {len(raw_data_mpu)} entries")
        with design_box3:
            st.subheader("BME Data")
            st.dataframe(
                raw_data_bme,
                use_container_width=True,
                height=300
            )
            st.caption(f"Showing {len(raw_data_bme)} entries")

    with graph:
#----------------------------------------------------- First Graph
        speed_length = min(
            len(raw_data["timestamp_gps"]),
            len(raw_data["speed"])
            )

        speed_timestamps = raw_data["timestamp_gps"][:speed_length]
        speed_values = raw_data["speed"][:speed_length]

        fig_speed = px.line(
                x=speed_timestamps,
                y=speed_values,
                title="Speed over time",
                labels={
                    "x": "Time",
                    "y": "Speed (km/h)"
                }
            )

        fig_speed.update_traces(
                line=dict(
                    color="#f71212",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Speed:</b> %{y:.1f} km/h"
                    "<extra></extra>"
                )
            )

        fig_speed.update_layout(
                height=260,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Speed over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

        fig_speed.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

        fig_speed.update_yaxes(
                title="Speed (km/h)",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

        st.plotly_chart(
                fig_speed,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )
        
#----------------------------------------------------- Second Graph

        timestamps = [d["timestamp"] for d in raw_data_gps]
        heights = [d["height"] for d in raw_data_gps]

        fig_height = px.line(
                x=timestamps,
                y=heights,
                title="Height (sea level) over time",
                labels={
                    "x": "Time",
                    "y": "Height (m)"
                }
            )

        fig_height.update_traces(
                line=dict(
                    color="#94ff3c",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Height:</b> %{y:.1f} m"
                    "<extra></extra>"
                )
            )

        fig_height.update_layout(
                height=260,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Height (sea level) over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

        fig_height.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

        fig_height.update_yaxes(
                title="Height (m)",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

        st.plotly_chart(
                fig_height,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )

#----------------------------------------------------- Third Graph (MPU)

        vib_data = raw_data.get("vib", [])

        vib_timestamps = [
                point.get("timestamp")
                for point in vib_data
                if point.get("timestamp") is not None
                and point.get("impact") is not None
            ]

        vib_impacts = [
                point.get("impact")
                for point in vib_data
                if point.get("timestamp") is not None
                and point.get("impact") is not None
            ]

        vib_length = min(
                len(vib_timestamps),
                len(vib_impacts)
            )

        vib_timestamps = vib_timestamps[:vib_length]
        vib_impacts = vib_impacts[:vib_length]

        fig_vib = px.line(
                x=vib_timestamps,
                y=vib_impacts,
                title="Vibration over time",
                labels={
                    "x": "Time",
                    "y": "Impact"
                }
            )

        fig_vib.update_traces(
                line=dict(
                    color="#ff9f43",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Impact:</b> %{y:.1f}"
                    "<extra></extra>"
                )
            )

        fig_vib.update_layout(
                height=260,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Vibration over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

        fig_vib.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

        fig_vib.update_yaxes(
                title="Impact",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

        st.plotly_chart(
                fig_vib,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )

#----------------------------------------------------- Fourth Graph (MPU)

        timestamps = [d["timestamp"] for d in raw_data_mpu]
        ax = [d["ax"] for d in raw_data_mpu]

        fig_ax = px.line(
                x=timestamps,
                y=ax,
                title="Ax",
                labels={
                    "x": "X",
                    "y": "x"
                }
            )

        fig_ax.update_traces(
                line=dict(
                    color="#d83cff",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Ax:</b> %{y:.1f}"
                    "<extra></extra>"
                )
            )

        fig_ax.update_layout(
                height=120,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Ax over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

        fig_ax.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

        fig_ax.update_yaxes(
                title="Ax",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

        st.plotly_chart(
                fig_ax,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )

#----------------------------------------------------- Fifth Graph (MPU)

        timestamps = [d["timestamp"] for d in raw_data_mpu]
        ay = [d["ay"] for d in raw_data_mpu]

        fig_ay = px.line(
                x=timestamps,
                y=ay,
                title="Ax",
                labels={
                    "x": "X",
                    "y": "x"
                }
            )

        fig_ay.update_traces(
                line=dict(
                    color="#d83cff",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Ay:</b> %{y:.1f}"
                    "<extra></extra>"
                )
            )

        fig_ay.update_layout(
                height=120,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Ay over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

        fig_ay.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

        fig_ay.update_yaxes(
                title="Ay",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

        st.plotly_chart(
                fig_ay,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )

#----------------------------------------------------- Sixth Graph (MPU)

        timestamps = [d["timestamp"] for d in raw_data_mpu]
        az = [d["az"] for d in raw_data_mpu]

        fig_az = px.line(
                x=timestamps,
                y=az,
                title="Az",
                labels={
                    "x": "X",
                    "y": "x"
                }
            )

        fig_az.update_traces(
                line=dict(
                    color="#d83cff",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Az:</b> %{y:.1f}"
                    "<extra></extra>"
                )
            )

        fig_az.update_layout(
                height=120,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Az over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

        fig_az.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

        fig_az.update_yaxes(
                title="Az",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

        st.plotly_chart(
                fig_az,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )

#----------------------------------------------------- Seventh Graph (MPU)

        timestamps = [d["timestamp"] for d in raw_data_mpu]
        gz = [d["gz"] for d in raw_data_mpu]

        fig_gz = px.line(
                x=timestamps,
                y=gz,
                title="Gz",
                labels={
                    "x": "X",
                    "y": "x"
                }
            )

        fig_gz.update_traces(
                line=dict(
                    color="#d83cff",
                    width=3
                ),
                hovertemplate=(
                    "<b>Time:</b> %{x}<br>"
                    "<b>Gz:</b> %{y:.1f}"
                    "<extra></extra>"
                )
            )

        fig_gz.update_layout(
                height=120,
                template="plotly_dark",
                plot_bgcolor="#0d171f",
                paper_bgcolor="#0d171f",
                font=dict(color="white"),
                title=dict(
                    text="Gz over time",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=55,
                    b=20
                )
            )

        fig_gz.update_xaxes(
                title="Time",
                showgrid=False,
                showline=True,
                linecolor="#2d3e50"
            )

        fig_gz.update_yaxes(
                title="Gz",
                gridcolor="#2d3e50",
                zeroline=False,
                rangemode="tozero"
            )

        st.plotly_chart(
                fig_gz,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True
                }
            )