import re
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st



# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Swim Records Explorer",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

px.defaults.template = "plotly_white"


# ============================================================
# FILE PATHS
# ============================================================

TOP_FILE = Path("Swimming_database_REAL.xlsx")
WR_FILE = Path("world_records_swimming.xlsx")


# ============================================================
# COLORS
# ============================================================

NAVY = "#052B44"
BLUE = "#0A6C9F"
AQUA = "#22B8CF"
LIGHT_AQUA = "#E8F8FB"
GOLD = "#D6A937"
GREY = "#D9E2EC"
DARK_GREY = "#52616B"
RED = "#D64545"

COURSE_COLORS = {
    "LC": BLUE,
    "SC": AQUA
}

GENDER_COLORS = {
    "Men": BLUE,
    "Women": "#C65BAA",
    "Mixed": GOLD,
    "Unknown": DARK_GREY
}


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        background-color: #F7FBFD;
    }

    .hero {
        padding: 34px 38px;
        border-radius: 24px;
        background: linear-gradient(135deg, #052B44 0%, #0A6C9F 48%, #22B8CF 100%);
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(5,43,68,0.18);
    }

    .hero h1 {
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 19px;
        opacity: 0.95;
        max-width: 950px;
        line-height: 1.45;
    }

    .section-title {
        color: #052B44;
        font-size: 28px;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 6px;
    }

    .section-subtitle {
        color: #52616B;
        font-size: 16px;
        margin-bottom: 18px;
        line-height: 1.45;
    }

    .kpi-card {
        background-color: white;
        padding: 22px 22px;
        border-radius: 20px;
        border: 1px solid #E4EEF3;
        box-shadow: 0 6px 20px rgba(5,43,68,0.06);
        min-height: 130px;
    }

    .kpi-label {
        font-size: 13px;
        text-transform: uppercase;
        color: #52616B;
        font-weight: 700;
        letter-spacing: 0.06em;
    }

    .kpi-value {
        font-size: 34px;
        color: #052B44;
        font-weight: 850;
        margin-top: 8px;
    }

    .kpi-note {
        font-size: 13px;
        color: #52616B;
        margin-top: 5px;
    }

    .info-box {
        background-color: white;
        border-left: 6px solid #22B8CF;
        border-radius: 16px;
        padding: 18px 20px;
        margin: 16px 0;
        box-shadow: 0 6px 20px rgba(5,43,68,0.05);
    }

    .warning-box {
        background-color: #FFF8E6;
        border-left: 6px solid #D6A937;
        border-radius: 16px;
        padding: 18px 20px;
        margin: 16px 0;
    }

    .small-caption {
        font-size: 13px;
        color: #52616B;
        line-height: 1.4;
    }

    div[data-testid="stMetricValue"] {
        color: #052B44;
    }

    div[data-testid="stSidebar"] {
        background-color: #EFF8FB;
    }

    /* ============================================================
       TOP NAVIGATION - OLYMPIC SWIMMING POOL
    ============================================================ */

    .block-container {
        padding-top: 1.2rem;
    }

    .pool-nav-shell {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(247, 251, 253, 0.92);
        backdrop-filter: blur(16px);
        border: 1px solid #D8ECF4;
        border-radius: 26px;
        padding: 18px 20px 20px 20px;
        margin-bottom: 28px;
        box-shadow: 0 12px 34px rgba(5,43,68,0.10);
    }

    .pool-nav-top {
        display: flex;
        justify-content: space-between;
        align-items: end;
        gap: 16px;
        margin-bottom: 14px;
    }

    .pool-brand {
        color: #052B44;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.05;
    }

    .pool-subtitle {
        color: #52616B;
        font-size: 13px;
        font-weight: 650;
        text-align: right;
        max-width: 420px;
        line-height: 1.35;
    }

    .pool-grid {
        display: grid;
        grid-template-columns: repeat(8, minmax(86px, 1fr));
        gap: 9px;
    }

    .pool-lane {
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: end;
        min-height: 104px;
        padding: 12px 10px;
        border-radius: 18px;
        overflow: hidden;
        text-decoration: none !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.72);
        box-shadow:
            inset 3px 0 0 rgba(255,255,255,0.70),
            inset -3px 0 0 rgba(255,255,255,0.70),
            0 8px 18px rgba(5,43,68,0.10);
        background:
            linear-gradient(90deg,
                rgba(255,255,255,0.72) 0px,
                rgba(255,255,255,0.72) 2px,
                transparent 2px,
                transparent calc(100% - 2px),
                rgba(255,255,255,0.72) calc(100% - 2px),
                rgba(255,255,255,0.72) 100%
            ),
            radial-gradient(circle at 18% 22%, rgba(255,255,255,0.35) 0 2px, transparent 3px 15px),
            radial-gradient(circle at 70% 38%, rgba(255,255,255,0.25) 0 2px, transparent 3px 18px),
            linear-gradient(180deg, #6EDAF0 0%, #21A7D0 48%, #087CAD 100%);
        background-size: 100% 100%, 32px 24px, 38px 29px, 100% 100%;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }

    .pool-lane::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: 1;
        background:
            linear-gradient(180deg,
                rgba(5,43,68,0.88) 0%,
                rgba(10,108,159,0.75) 52%,
                rgba(34,184,207,0.58) 100%
            );
        transform: scaleY(0);
        transform-origin: top;
        transition: transform 0.34s ease;
    }

    .pool-lane::after {
        content: "🏊";
        position: absolute;
        top: 6px;
        left: 50%;
        z-index: 3;
        font-size: 25px;
        opacity: 0;
        transform: translateX(-50%) translateY(-35px) rotate(90deg);
        transition:
            transform 0.58s cubic-bezier(.2,.85,.2,1),
            opacity 0.18s ease;
        filter: drop-shadow(0 4px 6px rgba(5,43,68,0.35));
    }

    .pool-lane:hover {
        transform: translateY(-4px);
        border-color: #FFFFFF;
        box-shadow:
            inset 3px 0 0 rgba(255,255,255,0.86),
            inset -3px 0 0 rgba(255,255,255,0.86),
            0 16px 32px rgba(5,43,68,0.20);
    }

    .pool-lane:hover::before {
        transform: scaleY(1);
    }

    .pool-lane:hover::after {
        opacity: 1;
        transform: translateX(-50%) translateY(56px) rotate(90deg);
    }

    .pool-lane.active {
        border: 2px solid #D6A937;
        box-shadow:
            inset 3px 0 0 rgba(255,255,255,0.90),
            inset -3px 0 0 rgba(255,255,255,0.90),
            0 16px 34px rgba(214,169,55,0.28);
    }

    .pool-lane.active::before {
        transform: scaleY(1);
        background:
            linear-gradient(180deg,
                rgba(5,43,68,0.94) 0%,
                rgba(10,108,159,0.84) 55%,
                rgba(214,169,55,0.68) 100%
            );
    }

    .pool-lane.active::after {
        content: "🏊";
        opacity: 1;
        transform: translateX(-50%) translateY(56px) rotate(90deg);
    }

    .lane-number,
    .lane-label,
    .lane-tag {
        position: relative;
        z-index: 2;
        display: block;
        text-shadow: 0 2px 8px rgba(5,43,68,0.34);
    }

    .lane-number {
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.88;
        margin-bottom: 4px;
    }

    .lane-label {
        font-size: 15px;
        font-weight: 900;
        line-height: 1.05;
    }

    .lane-tag {
        font-size: 10.5px;
        font-weight: 650;
        opacity: 0.86;
        margin-top: 5px;
        line-height: 1.15;
    }

    .current-lane {
        margin-top: 12px;
        color: #52616B;
        font-size: 13px;
        text-align: center;
        font-weight: 600;
    }

    .current-lane b {
        color: #052B44;
    }

    @media (max-width: 1150px) {
        .pool-grid {
            grid-template-columns: repeat(4, minmax(120px, 1fr));
        }

        .pool-lane {
            min-height: 92px;
        }
    }

    @media (max-width: 650px) {
        .pool-nav-top {
            flex-direction: column;
            align-items: flex-start;
        }

        .pool-subtitle {
            text-align: left;
        }

        .pool-grid {
            grid-template-columns: repeat(2, minmax(120px, 1fr));
        }
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clean_text(value):
    """Clean text values, including common mojibake like Â."""
    if pd.isna(value):
        return ""
    value = str(value)
    value = value.replace("Â", "")
    value = value.replace("\xa0", " ")
    value = value.replace("Ã©", "é")
    value = value.replace("Ã¨", "è")
    value = value.replace("Ã¶", "ö")
    value = value.replace("Ã¼", "ü")
    value = value.replace("Ã¡", "á")
    value = value.replace("Ã­", "í")
    value = value.replace("Ã³", "ó")
    value = value.replace("Ã£", "ã")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def snake_case(col):
    """Convert any column name to snake_case."""
    col = str(col)
    col = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", col)
    col = re.sub(r"[^0-9a-zA-Z]+", "_", col)
    col = col.strip("_").lower()
    return col


def format_time(seconds):
    """Format swimming seconds into mm:ss.xx or ss.xx."""
    if pd.isna(seconds):
        return ""
    try:
        seconds = float(seconds)
    except Exception:
        return ""

    if seconds >= 60:
        minutes = int(seconds // 60)
        sec = seconds - minutes * 60
        return f"{minutes}:{sec:05.2f}"
    return f"{seconds:.2f}"


def time_to_seconds(value):
    """Convert different time formats into seconds."""
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    s = clean_text(value).replace(",", ".")

    if not s:
        return np.nan

    parts = s.split(":")

    try:
        if len(parts) == 3:
            h = float(parts[0])
            m = float(parts[1])
            sec = float(parts[2])
            return h * 3600 + m * 60 + sec
        if len(parts) == 2:
            m = float(parts[0])
            sec = float(parts[1])
            return m * 60 + sec
        return float(s)
    except Exception:
        return np.nan


def parse_any_date(value):
    """Parse date values, including Excel serial dates and text dates."""
    if pd.isna(value):
        return pd.NaT

    if isinstance(value, pd.Timestamp):
        return value

    if isinstance(value, (int, float, np.integer, np.floating)):
        if value > 20000:
            return pd.to_datetime("1899-12-30") + pd.to_timedelta(float(value), unit="D")
        return pd.NaT

    s = clean_text(value)
    if not s:
        return pd.NaT

    date_1 = pd.to_datetime(s, errors="coerce", dayfirst=True)
    if not pd.isna(date_1):
        return date_1

    return pd.to_datetime(s, errors="coerce")


def normalize_gender(value):
    s = clean_text(value).lower()

    if s in ["m", "men", "male", "man"]:
        return "Men"
    if s in ["f", "women", "woman", "female"]:
        return "Women"
    if "mixed" in s:
        return "Mixed"
    return "Unknown"


def normalize_course(value):
    s = clean_text(value).upper()

    if s in ["LC", "LCM", "LONG COURSE", "LONG COURSE METERS"]:
        return "LC"
    if s in ["SC", "SCM", "SHORT COURSE", "SHORT COURSE METERS"]:
        return "SC"
    if "LCM" in s or "LONG" in s:
        return "LC"
    if "SCM" in s or "SHORT" in s:
        return "SC"
    return "Unknown"


def parse_distance_from_text(text):
    s = clean_text(text)
    match = re.search(r"\b(4x50|4x100|4x200|50|100|200|400|800|1500)\b", s)
    if match:
        return match.group(1)
    return ""


def parse_stroke_from_text(text):
    s = clean_text(text).lower()

    if "freestyle" in s:
        return "Freestyle"
    if "backstroke" in s:
        return "Backstroke"
    if "breaststroke" in s:
        return "Breaststroke"
    if "butterfly" in s:
        return "Butterfly"
    if "medley" in s:
        return "Medley"
    return "Unknown"


def first_existing_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def plotly_clean_layout(fig, height=480, title=None):
    fig.update_layout(
        height=height,
        title=title,
        title_font=dict(size=22, color=NAVY),
        font=dict(family="Arial", size=13, color=NAVY),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=30, r=30, t=70, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E7EEF2", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E7EEF2", zeroline=False)
    return fig


def card(label, value, note=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section(title, subtitle=""):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def safe_unique(series):
    if series is None:
        return []
    return sorted([x for x in series.dropna().unique().tolist() if clean_text(x) != ""])


def apply_common_filters(df, gender=True, course=True, stroke=True, distance=True, key_prefix=""):
    filtered = df.copy()

    with st.sidebar:
        st.markdown("### Filters")

        if gender and "gender" in filtered.columns:
            genders = safe_unique(filtered["gender"])
            selected_gender = st.multiselect(
                "Gender",
                genders,
                default=genders,
                key=f"{key_prefix}_gender"
            )
            filtered = filtered[filtered["gender"].isin(selected_gender)]

        if course and "course" in filtered.columns:
            courses = safe_unique(filtered["course"])
            selected_course = st.multiselect(
                "Course",
                courses,
                default=courses,
                key=f"{key_prefix}_course"
            )
            filtered = filtered[filtered["course"].isin(selected_course)]

        if stroke and "stroke" in filtered.columns:
            strokes = safe_unique(filtered["stroke"])
            selected_stroke = st.multiselect(
                "Stroke",
                strokes,
                default=strokes,
                key=f"{key_prefix}_stroke"
            )
            filtered = filtered[filtered["stroke"].isin(selected_stroke)]

        if distance and "distance" in filtered.columns:
            distances = safe_unique(filtered["distance"])
            selected_distance = st.multiselect(
                "Distance",
                distances,
                default=distances,
                key=f"{key_prefix}_distance"
            )
            filtered = filtered[filtered["distance"].isin(selected_distance)]

    return filtered


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_world_records():
    if not WR_FILE.exists():
        return pd.DataFrame()

    df = pd.read_excel(WR_FILE)
    df.columns = [snake_case(c) for c in df.columns]

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(clean_text)

    if "seconds" not in df.columns:
        time_col = first_existing_column(df, ["time", "swim_time", "duration"])
        if time_col:
            df["seconds"] = df[time_col].apply(time_to_seconds)
        else:
            df["seconds"] = np.nan
    else:
        df["seconds"] = pd.to_numeric(df["seconds"], errors="coerce")

    if "time" not in df.columns:
        df["time"] = df["seconds"].apply(format_time)
    else:
        df["time"] = df["time"].fillna(df["seconds"].apply(format_time))

    if "date" in df.columns:
        df["date"] = df["date"].apply(parse_any_date)
    else:
        df["date"] = pd.NaT

    df["year"] = df["date"].dt.year

    if "gender" in df.columns:
        df["gender"] = df["gender"].apply(normalize_gender)
    else:
        df["gender"] = "Unknown"

    if "course" in df.columns:
        df["course"] = df["course"].apply(normalize_course)
    else:
        df["course"] = "Unknown"

    if "distance" in df.columns:
        df["distance"] = df["distance"].astype(str).str.replace(".0", "", regex=False)
    else:
        df["distance"] = df.get("event", "").apply(parse_distance_from_text)

    if "stroke" not in df.columns:
        df["stroke"] = df.get("event", "").apply(parse_stroke_from_text)

    if "name" not in df.columns:
        df["name"] = ""

    if "nationality" not in df.columns:
        df["nationality"] = "Unknown"

    if "meet" not in df.columns:
        df["meet"] = ""

    if "location" not in df.columns:
        df["location"] = ""

    if "is_current" in df.columns:
        df["is_current_bool"] = (
            df["is_current"]
            .astype(str)
            .str.lower()
            .str.strip()
            .isin(["true", "1", "yes", "current"])
        )
    elif "iscurrent" in df.columns:
        df["is_current_bool"] = (
            df["iscurrent"]
            .astype(str)
            .str.lower()
            .str.strip()
            .isin(["true", "1", "yes", "current"])
        )
    else:
        df["is_current_bool"] = False

    df["event_label"] = (
        df["gender"].astype(str)
        + " "
        + df["distance"].astype(str)
        + "m "
        + df["stroke"].astype(str)
        + " ("
        + df["course"].astype(str)
        + ")"
    )

    df = df.sort_values(["event_label", "date", "seconds"], ascending=[True, True, True])

    return df


@st.cache_data
def load_top_performances():
    if not TOP_FILE.exists():
        return pd.DataFrame()

    df = pd.read_excel(TOP_FILE)
    df.columns = [snake_case(c) for c in df.columns]

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(clean_text)

    desc_col = first_existing_column(df, ["event_description", "event_name", "event"])

    time_col = first_existing_column(df, ["swim_time", "seconds", "time_seconds", "duration"])
    if time_col:
        df["time_seconds"] = df[time_col].apply(time_to_seconds)
    else:
        df["time_seconds"] = np.nan

    date_col = first_existing_column(df, ["swim_date", "date"])
    if date_col:
        df["date"] = df[date_col].apply(parse_any_date)
    else:
        df["date"] = pd.NaT

    df["year"] = df["date"].dt.year

    if "rank_order" in df.columns:
        df["rank"] = pd.to_numeric(df["rank_order"], errors="coerce")
    elif "rank" in df.columns:
        df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    else:
        df["rank"] = np.nan

    if "athlete_full_name" in df.columns:
        df["athlete"] = df["athlete_full_name"]
    elif "name" in df.columns:
        df["athlete"] = df["name"]
    else:
        df["athlete"] = ""

    if "team_name" not in df.columns:
        df["team_name"] = ""

    if "team_code" not in df.columns:
        df["team_code"] = ""

    if "city" not in df.columns:
        df["city"] = ""

    if "country_code" not in df.columns:
        df["country_code"] = ""

    if "gender" in df.columns:
        df["gender"] = df["gender"].apply(normalize_gender)
    else:
        df["gender"] = df[desc_col].apply(normalize_gender) if desc_col else "Unknown"

    if desc_col:
        df["distance"] = df[desc_col].apply(parse_distance_from_text)
        df["stroke"] = df[desc_col].apply(parse_stroke_from_text)
        df["course"] = df[desc_col].apply(lambda x: "LC" if "LCM" in clean_text(x).upper() else "SC" if "SCM" in clean_text(x).upper() else "Unknown")
        df["event_label"] = df[desc_col]
    else:
        df["distance"] = ""
        df["stroke"] = "Unknown"
        df["course"] = "Unknown"
        df["event_label"] = "Unknown event"

    df["time_label"] = df["time_seconds"].apply(format_time)

    df = df.sort_values(["event_label", "rank", "time_seconds"], ascending=[True, True, True])

    return df


wr = load_world_records()
top = load_top_performances()


# ============================================================
# DATA CHECK
# ============================================================

missing_files = []

if wr.empty:
    missing_files.append(str(WR_FILE))

if top.empty:
    missing_files.append(str(TOP_FILE))

if missing_files:
    st.error(
        "Missing or unreadable file(s): "
        + ", ".join(missing_files)
        + ". Put the Excel files in the same folder as app.py."
    )
    st.stop()


# ============================================================
# TOP NAVIGATION - SWIMMING POOL LANES
# ============================================================

PAGES = [
    "Home",
    "World Record Timeline",
    "Current World Records",
    "All-Time Top 200 Rankings",
    "Athletes Hall of Fame",
    "Nations & Places",
    "Compare Events",
    "Data & Methods"
]

PAGE_LABELS = {
    "Home": "Home",
    "World Record Timeline": "Timeline",
    "Current World Records": "Records",
    "All-Time Top 200 Rankings": "Top 200",
    "Athletes Hall of Fame": "Athletes",
    "Nations & Places": "Nations",
    "Compare Events": "Compare",
    "Data & Methods": "Methods"
}

PAGE_TAGS = {
    "Home": "Start block",
    "World Record Timeline": "Record flow",
    "Current World Records": "Gold lane",
    "All-Time Top 200 Rankings": "Elite depth",
    "Athletes Hall of Fame": "Legends",
    "Nations & Places": "Maps & flags",
    "Compare Events": "Race match",
    "Data & Methods": "Behind data"
}

# Read selected page from the URL.
# Example: ?page=World%20Record%20Timeline
query_page = st.query_params.get("page", "Home")

if isinstance(query_page, list):
    query_page = query_page[0]

page = query_page if query_page in PAGES else "Home"

# Build the lane buttons as ONE compact HTML string.
# Important: no multi-line indented HTML here, otherwise Streamlit may print it as code.
nav_items = ""

for i, page_name in enumerate(PAGES, start=1):
    active_class = " active" if page == page_name else ""
    page_url = quote(page_name, safe="")

    nav_items += (
        f'<a class="pool-lane{active_class}" href="?page={page_url}">'
        f'<span class="lane-number">Lane {i}</span>'
        f'<span class="lane-label">{PAGE_LABELS[page_name]}</span>'
        f'<span class="lane-tag">{PAGE_TAGS[page_name]}</span>'
        f'</a>'
    )

nav_html = (
    '<div class="pool-nav-shell">'
    '<div class="pool-nav-top">'
    '<div class="pool-brand">🏊 Swim Records Explorer</div>'
    '<div class="pool-subtitle">'
    'Select a lane to dive into swimming records, rankings, athletes and nations.'
    '</div>'
    '</div>'
    f'<div class="pool-grid">{nav_items}</div>'
    f'<div class="current-lane">Current lane: <b>{PAGE_LABELS[page]}</b></div>'
    '</div>'
)

st.markdown(nav_html, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏊 Filters")
    st.caption("Use this panel only when a page requires filtering.")
    st.markdown("---")
    st.caption("Gold = current record / best performance. Blue = long course. Aqua = short course.")


# ============================================================
# PAGE 1 - HOME
# ============================================================

if page == "Home":

    st.markdown(
        """
        <div class="hero">
            <h1>Swim Records Explorer</h1>
            <p>
            Explore the evolution of world records and the greatest all-time performances in swimming.
            This interactive archive is designed for fans: simple enough to explore, but structured enough
            to reveal athletes, nations, events and historical moments that shaped swimming speed.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        card("World record entries", f"{len(wr):,}", "Historical record progressions")

    with c2:
        card("Top performances", f"{len(top):,}", "Top 200 rankings by event")

    with c3:
        card("Events covered", f"{wr['event_label'].nunique():,}", "Across course, gender and stroke")

    with c4:
        year_min = int(wr["year"].min()) if wr["year"].notna().any() else "-"
        year_max = int(wr["year"].max()) if wr["year"].notna().any() else "-"
        card("Record history", f"{year_min}–{year_max}", "Historical time range")

    st.markdown(
        """
        <div class="info-box">
        <b>Editorial angle:</b> this app does not simply list swimming results.
        It tells the story of speed through two complementary views:
        <br><br>
        <b>World records</b> show how the limit of performance changed over time.  
        <br>
        <b>Top 200 all-time rankings</b> show the depth of elite swimming beyond the single fastest time.
        </div>
        """,
        unsafe_allow_html=True
    )

    section(
        "Overview",
        "A first glance at how world records are distributed across time and how dominant athletes emerge from the database."
    )

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        wr_decade = wr.dropna(subset=["year"]).copy()
        wr_decade["decade"] = (wr_decade["year"] // 10 * 10).astype(int).astype(str) + "s"

        decade_counts = (
            wr_decade.groupby("decade")
            .size()
            .reset_index(name="records")
            .sort_values("decade")
        )

        fig = px.bar(
            decade_counts,
            x="decade",
            y="records",
            text="records",
            color_discrete_sequence=[BLUE],
            title="World records by decade"
        )
        fig.update_traces(textposition="outside")
        fig = plotly_clean_layout(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        athlete_wr = (
            wr.groupby("name")
            .size()
            .reset_index(name="world_records")
            .sort_values("world_records", ascending=False)
            .head(10)
        )

        fig = px.bar(
            athlete_wr,
            x="world_records",
            y="name",
            orientation="h",
            color_discrete_sequence=[GOLD],
            title="Most frequent names in world record history"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = plotly_clean_layout(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)

    section(
        "How to read this app",
        "Use the sidebar to move across the story: first the record timeline, then current records, then all-time rankings, athletes and nations."
    )

    st.markdown(
        """
        <div class="warning-box">
        <b>Important limitation:</b> the app visualizes elite swimming performances.
        It does not include every official swimming result ever recorded, so conclusions should refer to
        <b>world records</b> and <b>top-200 all-time entries</b>, not to the whole swimming population.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE 2 - WORLD RECORD TIMELINE
# ============================================================

elif page == "World Record Timeline":

    section(
        "World Record Timeline",
        "Follow how the fastest official world record in each event changed over time. Lower seconds mean faster performance."
    )

    filtered = apply_common_filters(
        wr,
        gender=True,
        course=True,
        stroke=True,
        distance=True,
        key_prefix="timeline"
    )

    with st.sidebar:
        st.markdown("### Event selection")
        available_events = safe_unique(filtered["event_label"])
        selected_event = st.selectbox(
            "Choose one event",
            available_events,
            index=0 if available_events else None
        )

    data = filtered[filtered["event_label"] == selected_event].copy()
    data = data.sort_values("date")

    if data.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    first_record = data.dropna(subset=["seconds"]).iloc[0]
    last_record = data.dropna(subset=["seconds"]).iloc[-1]
    improvement = first_record["seconds"] - last_record["seconds"]
    improvement_pct = improvement / first_record["seconds"] * 100 if first_record["seconds"] else np.nan

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Selected event", selected_event)

    with c2:
        st.metric("Number of records", len(data))

    with c3:
        st.metric("Total improvement", f"{improvement:.2f} s")

    with c4:
        st.metric("Improvement %", f"{improvement_pct:.1f}%")

    fig = px.line(
        data,
        x="date",
        y="seconds",
        markers=True,
        color="course",
        color_discrete_map=COURSE_COLORS,
        hover_data={
            "name": True,
            "nationality": True,
            "time": True,
            "meet": True,
            "location": True,
            "date": "|%d %b %Y",
            "seconds": ":.2f"
        },
        title=f"Record progression — {selected_event}"
    )

    current_data = data[data["is_current_bool"] == True]

    if not current_data.empty:
        fig.add_trace(
            go.Scatter(
                x=current_data["date"],
                y=current_data["seconds"],
                mode="markers+text",
                marker=dict(size=17, color=GOLD, symbol="star"),
                text=["Current record"] * len(current_data),
                textposition="top center",
                name="Current record",
                hovertext=current_data["name"] + " — " + current_data["time"],
                hoverinfo="text"
            )
        )

    fig.update_yaxes(
        autorange="reversed",
        title="Time in seconds — lower is faster"
    )
    fig.update_xaxes(title="Date")
    fig = plotly_clean_layout(fig, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div class="small-caption">
        Design note: the y-axis is reversed because in swimming a lower time represents a better performance.
        The gold marker highlights the current world record.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        data[
            ["date", "time", "seconds", "name", "nationality", "meet", "location", "is_current_bool"]
        ].rename(
            columns={
                "date": "Date",
                "time": "Time",
                "seconds": "Seconds",
                "name": "Athlete",
                "nationality": "Nationality",
                "meet": "Meet",
                "location": "Location",
                "is_current_bool": "Current record"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 3 - CURRENT WORLD RECORDS
# ============================================================

elif page == "Current World Records":

    section(
        "Current World Records",
        "A clean overview of the records that currently define the limit of swimming performance."
    )

    current = wr[wr["is_current_bool"] == True].copy()

    filtered = apply_common_filters(
        current,
        gender=True,
        course=True,
        stroke=True,
        distance=True,
        key_prefix="current"
    )

    if filtered.empty:
        st.warning("No current records available for the selected filters.")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Current records shown", len(filtered))

    with c2:
        st.metric("Athletes", filtered["name"].nunique())

    with c3:
        st.metric("Nations", filtered["nationality"].nunique())

    with c4:
        newest_year = int(filtered["year"].max()) if filtered["year"].notna().any() else "-"
        st.metric("Most recent record year", newest_year)

    st.markdown(
        """
        <div class="warning-box">
        Direct time comparison across different distances is not analytically fair.
        Use filters to compare similar events, or read this page as a lookup view of current records.
        </div>
        """,
        unsafe_allow_html=True
    )

    display = filtered.copy()
    display["label"] = display["event_label"] + " — " + display["name"]

    fig = px.bar(
        display.sort_values("seconds", ascending=True),
        x="seconds",
        y="label",
        orientation="h",
        color="gender",
        color_discrete_map=GENDER_COLORS,
        hover_data=["time", "nationality", "meet", "location", "date"],
        title="Current world records selected"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_xaxes(title="Time in seconds")
    fig.update_yaxes(title="")
    fig = plotly_clean_layout(fig, height=max(420, 26 * len(display)))
    st.plotly_chart(fig, use_container_width=True)

    table_cols = [
        "event_label", "time", "seconds", "name", "nationality",
        "date", "meet", "location"
    ]

    st.dataframe(
        filtered[table_cols].rename(
            columns={
                "event_label": "Event",
                "time": "Time",
                "seconds": "Seconds",
                "name": "Athlete",
                "nationality": "Nationality",
                "date": "Date",
                "meet": "Meet",
                "location": "Location"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 4 - ALL-TIME TOP 200 RANKINGS
# ============================================================

elif page == "All-Time Top 200 Rankings":

    section(
        "All-Time Top 200 Rankings",
        "Go beyond the world record and explore the depth of elite swimming performances."
    )

    filtered = apply_common_filters(
        top,
        gender=True,
        course=True,
        stroke=True,
        distance=True,
        key_prefix="top"
    )

    with st.sidebar:
        st.markdown("### Ranking selection")

        events = safe_unique(filtered["event_label"])
        selected_event = st.selectbox(
            "Choose event",
            events,
            index=0 if events else None,
            key="top_event"
        )

        max_rank = int(filtered["rank"].max()) if filtered["rank"].notna().any() else 200
        rank_limit = st.slider(
            "Show top N",
            min_value=5,
            max_value=min(200, max_rank),
            value=30,
            step=5
        )

    data = filtered[
        (filtered["event_label"] == selected_event)
        & (filtered["rank"] <= rank_limit)
    ].copy()

    if data.empty:
        st.warning("No ranking data available for the selected filters.")
        st.stop()

    data = data.sort_values(["rank", "time_seconds"])

    best_time = data["time_seconds"].min()
    data["gap_from_best"] = data["time_seconds"] - best_time
    data["chart_label"] = (
        "#" + data["rank"].astype(int).astype(str)
        + " — "
        + data["athlete"].astype(str)
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Event", selected_event)

    with c2:
        st.metric("Best time", format_time(best_time))

    with c3:
        st.metric("Athletes shown", data["athlete"].nunique())

    with c4:
        st.metric("Nations shown", data["team_name"].nunique())

    fig = px.bar(
        data.sort_values("rank"),
        x="gap_from_best",
        y="chart_label",
        orientation="h",
        color="gap_from_best",
        color_continuous_scale=[[0, GOLD], [1, BLUE]],
        hover_data={
            "athlete": True,
            "time_label": True,
            "rank": True,
            "team_name": True,
            "city": True,
            "date": True,
            "gap_from_best": ":.2f"
        },
        title=f"Gap from the best time — {selected_event}"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig.update_xaxes(title="Gap from best time, seconds")
    fig.update_yaxes(title="")
    fig = plotly_clean_layout(fig, height=max(520, 22 * len(data)))
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns([1, 1])

    with col_a:
        fig_hist = px.histogram(
            filtered[filtered["event_label"] == selected_event],
            x="time_seconds",
            nbins=30,
            color_discrete_sequence=[AQUA],
            title="Distribution of top-200 times"
        )
        fig_hist.update_xaxes(title="Time in seconds")
        fig_hist.update_yaxes(title="Number of performances")
        fig_hist = plotly_clean_layout(fig_hist, height=420)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        athlete_counts = (
            filtered[filtered["event_label"] == selected_event]
            .groupby("athlete")
            .size()
            .reset_index(name="entries")
            .sort_values("entries", ascending=False)
            .head(15)
        )

        fig_ath = px.bar(
            athlete_counts,
            x="entries",
            y="athlete",
            orientation="h",
            color_discrete_sequence=[BLUE],
            title="Most recurring athletes in this event top 200"
        )
        fig_ath.update_layout(yaxis=dict(autorange="reversed"))
        fig_ath = plotly_clean_layout(fig_ath, height=420)
        st.plotly_chart(fig_ath, use_container_width=True)

    st.dataframe(
        data[
            [
                "rank", "athlete", "time_label", "time_seconds",
                "team_name", "team_code", "date", "city", "country_code"
            ]
        ].rename(
            columns={
                "rank": "Rank",
                "athlete": "Athlete",
                "time_label": "Time",
                "time_seconds": "Seconds",
                "team_name": "Team",
                "team_code": "Team code",
                "date": "Date",
                "city": "City",
                "country_code": "Country code"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 5 - ATHLETES HALL OF FAME
# ============================================================

elif page == "Athletes Hall of Fame":

    section(
        "Athletes Hall of Fame",
        "Explore the swimmers who appear most often in world record history and all-time rankings."
    )

    wr_names = set(wr["name"].dropna().unique())
    top_names = set(top["athlete"].dropna().unique())
    all_names = sorted([x for x in wr_names.union(top_names) if clean_text(x) != ""])

    with st.sidebar:
        st.markdown("### Athlete selection")
        search = st.text_input("Search athlete", "")
        if search:
            filtered_names = [n for n in all_names if search.lower() in n.lower()]
        else:
            filtered_names = all_names

        selected_athlete = st.selectbox(
            "Choose athlete",
            filtered_names,
            index=0 if filtered_names else None
        )

    if not selected_athlete:
        st.warning("No athlete selected.")
        st.stop()

    athlete_wr = wr[wr["name"] == selected_athlete].copy()
    athlete_top = top[top["athlete"] == selected_athlete].copy()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("World record entries", len(athlete_wr))

    with c2:
        st.metric("Current world records", int(athlete_wr["is_current_bool"].sum()) if not athlete_wr.empty else 0)

    with c3:
        st.metric("Top-200 entries", len(athlete_top))

    with c4:
        best_rank = int(athlete_top["rank"].min()) if not athlete_top.empty and athlete_top["rank"].notna().any() else "-"
        st.metric("Best top-200 rank", best_rank)

    st.markdown(
        f"""
        <div class="info-box">
        <b>{selected_athlete}</b> profile combines two sources:
        world record progression entries and top-200 all-time ranking appearances.
        </div>
        """,
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([1.1, 1])

    with col_a:
        if not athlete_wr.empty:
            athlete_wr = athlete_wr.sort_values("date")

            fig = px.scatter(
                athlete_wr,
                x="date",
                y="seconds",
                color="course",
                color_discrete_map=COURSE_COLORS,
                size=np.where(athlete_wr["is_current_bool"], 18, 9),
                hover_data=["event_label", "time", "nationality", "meet", "location"],
                title=f"World record timeline — {selected_athlete}"
            )
            fig.update_yaxes(autorange="reversed", title="Time in seconds — lower is faster")
            fig.update_xaxes(title="Date")
            fig = plotly_clean_layout(fig, height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("This athlete has no world record entries in the world record dataset.")

    with col_b:
        if not athlete_top.empty:
            event_counts = (
                athlete_top.groupby("event_label")
                .size()
                .reset_index(name="entries")
                .sort_values("entries", ascending=False)
            )

            fig = px.bar(
                event_counts,
                x="entries",
                y="event_label",
                orientation="h",
                color_discrete_sequence=[GOLD],
                title=f"Top-200 appearances by event"
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            fig.update_yaxes(title="")
            fig = plotly_clean_layout(fig, height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("This athlete has no top-200 entries in the all-time ranking dataset.")

    section(
        "Global athlete rankings",
        "These rankings show recurring names, not necessarily a final judgement of absolute greatness."
    )

    col_1, col_2 = st.columns(2)

    with col_1:
        wr_rank = (
            wr.groupby("name")
            .size()
            .reset_index(name="world_record_entries")
            .sort_values("world_record_entries", ascending=False)
            .head(15)
        )

        fig = px.bar(
            wr_rank,
            x="world_record_entries",
            y="name",
            orientation="h",
            color_discrete_sequence=[BLUE],
            title="Most world record entries"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = plotly_clean_layout(fig, height=520)
        st.plotly_chart(fig, use_container_width=True)

    with col_2:
        top_rank = (
            top.groupby("athlete")
            .size()
            .reset_index(name="top_200_entries")
            .sort_values("top_200_entries", ascending=False)
            .head(15)
        )

        fig = px.bar(
            top_rank,
            x="top_200_entries",
            y="athlete",
            orientation="h",
            color_discrete_sequence=[AQUA],
            title="Most top-200 entries"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = plotly_clean_layout(fig, height=520)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Athlete world record entries"):
        if not athlete_wr.empty:
            st.dataframe(
                athlete_wr[
                    ["event_label", "time", "seconds", "date", "nationality", "meet", "location", "is_current_bool"]
                ],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No world record entries.")

    with st.expander("Athlete top-200 entries"):
        if not athlete_top.empty:
            st.dataframe(
                athlete_top[
                    ["event_label", "rank", "time_label", "time_seconds", "team_name", "date", "city"]
                ],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No top-200 entries.")


# ============================================================
# PAGE 6 - NATIONS & PLACES
# ============================================================

elif page == "Nations & Places":

    section(
        "Nations & Places",
        "Discover which nations and locations appear most frequently in swimming record history and all-time rankings."
    )

    filtered_wr = apply_common_filters(
        wr,
        gender=True,
        course=True,
        stroke=True,
        distance=True,
        key_prefix="nation"
    )

    if filtered_wr.empty:
        st.warning("No world record data available for the selected filters.")
        st.stop()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Nations in WR data", filtered_wr["nationality"].nunique())

    with c2:
        st.metric("Record locations", filtered_wr["location"].nunique())

    with c3:
        st.metric("Meets", filtered_wr["meet"].nunique())

    col_a, col_b = st.columns(2)

    with col_a:
        nation_wr = (
            filtered_wr.groupby("nationality")
            .size()
            .reset_index(name="world_record_entries")
            .sort_values("world_record_entries", ascending=False)
            .head(20)
        )

        fig = px.bar(
            nation_wr,
            x="world_record_entries",
            y="nationality",
            orientation="h",
            color_discrete_sequence=[BLUE],
            title="Most represented nationalities in world record history"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = plotly_clean_layout(fig, height=560)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        current_nations = (
            wr[wr["is_current_bool"] == True]
            .groupby("nationality")
            .size()
            .reset_index(name="current_records")
            .sort_values("current_records", ascending=False)
            .head(20)
        )

        fig = px.bar(
            current_nations,
            x="current_records",
            y="nationality",
            orientation="h",
            color_discrete_sequence=[GOLD],
            title="Current world records by nationality"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = plotly_clean_layout(fig, height=560)
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        top_nations = (
            top.groupby("team_name")
            .size()
            .reset_index(name="top_200_entries")
            .sort_values("top_200_entries", ascending=False)
            .head(20)
        )

        fig = px.bar(
            top_nations,
            x="top_200_entries",
            y="team_name",
            orientation="h",
            color_discrete_sequence=[AQUA],
            title="Most represented teams in top-200 rankings"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = plotly_clean_layout(fig, height=560)
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        locations = (
            filtered_wr[filtered_wr["location"] != ""]
            .groupby("location")
            .size()
            .reset_index(name="records")
            .sort_values("records", ascending=False)
            .head(20)
        )

        fig = px.bar(
            locations,
            x="records",
            y="location",
            orientation="h",
            color_discrete_sequence=[NAVY],
            title="Locations where world records were set"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = plotly_clean_layout(fig, height=560)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div class="small-caption">
        Interpretation note: these charts show representation inside the available datasets.
        They should not be read as a complete medal table or as a full ranking of national swimming systems.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE 7 - COMPARE EVENTS
# ============================================================

elif page == "Compare Events":

    section(
        "Compare Events",
        "Compare how different swimming events evolved: number of record changes, time improvement and record age."
    )

    filtered = apply_common_filters(
        wr,
        gender=True,
        course=True,
        stroke=True,
        distance=True,
        key_prefix="compare"
    )

    if filtered.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    summary_rows = []

    for event, group in filtered.dropna(subset=["seconds"]).groupby("event_label"):
        group = group.sort_values("date")

        if group.empty:
            continue

        first = group.iloc[0]
        last = group.iloc[-1]
        improvement_s = first["seconds"] - last["seconds"]
        improvement_pct = improvement_s / first["seconds"] * 100 if first["seconds"] else np.nan

        current_rows = group[group["is_current_bool"] == True]
        if not current_rows.empty:
            current_date = current_rows.iloc[-1]["date"]
            current_holder = current_rows.iloc[-1]["name"]
            current_time = current_rows.iloc[-1]["time"]
        else:
            current_date = last["date"]
            current_holder = last["name"]
            current_time = last["time"]

        age_years = (pd.Timestamp.today() - current_date).days / 365.25 if not pd.isna(current_date) else np.nan

        summary_rows.append(
            {
                "event_label": event,
                "records": len(group),
                "first_year": first["year"],
                "latest_year": last["year"],
                "first_seconds": first["seconds"],
                "latest_seconds": last["seconds"],
                "improvement_s": improvement_s,
                "improvement_pct": improvement_pct,
                "current_record_age_years": age_years,
                "current_holder": current_holder,
                "current_time": current_time
            }
        )

    summary = pd.DataFrame(summary_rows)

    if summary.empty:
        st.warning("No comparable event summary available.")
        st.stop()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Events compared", len(summary))

    with c2:
        st.metric("Average record changes", f"{summary['records'].mean():.1f}")

    with c3:
        oldest = summary.sort_values("current_record_age_years", ascending=False).iloc[0]
        st.metric("Oldest current record", oldest["event_label"])

    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.bar(
            summary.sort_values("records", ascending=False).head(25),
            x="records",
            y="event_label",
            orientation="h",
            color_discrete_sequence=[BLUE],
            title="Events with the most world record changes"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig.update_xaxes(title="Number of historical records")
        fig.update_yaxes(title="")
        fig = plotly_clean_layout(fig, height=620)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = px.bar(
            summary.sort_values("improvement_pct", ascending=False).head(25),
            x="improvement_pct",
            y="event_label",
            orientation="h",
            color_discrete_sequence=[AQUA],
            title="Largest percentage improvement from first to latest record"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig.update_xaxes(title="Improvement %")
        fig.update_yaxes(title="")
        fig = plotly_clean_layout(fig, height=620)
        st.plotly_chart(fig, use_container_width=True)

    section(
        "Record age",
        "Some records fall frequently, while others survive for many years."
    )

    fig = px.scatter(
        summary,
        x="records",
        y="current_record_age_years",
        size="improvement_pct",
        color="improvement_pct",
        color_continuous_scale=[[0, BLUE], [1, GOLD]],
        hover_data=[
            "event_label",
            "current_holder",
            "current_time",
            "first_year",
            "latest_year",
            "improvement_pct"
        ],
        title="Record changes vs current record age"
    )
    fig.update_xaxes(title="Number of record changes")
    fig.update_yaxes(title="Current record age, years")
    fig = plotly_clean_layout(fig, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        summary.sort_values("records", ascending=False).rename(
            columns={
                "event_label": "Event",
                "records": "Number of records",
                "first_year": "First year",
                "latest_year": "Latest year",
                "improvement_s": "Improvement, seconds",
                "improvement_pct": "Improvement, %",
                "current_record_age_years": "Current record age, years",
                "current_holder": "Current holder",
                "current_time": "Current time"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 8 - DATA & METHODS
# ============================================================

elif page == "Data & Methods":

    section(
        "Data & Methods",
        "This page explains how the app uses the two datasets and what limitations should be considered."
    )

    st.markdown(
        """
        <div class="info-box">
        <b>Dataset 1 — World records history</b><br>
        Used to visualize the historical progression of world records across gender, course, distance and stroke.
        It contains athlete name, nationality, date, meet, location, time in seconds and whether the record is current.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Property": [
                    "Rows",
                    "Events",
                    "Athletes",
                    "Nationalities",
                    "Courses",
                    "Years"
                ],
                "Value": [
                    len(wr),
                    wr["event_label"].nunique(),
                    wr["name"].nunique(),
                    wr["nationality"].nunique(),
                    ", ".join(safe_unique(wr["course"])),
                    f"{int(wr['year'].min())}–{int(wr['year'].max())}" if wr["year"].notna().any() else "-"
                ]
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        <div class="info-box">
        <b>Dataset 2 — All-time top 200 performances</b><br>
        Used to explore depth of elite performance beyond a single record.
        It contains ranking order, athlete, team, event description, time, date and competition location.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Property": [
                    "Rows",
                    "Events",
                    "Athletes",
                    "Teams",
                    "Cities",
                    "Years"
                ],
                "Value": [
                    len(top),
                    top["event_label"].nunique(),
                    top["athlete"].nunique(),
                    top["team_name"].nunique(),
                    top["city"].nunique(),
                    f"{int(top['year'].min())}–{int(top['year'].max())}" if top["year"].notna().any() else "-"
                ]
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    section("Interpretation rules")

    st.markdown(
        """
        <div class="warning-box">
        <b>1. Elite data only.</b><br>
        The app does not represent all swimming races ever performed. It focuses on world records and top-200 all-time performances.
        <br><br>
        <b>2. Same athlete can appear multiple times.</b><br>
        Entries represent performances or record events, not unique athletes.
        <br><br>
        <b>3. Long course and short course are not directly equivalent.</b><br>
        The app allows comparison, but interpretation should consider that LC and SC are different competition contexts.
        <br><br>
        <b>4. Lower time is better.</b><br>
        Timeline charts reverse the y-axis to make performance improvement visually intuitive.
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("World records raw preview"):
        st.dataframe(wr.head(100), use_container_width=True)

    with st.expander("Top performances raw preview"):
        st.dataframe(top.head(100), use_container_width=True)