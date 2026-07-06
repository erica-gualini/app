import re
import base64
import random
import unicodedata
from difflib import get_close_matches
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
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow:wght@400;500;600;700;800&display=swap');

    html, body, .stApp {
        font-family: 'Barlow', system-ui, -apple-system, sans-serif;
    }

    .stApp {
        background-color: #EDE4D2;
    }

    .main {
        background-color: transparent;
    }

    /* thin wave rule used as a decorative divider */
    .wave-rule {
        height: 12px;
        margin: 4px 0 12px 0;
        background:
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='90' height='12'%3E%3Cpath d='M0 6 q11.25 -6 22.5 0 t22.5 0 t22.5 0 t22.5 0' fill='none' stroke='%231A38A8' stroke-width='2.4' stroke-linecap='round'/%3E%3C/svg%3E") repeat-x left center / 90px 12px;
        opacity: 0.5;
    }

    .hero {
        position: relative;
        overflow: hidden;
        display: grid;
        grid-template-columns: 1.12fr 0.88fr;
        gap: 34px;
        align-items: center;
        padding: 42px 46px;
        border-radius: 26px;
        background: #F7F1E3;
        border: 1px solid #E7DFCB;
        color: #12233A;
        margin-bottom: 26px;
        box-shadow: 0 26px 60px -34px rgba(5,43,68,0.5);
    }

    .hero-kicker {
        font-family: 'Barlow', system-ui, sans-serif;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #1A38A8;
        margin-bottom: 12px;
    }

    .hero h1 {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.005em;
        line-height: 0.9;
        font-size: 62px;
        color: #1A38A8;
        margin: 0 0 16px 0;
    }

    .hero p {
        font-family: 'Barlow', system-ui, sans-serif;
        font-size: 17.5px;
        font-weight: 500;
        color: #3A4A5C;
        opacity: 1;
        max-width: 620px;
        line-height: 1.5;
        margin: 0;
    }

    @media (max-width: 900px) {
        .hero {
            grid-template-columns: 1fr;
            gap: 22px;
            padding: 30px 28px;
        }
        .hero h1 { font-size: 46px; }
    }

    .section-title {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.006em;
        line-height: 0.95;
        color: #1A38A8;
        font-size: 40px;
        margin-top: 16px;
        margin-bottom: 8px;
    }

    .section-subtitle {
        font-family: 'Barlow', system-ui, sans-serif;
        color: #52616B;
        font-size: 16.5px;
        font-weight: 500;
        max-width: 840px;
        margin-bottom: 18px;
        line-height: 1.5;
    }

    .kpi-card {
        background-color: #FFFDF8;
        padding: 22px 22px;
        border-radius: 18px;
        border: 1px solid #E7DFCB;
        box-shadow: 0 12px 28px -18px rgba(5,43,68,0.4);
        min-height: 130px;
    }

    .kpi-label {
        font-size: 12.5px;
        text-transform: uppercase;
        color: #52616B;
        font-weight: 700;
        letter-spacing: 0.08em;
    }

    .kpi-value {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        font-size: 42px;
        color: #1A38A8;
        margin-top: 8px;
        line-height: 1;
    }

    .kpi-note {
        font-size: 13px;
        color: #52616B;
        margin-top: 5px;
    }

    .info-box {
        background-color: #FFFDF8;
        border-left: 6px solid #1A38A8;
        border-radius: 14px;
        padding: 18px 22px;
        margin: 16px 0;
        box-shadow: 0 12px 28px -20px rgba(5,43,68,0.4);
        color: #26333F;
    }

    .warning-box {
        background-color: #FBF3DE;
        border-left: 6px solid #D6A937;
        border-radius: 14px;
        padding: 18px 22px;
        margin: 16px 0;
        color: #4A3E1E;
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

    .block-container {
        padding-top: 2.6rem;
    }

    /* Let the sticky pool header sit above Streamlit's own top bar
       instead of being clipped by it. */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ============================================================
       HOME + NAV - OLYMPIC POOL
       One single pool component is used everywhere:
       - full page on the Home
       - small sticky header (.compact) on every other page
       Light & clean: flat refined blue, hairline borders, thin red
       rope dashes, translucent floor numerals, pictogram swimmer.
    ============================================================ */

    .home-pool {
        max-width: 1400px;
        margin: 0 auto 10px auto;
        background: #FBF7EF;
        border: 1px solid #E7DFCB;
        border-radius: 24px;
        padding: 16px;
        box-shadow: 0 30px 70px -34px rgba(5,43,68,0.4);
    }

    .home-pool-head {
        text-align: center;
        margin: 10px 0 16px 0;
    }

    .home-pool-title {
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 34px;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.01em;
        line-height: 0.95;
        color: #1A38A8;
    }

    .home-pool-sub {
        color: #52616B;
        font-size: 13.5px;
        font-weight: 500;
        margin-top: 7px;
        line-height: 1.4;
    }

    .home-lanes {
        position: relative;
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        gap: 0;
        border-radius: 16px;
        overflow: hidden;
        background:
            url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='130'%20height='44'%3E%3Cpath%20d='M0%2022%20Q16.25%2014%2032.5%2022%20T65%2022%20T97.5%2022%20T130%2022'%20fill='none'%20stroke='%23FFFFFF'%20stroke-opacity='0.10'%20stroke-width='2'%20stroke-linecap='round'/%3E%3C/svg%3E") repeat,
            url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='220'%20height='74'%3E%3Cpath%20d='M0%2037%20Q27.5%2025%2055%2037%20T110%2037%20T165%2037%20T220%2037'%20fill='none'%20stroke='%23FFFFFF'%20stroke-opacity='0.06'%20stroke-width='3'%20stroke-linecap='round'/%3E%3C/svg%3E") repeat,
            linear-gradient(180deg, #46B8E6 0%, #1E86BC 100%);
        background-size: 130px 44px, 220px 74px, 100% 100%;
        box-shadow:
            inset 0 0 0 1px rgba(255,255,255,0.35),
            inset 0 18px 40px rgba(5,43,68,0.16);
        animation: home-water-drift 22s linear infinite;
    }

    @keyframes home-water-drift {
        from { background-position: 0 0, 0 0, 0 0; }
        to   { background-position: 130px 44px, -220px 74px, 0 0; }
    }

    .home-lane {
        position: relative;
        display: block;
        min-height: 68vh;
        overflow: hidden;
        text-decoration: none !important;
        transition: background 0.25s ease;
    }

    .home-lane:hover {
        background: rgba(255,255,255,0.07);
    }

    /* Lane ropes sit exactly on the lane boundaries (siblings of the
       lanes, absolutely positioned so the grid ignores them):
       a thin white cable with crisp red dashes. */
    .pool-rope {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 6px;
        transform: translateX(-50%);
        z-index: 2;
        pointer-events: none;
        background:
            repeating-linear-gradient(180deg, #E23636 0px 12px, transparent 12px 22px) center top / 4px 100% no-repeat,
            linear-gradient(180deg, rgba(255,255,255,0.55), rgba(255,255,255,0.55)) center top / 1.5px 100% no-repeat;
    }

    .pool-rope:nth-of-type(1) { left: 12.5%; }
    .pool-rope:nth-of-type(2) { left: 25%; }
    .pool-rope:nth-of-type(3) { left: 37.5%; }
    .pool-rope:nth-of-type(4) { left: 50%; }
    .pool-rope:nth-of-type(5) { left: 62.5%; }
    .pool-rope:nth-of-type(6) { left: 75%; }
    .pool-rope:nth-of-type(7) { left: 87.5%; }

    /* Dark line on the lane floor, with the T mark at both walls. */
    .hl-line {
        position: absolute;
        left: 50%;
        top: 13%;
        bottom: 5%;
        width: 4px;
        transform: translateX(-50%);
        z-index: 1;
        pointer-events: none;
        background: rgba(5,43,68,0.16);
        border-radius: 2px;
    }

    .hl-line::before,
    .hl-line::after {
        content: "";
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 22px;
        height: 4px;
        background: rgba(5,43,68,0.16);
        border-radius: 2px;
    }

    .hl-line::before { top: 0; }
    .hl-line::after { bottom: 0; }

    /* Section button: a frosted minimal card on the finish wall. */
    .hl-btn {
        position: relative;
        z-index: 3;
        display: block;
        margin: 14px 10px 0 10px;
        padding: 10px 6px;
        text-align: center;
        background: rgba(255,255,255,0.92);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        border: 1px solid #E3EEF3;
        border-radius: 10px;
        box-shadow: 0 10px 24px -12px rgba(5,43,68,0.45);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .hl-name {
        display: block;
        font-family: 'Anton', system-ui, sans-serif;
        color: #12233A;
        font-size: 14px;
        font-weight: 400;
        text-transform: uppercase;
        line-height: 1.05;
        letter-spacing: 0.02em;
    }

    .hl-tag {
        display: block;
        color: #5A7484;
        font-size: 9.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
        line-height: 1.15;
    }

    .home-lane:hover .hl-btn {
        transform: translateY(-2px);
        border-color: #E23636;
        box-shadow: 0 16px 30px -14px rgba(5,43,68,0.55);
    }

    .home-lane.active .hl-btn {
        border-color: #E23636;
    }

    /* Translucent lane numeral painted on the pool floor. */
    .hl-num {
        position: absolute;
        bottom: 14px;
        left: 0;
        right: 0;
        z-index: 1;
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        letter-spacing: -0.02em;
        line-height: 1;
        color: rgba(255,255,255,0.30);
        pointer-events: none;
    }

    /* The swimmer: a white pictogram that swims up to the wall on hover. */
    .home-lane::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        z-index: 4;
        width: 40px;
        height: 62px;
        background: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2044%2070'%3E%3Cg%20fill='none'%20stroke='%23FFFFFF'%20stroke-width='4.6'%20stroke-linecap='round'%3E%3Cpath%20d='M15%2020%20L12%204'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='-6%2015%2020%3B16%2015%2020%3B-6%2015%2020'%20dur='1s'%20repeatCount='indefinite'/%3E%3C/path%3E%3Cpath%20d='M29%2020%20L37%2032'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='12%2029%2020%3B-14%2029%2020%3B12%2029%2020'%20dur='1s'%20repeatCount='indefinite'/%3E%3C/path%3E%3Cpath%20d='M19.5%2046%20L17.5%2064'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='-9%2019.5%2046%3B9%2019.5%2046%3B-9%2019.5%2046'%20dur='0.4s'%20repeatCount='indefinite'/%3E%3C/path%3E%3Cpath%20d='M24.5%2046%20L26.5%2062'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='9%2024.5%2046%3B-9%2024.5%2046%3B9%2024.5%2046'%20dur='0.4s'%20repeatCount='indefinite'/%3E%3C/path%3E%3C/g%3E%3Ccircle%20cx='22'%20cy='13'%20r='5.6'%20fill='%23FFFFFF'/%3E%3Cpath%20d='M15%2020%20Q22%2015.5%2029%2020%20L26%2045.5%20Q22%2048.5%2018%2045.5%20Z'%20fill='%23FFFFFF'/%3E%3C/svg%3E") center / contain no-repeat;
        opacity: 0;
        transform: translate(-50%, -50%);
        filter: drop-shadow(0 4px 8px rgba(5,43,68,0.35));
        pointer-events: none;
    }

    .home-lane:hover::after {
        animation: swim-up 1.7s cubic-bezier(0.3, 0.55, 0.35, 1) forwards;
    }

    @keyframes swim-up {
        0% {
            opacity: 0;
            top: 100%;
            transform: translate(-50%, -50%) rotate(0deg);
        }
        7% {
            opacity: 1;
        }
        30% {
            transform: translate(-56%, -50%) rotate(-3deg);
        }
        55% {
            transform: translate(-44%, -50%) rotate(3deg);
        }
        80% {
            transform: translate(-53%, -50%) rotate(-2deg);
        }
        100% {
            opacity: 1;
            top: 15%;
            transform: translate(-50%, -50%) rotate(0deg);
        }
    }

    @media (max-width: 1150px) {
        .home-lanes {
            grid-template-columns: repeat(4, 1fr);
            row-gap: 14px;
        }

        .home-lane {
            min-height: 40vh;
        }

        .pool-rope { display: none; }
        .pool-rope:nth-of-type(2n) { display: block; }
    }

    @media (max-width: 650px) {
        .home-lanes {
            grid-template-columns: repeat(2, 1fr);
        }

        .home-lane {
            min-height: 34vh;
        }

        .pool-rope:nth-of-type(2n) { display: none; }
        .pool-rope:nth-of-type(4) { display: block; }
    }

    /* ============================================================
       COMPACT POOL NAV — the very same pool as the Home, shrunk.
       Shown as a sticky header on every page other than Home,
       so navigation always keeps the identical style.
    ============================================================ */

    .home-pool.compact {
        position: sticky;
        top: 8px;
        z-index: 999;
        max-width: 1400px;
        margin: 0 auto 24px auto;
        padding: 12px;
        box-shadow: 0 14px 34px -12px rgba(5,43,68,0.30);
    }

    .home-pool.compact .home-pool-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        text-align: left;
        margin: 4px 4px 10px 4px;
    }

    .home-pool.compact .home-pool-title { font-size: 19px; }

    .home-pool.compact .brand-logo { width: 38px; height: 38px; }

    .home-pool.compact .home-pool-sub {
        margin-top: 0;
        text-align: right;
        max-width: 440px;
        font-size: 12px;
    }

    .home-pool.compact .home-lanes {
        border-radius: 14px;
        animation-duration: 30s;
    }

    /* fixed height instead of 68vh */
    .home-pool.compact .home-lane { min-height: 122px; }

    .home-pool.compact .hl-line { top: 8%; bottom: 4%; }

    .home-pool.compact .hl-btn {
        margin: 12px 6px 0 6px;
        padding: 8px 4px;
        border-radius: 9px;
    }

    .home-pool.compact .hl-name { font-size: 12px; }

    .home-pool.compact .hl-tag {
        font-size: 8.5px;
        margin-top: 3px;
    }

    .home-pool.compact .hl-num {
        bottom: 8px;
        font-size: 26px;
    }

    .home-pool.compact .home-lane::after {
        width: 26px;
        height: 40px;
    }

    .home-pool.compact .current-lane {
        margin-top: 10px;
        color: #52616B;
        font-size: 12.5px;
        text-align: center;
        font-weight: 600;
    }

    .home-pool.compact .current-lane b { color: #052B44; }

    /* compact stays short on small screens too
       (wins over the .home-lane media queries by specificity) */
    @media (max-width: 1150px) {
        .home-pool.compact .home-lane { min-height: 96px; }
    }

    @media (max-width: 650px) {
        .home-pool.compact .home-pool-head {
            flex-direction: column;
            align-items: flex-start;
        }
        .home-pool.compact .home-pool-sub { text-align: left; }
        .home-pool.compact .home-lane { min-height: 84px; }
    }

    /* ============================================================
       BRAND / LOGO, STAT CHIPS, POOL LEGEND
    ============================================================ */

    .brand {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        vertical-align: middle;
    }

    .brand-logo {
        width: 48px;
        height: 48px;
        flex: none;
        filter: drop-shadow(0 6px 14px rgba(5,43,68,0.28));
    }

    .brand-text {
        text-align: left;
        line-height: 1;
    }

    .brand-tag {
        font-family: 'Barlow', system-ui, sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #1A38A8;
        margin-top: 4px;
    }

    .home-pool.compact .brand-tag { font-size: 10px; margin-top: 2px; }

    .pool-stats {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px;
        margin: 18px 0 2px 0;
    }

    .pool-stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 108px;
        padding: 12px 18px;
        border-radius: 16px;
        background: #FFFFFF;
        border: 1px solid #E3EEF3;
        box-shadow: 0 10px 22px -14px rgba(5,43,68,0.45);
    }

    .ps-num {
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 30px;
        font-weight: 400;
        line-height: 1;
        color: #1A38A8;
    }

    .ps-lab {
        margin-top: 5px;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #5A7484;
    }

    .pool-foot {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 16px;
        font-size: 12.5px;
        font-weight: 600;
        color: #52616B;
    }

    .pool-foot span {
        display: inline-flex;
        align-items: center;
        gap: 7px;
    }

    .pool-foot i {
        width: 11px;
        height: 11px;
        border-radius: 50%;
        display: inline-block;
    }

    @media (max-width: 650px) {
        .pool-stat { min-width: 88px; padding: 10px 12px; }
        .ps-num { font-size: 21px; }
    }

    /* ============================================================
       SWIM RECORD TOE - GAME (styled to match the app)
    ============================================================ */

    .game-turn-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #E8F8FB 100%);
        border: 1px solid #E4EEF3;
        border-radius: 20px;
        padding: 16px 20px;
        box-shadow: 0 6px 20px rgba(5,43,68,0.06);
        color: #052B44;
        text-align: center;
    }

    .game-turn-card .gt-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-weight: 700;
        color: #52616B;
    }

    .game-turn-card .gt-value {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        color: #1A38A8;
        margin-top: 4px;
        line-height: 1.05;
    }

    .game-axis-label {
        font-family: 'Anton', system-ui, sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        background: #12233A;
        color: white;
        border-radius: 16px;
        padding: 12px 10px;
        text-align: center;
        font-weight: 400;
        min-height: 64px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.1;
        box-shadow: 0 8px 18px rgba(5,43,68,0.14);
    }

    .game-row-label {
        font-family: 'Anton', system-ui, sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        background: linear-gradient(135deg, #1A38A8 0%, #0A6C9F 100%);
        color: white;
        border-radius: 16px;
        padding: 12px 10px;
        text-align: center;
        font-weight: 400;
        min-height: 72px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.1;
        box-shadow: 0 8px 18px rgba(5,43,68,0.12);
    }

    .game-empty-corner {
        background: transparent;
        min-height: 64px;
    }

    /* Game buttons — pool-lane look (only the Game page uses buttons). */
    div[data-testid="stButton"] button {
        font-family: 'Barlow', system-ui, sans-serif;
        border-radius: 16px;
        border: 2px solid rgba(26,56,168,0.22);
        background:
            linear-gradient(90deg,
                rgba(255,255,255,0.72) 0px,
                rgba(255,255,255,0.72) 2px,
                transparent 2px,
                transparent calc(100% - 2px),
                rgba(255,255,255,0.72) calc(100% - 2px),
                rgba(255,255,255,0.72) 100%
            ),
            linear-gradient(135deg, #E8F8FB 0%, #BDEFFA 48%, #6EDAF0 100%);
        color: #12233A;
        font-weight: 700;
        min-height: 62px;
        box-shadow: 0 8px 20px rgba(5,43,68,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        white-space: pre-line;
    }

    div[data-testid="stButton"] button:hover {
        border-color: #0A6C9F;
        transform: translateY(-2px);
        box-shadow: 0 14px 28px rgba(5,43,68,0.16);
    }

    div[data-testid="stButton"] button:disabled {
        background: #E4EEF3;
        color: #52616B;
        border-color: #D8ECF4;
        box-shadow: none;
        transform: none;
    }

    /* ============================================================
       SWIM PHOTOS (with graceful placeholder when missing)
    ============================================================ */

    .swim-figure {
        position: relative;
        overflow: hidden;
        border-radius: 20px;
        border: 1px solid #E7DFCB;
        box-shadow: 0 22px 50px -30px rgba(5,43,68,0.55);
        background: #D7E6EE;
    }

    .swim-figure-inner {
        position: relative;
        width: 100%;
    }

    .swim-figure-inner > img,
    .swim-figure-inner > .img-ph-label {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
    }

    .swim-figure.is-placeholder {
        background:
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='40'%3E%3Cg fill='none' stroke='%231A38A8' stroke-opacity='0.28' stroke-width='2.4' stroke-linecap='round'%3E%3Cpath d='M0 12 q15 -8 30 0 t30 0 t30 0 t30 0'/%3E%3Cpath d='M0 28 q15 -8 30 0 t30 0 t30 0 t30 0'/%3E%3C/g%3E%3C/svg%3E") repeat,
            linear-gradient(135deg, #E9EFEA 0%, #D7E6EE 100%);
    }

    .img-ph-label {
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #3A4A5C;
        font-family: 'Barlow', system-ui, sans-serif;
        font-weight: 600;
        font-size: 14px;
        line-height: 1.4;
        padding: 18px;
    }

    .img-ph-label b { color: #1A38A8; }

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
# GAME FUNCTIONS - SWIM RECORD TOE
# ============================================================

def normalize_answer(value):
    """Normalize swimmer names for robust answer checking."""
    value = clean_text(value).lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def prepare_swim_game_data(df):
    """Prepare world record data for the tic-tac-toe quiz."""
    game_df = df.copy()

    game_df = game_df[game_df["name"].astype(str).str.strip() != ""].copy()
    game_df = game_df[game_df["event_label"].astype(str).str.strip() != ""].copy()

    # Place criterion: location first, meet as fallback.
    game_df["record_place"] = game_df["location"].astype(str).apply(clean_text)

    if "meet" in game_df.columns:
        game_df.loc[game_df["record_place"] == "", "record_place"] = (
            game_df.loc[game_df["record_place"] == "", "meet"]
            .astype(str)
            .apply(clean_text)
        )

    game_df.loc[game_df["record_place"] == "", "record_place"] = "Unknown place"

    # Decade criterion.
    game_df["year_numeric"] = pd.to_numeric(game_df["year"], errors="coerce")
    game_df["decade"] = np.where(
        game_df["year_numeric"].notna(),
        ((game_df["year_numeric"] // 10) * 10).astype("Int64").astype(str) + "s",
        "Unknown decade"
    )

    # Compact event criterion, useful if event_label is too specific.
    game_df["event_family"] = (
        game_df["distance"].astype(str)
        + "m "
        + game_df["stroke"].astype(str)
    )

    # Remove empty/useless criteria.
    for col in ["record_place", "nationality", "decade", "course", "event_label", "event_family"]:
        if col in game_df.columns:
            game_df[col] = game_df[col].astype(str).apply(clean_text)
            game_df = game_df[game_df[col] != ""]
            game_df = game_df[game_df[col] != "Unknown"]

    return game_df


def build_swim_game_grid(game_df, row_col, col_col, attempts=1500):
    """
    Build a 3x3 grid.
    It tries to find rows and columns where every intersection has at least one valid swimmer.
    """
    pair_counts = (
        game_df
        .dropna(subset=[row_col, col_col, "name"])
        .groupby([row_col, col_col])["name"]
        .nunique()
        .reset_index(name="valid_answers")
    )

    if pair_counts.empty:
        return [], [], 0

    # Use the most connected values to avoid impossible boards.
    candidate_rows = (
        pair_counts.groupby(row_col)["valid_answers"]
        .sum()
        .sort_values(ascending=False)
        .head(35)
        .index
        .tolist()
    )

    candidate_cols = (
        pair_counts.groupby(col_col)["valid_answers"]
        .sum()
        .sort_values(ascending=False)
        .head(35)
        .index
        .tolist()
    )

    if len(candidate_rows) < 3 or len(candidate_cols) < 3:
        return [], [], 0

    best_rows = None
    best_cols = None
    best_score = -1

    for _ in range(attempts):
        rows = random.sample(candidate_rows, 3)
        cols = random.sample(candidate_cols, 3)

        score = 0
        for r in rows:
            for c in cols:
                exists = (
                    (pair_counts[row_col] == r)
                    & (pair_counts[col_col] == c)
                ).any()
                if exists:
                    score += 1

        if score > best_score:
            best_rows = rows
            best_cols = cols
            best_score = score

        if score == 9:
            break

    return best_rows, best_cols, best_score


def get_cell_answers(game_df, row_value, col_value, row_col, col_col):
    """Return all valid swimmers for a specific grid cell."""
    cell_df = game_df[
        (game_df[row_col].astype(str) == str(row_value))
        & (game_df[col_col].astype(str) == str(col_value))
    ].copy()

    answers = (
        cell_df["name"]
        .dropna()
        .astype(str)
        .apply(clean_text)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return answers


def validate_swim_answer(game_df, answer, row_value, col_value, row_col, col_col):
    """Check whether the submitted swimmer is valid for the selected cell."""
    valid_answers = get_cell_answers(game_df, row_value, col_value, row_col, col_col)

    if not valid_answers:
        return False, None, []

    normalized_map = {
        normalize_answer(name): name
        for name in valid_answers
    }

    user_norm = normalize_answer(answer)

    if user_norm in normalized_map:
        return True, normalized_map[user_norm], valid_answers

    close = get_close_matches(
        user_norm,
        list(normalized_map.keys()),
        n=1,
        cutoff=0.84
    )

    if close:
        return True, normalized_map[close[0]], valid_answers

    return False, None, valid_answers


def check_swim_game_winner(board):
    """Return winner symbol, Draw, or None."""
    lines = []

    lines.extend(board)
    lines.extend([[board[0][j], board[1][j], board[2][j]] for j in range(3)])
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    for line in lines:
        if line[0] != "" and line[0] == line[1] == line[2]:
            return line[0]

    if all(board[i][j] != "" for i in range(3) for j in range(3)):
        return "Draw"

    return None


def reset_swim_record_toe(game_df, row_col, col_col):
    rows, cols, score = build_swim_game_grid(game_df, row_col, col_col)

    st.session_state.swim_toe_rows = rows
    st.session_state.swim_toe_cols = cols
    st.session_state.swim_toe_score = score
    st.session_state.swim_toe_board = [["" for _ in range(3)] for _ in range(3)]
    st.session_state.swim_toe_answers = [["" for _ in range(3)] for _ in range(3)]
    st.session_state.swim_toe_turn = "❌"
    st.session_state.swim_toe_winner = None
    st.session_state.swim_toe_selected = None
    st.session_state.swim_toe_used_names = []
    st.session_state.swim_toe_feedback = ""


# ============================================================
# NAVIGATION - SWIMMING POOL LANES
# ============================================================

PAGES = [
    "Home",
    "World Record Timeline",
    "All-Time Top 200 Rankings",
    "Athletes Hall of Fame",
    "Nations & Places",
    "Compare Events",
    "Data & Methods",
    "Game"
]

PAGE_LABELS = {
    "Home": "Home",
    "World Record Timeline": "Timeline",
    "All-Time Top 200 Rankings": "Top 200",
    "Athletes Hall of Fame": "Athletes",
    "Nations & Places": "Nations",
    "Compare Events": "Compare",
    "Data & Methods": "Methods",
    "Game": "Game"
}

PAGE_TAGS = {
    "Home": "Start block",
    "World Record Timeline": "Record flow",
    "All-Time Top 200 Rankings": "Elite depth",
    "Athletes Hall of Fame": "Legends",
    "Nations & Places": "Maps & flags",
    "Compare Events": "Race match",
    "Data & Methods": "Behind data",
    "Game": "Play & guess"
}

# Read selected page from the URL.
# Example: ?page=World%20Record%20Timeline
query_page = st.query_params.get("page", "Home")

if isinstance(query_page, list):
    query_page = query_page[0]

page = query_page if query_page in PAGES else "Home"


# ------------------------------------------------------------
# Shared builder for the pool lanes.
# The SAME lanes are used both for the full-page pool on the Home
# and for the small (sticky) pool shown on every other page, so
# navigation always keeps the identical style.
# Keep it as ONE compact HTML string: no multi-line indented HTML,
# otherwise Streamlit renders it as a code block.
# ------------------------------------------------------------

def build_pool_lanes():
    lanes = ""
    for i, page_name in enumerate(PAGES, start=1):
        active_class = " active" if page == page_name else ""
        page_url = quote(page_name, safe="")
        lanes += (
            f'<a class="home-lane{active_class}" href="?page={page_url}">'
            f'<span class="hl-line"></span>'
            f'<span class="hl-btn">'
            f'<span class="hl-name">{PAGE_LABELS[page_name]}</span>'
            f'<span class="hl-tag">{PAGE_TAGS[page_name]}</span>'
            f'</span>'
            f'<span class="hl-num">{i}</span>'
            f'</a>'
        )
    # Rope separators on the exact lane boundaries (absolute, the grid ignores them).
    lanes += '<span class="pool-rope"></span>' * 7
    return lanes


# ------------------------------------------------------------
# Brand logo (inline SVG): a rounded badge with a gradient pool,
# white waves, a little swimmer and a gold "record" dot.
# ------------------------------------------------------------

LOGO_SVG = (
    '<svg class="brand-logo" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">'
    '<defs><linearGradient id="swlg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#052B44"/>'
    '<stop offset="0.5" stop-color="#0A6C9F"/>'
    '<stop offset="1" stop-color="#22B8CF"/>'
    '</linearGradient></defs>'
    '<rect x="1" y="1" width="46" height="46" rx="13" fill="url(#swlg)"/>'
    '<g fill="none" stroke="#FFFFFF" stroke-linecap="round">'
    '<path d="M6 32 q4 -4 8 0 t8 0 t8 0 t8 0" stroke-width="2"/>'
    '<path d="M6 38 q4 -4 8 0 t8 0 t8 0 t8 0" stroke-width="2" opacity="0.55"/>'
    '</g>'
    '<circle cx="18.5" cy="16" r="3.4" fill="#FFFFFF"/>'
    '<path d="M13.5 24 q6 -5 12 -3 l6.5 -4.5" fill="none" stroke="#FFFFFF" '
    'stroke-width="3" stroke-linecap="round"/>'
    '<circle cx="34.5" cy="13.5" r="2.4" fill="#D6A937"/>'
    '</svg>'
)


def brand_html(tagline):
    """Logo + title + small uppercase tagline, reused on every header."""
    return (
        '<div class="brand">'
        f'{LOGO_SVG}'
        '<div class="brand-text">'
        '<div class="home-pool-title">Swim Records Explorer</div>'
        f'<div class="brand-tag">{tagline}</div>'
        '</div>'
        '</div>'
    )


def home_stats_html():
    """Scoreboard-style chips with a few real numbers from the datasets."""
    names = {clean_text(x) for x in wr["name"].dropna()} | {clean_text(x) for x in top["athlete"].dropna()}
    names = {n for n in names if n}

    chips = [
        (len(wr), "World records"),
        (wr["event_label"].nunique(), "Events"),
        (len(names), "Athletes"),
        (wr["nationality"].nunique(), "Nations"),
    ]

    inner = ""
    for num, lab in chips:
        inner += (
            f'<div class="pool-stat">'
            f'<span class="ps-num">{num}</span>'
            f'<span class="ps-lab">{lab}</span>'
            f'</div>'
        )
    return f'<div class="pool-stats">{inner}</div>'


POOL_FOOT = (
    '<div class="pool-foot">'
    '<span><i style="background:#0A6C9F"></i>Long course</span>'
    '<span><i style="background:#22B8CF"></i>Short course</span>'
    '<span><i style="background:#D6A937"></i>Current record</span>'
    '</div>'
)


# ------------------------------------------------------------
# Swim photos.
# Drop image files into an "assets/" folder next to this script
# (e.g. assets/hero.jpg). If the file is missing, a clean themed
# placeholder is shown instead, so the layout never breaks.
# ------------------------------------------------------------

ASSETS_DIR = Path("assets")


def _img_data_uri(path):
    ext = path.suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{mime};base64,{data}"


def swim_figure(filename, alt="Swimming", ratio="62%", radius=20):
    """Return an HTML figure for a swim photo in assets/, or a placeholder."""
    path = ASSETS_DIR / filename

    if path.exists():
        inner = (
            f'<img src="{_img_data_uri(path)}" alt="{alt}" '
            f'style="object-fit:cover;display:block;"/>'
        )
        ph_class = ""
    else:
        inner = f'<div class="img-ph-label">Add <b>assets/{filename}</b><br>{alt}</div>'
        ph_class = " is-placeholder"

    return (
        f'<div class="swim-figure{ph_class}" style="border-radius:{radius}px;">'
        f'<div class="swim-figure-inner" style="padding-top:{ratio};">{inner}</div>'
        f'</div>'
    )


def page_header(title, subtitle="", image_file=None, alt="Swimming", ratio="120%"):
    """Section header. With an image it becomes a two-column 'title beside photo'
    layout like an editorial spread; without one it falls back to a plain title."""
    if image_file is None:
        section(title, subtitle)
        return

    col_txt, col_img = st.columns([1.45, 1], gap="large")

    with col_txt:
        st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
        st.markdown("<div class='wave-rule'></div>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<div class='section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

    with col_img:
        st.markdown(swim_figure(image_file, alt, ratio=ratio), unsafe_allow_html=True)


# Small pool-header on every page except the Home.
if page != "Home":
    compact_pool_html = (
        '<div class="home-pool compact">'
        '<div class="home-pool-head">'
        f'{brand_html("Records · Rankings · Athletes")}'
        '<div class="home-pool-sub">Select a lane to jump to another section.</div>'
        '</div>'
        f'<div class="home-lanes">{build_pool_lanes()}</div>'
        f'<div class="current-lane">Current lane: <b>{PAGE_LABELS[page]}</b></div>'
        '</div>'
    )
    st.markdown(compact_pool_html, unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## 🏊 Filters")
    st.caption("Use this panel only when a page requires filtering.")
    st.markdown("---")
    st.caption("Gold = current record / best performance. Blue = long course. Aqua = short course.")


# ============================================================
# PAGE 1 - HOME
# ============================================================

if page == "Home":

    # Editorial hero: big poster title + intro + a swimming photo.
    hero_html = (
        '<div class="hero">'
        '<div class="hero-text">'
        '<div class="hero-kicker">World records · Rankings · Athletes</div>'
        '<h1>From records<br>to legends</h1>'
        '<div class="wave-rule"></div>'
        '<p>Dive into more than a century of swimming world records, the all-time '
        'top-200 rankings, and the athletes and nations behind them — then challenge '
        'yourself in the game.</p>'
        '</div>'
        '<div class="hero-media">'
        f'{swim_figure("hero.jpg", "Olympic swimming start", ratio="66%")}'
        '</div>'
        '</div>'
    )

    st.markdown(hero_html, unsafe_allow_html=True)

    # The Home uses the same builder as the other pages: the pool is
    # identical, here just full page (without the "compact" class).
    home_pool_html = (
        '<div class="home-pool">'
        '<div class="home-pool-head">'
        f'{brand_html("World records · Rankings · Athletes · Nations")}'
        '<div class="home-pool-sub">'
        'Eight lanes, one pool. Hover a lane to send the swimmer up, '
        'then click to dive into that section.'
        '</div>'
        f'{home_stats_html()}'
        '</div>'
        f'<div class="home-lanes">{build_pool_lanes()}</div>'
        f'{POOL_FOOT}'
        '</div>'
    )

    st.markdown(home_pool_html, unsafe_allow_html=True)


# ============================================================
# PAGE 2 - WORLD RECORD TIMELINE
# ============================================================

elif page == "World Record Timeline":

    page_header(
        "World Record Timeline",
        "Follow how the fastest official world record in each event changed over time. Lower seconds mean faster performance.",
        image_file="timeline.jpg",
        alt="Vintage Olympic swimming start",
        ratio="70%"
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
# PAGE 3 - ALL-TIME TOP 200 RANKINGS
# ============================================================

elif page == "All-Time Top 200 Rankings":

    page_header(
        "All-Time Top 200 Rankings",
        "Go beyond the world record and explore the depth of elite swimming performances.",
        image_file="top200.jpg",
        alt="Underwater view of swimmers",
        ratio="122%"
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
# PAGE 4 - ATHLETES HALL OF FAME
# ============================================================

elif page == "Athletes Hall of Fame":

    page_header(
        "Athletes Hall of Fame",
        "Explore the swimmers who appear most often in world record history and all-time rankings.",
        image_file="athletes.jpg",
        alt="Swimmer racing butterfly",
        ratio="128%"
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
# PAGE 5 - NATIONS & PLACES
# ============================================================

elif page == "Nations & Places":

    page_header(
        "Nations & Places",
        "Discover which nations and locations appear most frequently in swimming record history and all-time rankings.",
        image_file="nations.jpg",
        alt="Underwater backstroke swimmer",
        ratio="126%"
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
# PAGE 6 - COMPARE EVENTS
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
# PAGE 7 - DATA & METHODS
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


# ============================================================
# PAGE 8 - GAME (SWIM RECORD TOE)
# ============================================================

elif page == "Game":

    page_header(
        "Swim Record Toe",
        "A swimming take on tic-tac-toe: pick a square, connect its row and column criteria, "
        "then name a swimmer who really set a world record matching both. Claim three lanes in a row to win.",
        image_file="game.jpg",
        alt="Swimming goggles by the pool",
        ratio="118%"
    )

    st.markdown(
        """
        <div class="info-box">
        <b>How to play</b><br>
        1. Choose a free square in the pool grid.<br>
        2. Look at the row and column criteria that meet in that square.<br>
        3. Type the swimmer's name or pick it from the dropdown.<br>
        4. If the answer exists in the world record dataset, you claim the lane with ❌ or ⭕.
        </div>
        """,
        unsafe_allow_html=True
    )

    game_df = prepare_swim_game_data(wr)

    if game_df.empty:
        st.error("The game cannot start because the world record dataset has no usable swimmer names.")
        st.stop()

    row_options = {
        "Specific event": "event_label",
        "Event family": "event_family",
        "Stroke": "stroke",
        "Gender": "gender"
    }

    col_options = {
        "Record location / pool": "record_place",
        "Nationality": "nationality",
        "Decade": "decade",
        "Course": "course"
    }

    c_setup_1, c_setup_2, c_setup_3 = st.columns([1, 1, 0.7])

    with c_setup_1:
        row_label = st.selectbox(
            "Rows define",
            list(row_options.keys()),
            index=0,
            key="swim_toe_row_label"
        )

    with c_setup_2:
        col_label = st.selectbox(
            "Columns define",
            list(col_options.keys()),
            index=0,
            key="swim_toe_col_label"
        )

    row_col = row_options[row_label]
    col_col = col_options[col_label]

    with c_setup_3:
        st.write("")
        st.write("")
        new_game = st.button("New game", use_container_width=True)

    state_missing = (
        "swim_toe_board" not in st.session_state
        or "swim_toe_rows" not in st.session_state
        or "swim_toe_cols" not in st.session_state
    )

    axes_changed = (
        st.session_state.get("swim_toe_row_col") != row_col
        or st.session_state.get("swim_toe_col_col") != col_col
    )

    if state_missing or axes_changed or new_game:
        st.session_state.swim_toe_row_col = row_col
        st.session_state.swim_toe_col_col = col_col
        reset_swim_record_toe(game_df, row_col, col_col)

    rows = st.session_state.swim_toe_rows
    cols = st.session_state.swim_toe_cols
    board = st.session_state.swim_toe_board

    if not rows or not cols:
        st.warning("Not enough data to build a 3x3 game board with these criteria. Try another row or column setting.")
        st.stop()

    if st.session_state.swim_toe_score < 9:
        st.markdown(
            """
            <div class="warning-box">
            This board contains one or more very difficult cells.
            Try another <b>New game</b>, or switch from location to nationality/decade for an easier board.
            </div>
            """,
            unsafe_allow_html=True
        )

    c_turn_1, c_turn_2, c_turn_3 = st.columns(3)

    with c_turn_1:
        st.markdown(
            f"""
            <div class="game-turn-card">
            <div class="gt-label">Current turn</div>
            <div class="gt-value" style="font-size:34px;">{st.session_state.swim_toe_turn}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_turn_2:
        claimed = sum(
            1 for i in range(3) for j in range(3)
            if st.session_state.swim_toe_board[i][j] != ""
        )
        st.markdown(
            f"""
            <div class="game-turn-card">
            <div class="gt-label">Claimed lanes</div>
            <div class="gt-value" style="font-size:34px;">{claimed}/9</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_turn_3:
        if st.session_state.swim_toe_winner is None:
            status_text = "Race still open"
        elif st.session_state.swim_toe_winner == "Draw":
            status_text = "Draw"
        else:
            status_text = f"{st.session_state.swim_toe_winner} wins"

        st.markdown(
            f"""
            <div class="game-turn-card">
            <div class="gt-label">Status</div>
            <div class="gt-value" style="font-size:22px;">{status_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")

    # Header row
    header_cols = st.columns(4)
    header_cols[0].markdown("<div class='game-empty-corner'></div>", unsafe_allow_html=True)

    for j in range(3):
        header_cols[j + 1].markdown(
            f"<div class='game-axis-label'>{cols[j]}</div>",
            unsafe_allow_html=True
        )

    # Game grid
    for i in range(3):
        grid_cols = st.columns(4)

        grid_cols[0].markdown(
            f"<div class='game-row-label'>{rows[i]}</div>",
            unsafe_allow_html=True
        )

        for j in range(3):
            current_mark = board[i][j]
            valid_answers = get_cell_answers(game_df, rows[i], cols[j], row_col, col_col)

            if current_mark != "":
                label = f"{current_mark}\n{st.session_state.swim_toe_answers[i][j]}"
                disabled = True
            elif not valid_answers:
                label = "No data"
                disabled = True
            else:
                label = "Dive in"

                if st.session_state.swim_toe_selected == (i, j):
                    label = "Selected"

                disabled = st.session_state.swim_toe_winner is not None

            if grid_cols[j + 1].button(
                label,
                key=f"swim_toe_cell_{i}_{j}",
                use_container_width=True,
                disabled=disabled
            ):
                st.session_state.swim_toe_selected = (i, j)
                st.session_state.swim_toe_feedback = ""
                st.rerun()

    winner = st.session_state.swim_toe_winner

    if winner is not None:
        if winner == "Draw":
            st.success("The race ends in a draw. No more free lanes.")
        else:
            st.success(f"{winner} wins the pool battle!")

    selected = st.session_state.swim_toe_selected

    if selected is not None and st.session_state.swim_toe_winner is None:

        i, j = selected
        row_value = rows[i]
        col_value = cols[j]

        valid_answers = get_cell_answers(game_df, row_value, col_value, row_col, col_col)

        st.markdown(
            f"""
            <div class="info-box">
            <b>Selected square:</b> {row_value} × {col_value}<br>
            Write the swimmer manually or choose a name from the dropdown.
            </div>
            """,
            unsafe_allow_html=True
        )

        all_swimmers = (
            game_df["name"]
            .dropna()
            .astype(str)
            .apply(clean_text)
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        c_ans_1, c_ans_2 = st.columns(2)

        with c_ans_1:
            typed_answer = st.text_input(
                "Write swimmer name",
                placeholder="Example: Michael Phelps",
                key=f"typed_answer_{i}_{j}"
            )

        with c_ans_2:
            dropdown_answer = st.selectbox(
                "Or choose swimmer from dropdown",
                [""] + all_swimmers,
                index=0,
                key=f"dropdown_answer_{i}_{j}"
            )

        answer_to_check = typed_answer.strip() if typed_answer.strip() else dropdown_answer.strip()

        c_submit_1, c_submit_2, c_submit_3 = st.columns([1, 1, 1])

        with c_submit_1:
            submit_answer = st.button("Submit answer", use_container_width=True)

        with c_submit_2:
            clear_selection = st.button("Cancel selection", use_container_width=True)

        with c_submit_3:
            reveal_hint = st.button("Small hint", use_container_width=True)

        if clear_selection:
            st.session_state.swim_toe_selected = None
            st.session_state.swim_toe_feedback = ""
            st.rerun()

        if reveal_hint:
            if valid_answers:
                st.info(f"Hint: there are {len(valid_answers)} valid swimmer(s) for this square.")
            else:
                st.warning("No valid swimmer exists for this square in the dataset.")

        if submit_answer:
            if answer_to_check == "":
                st.warning("Write or select a swimmer before submitting.")
            elif normalize_answer(answer_to_check) in st.session_state.swim_toe_used_names:
                st.warning("This swimmer has already been used in this game. Try another name.")
            else:
                is_correct, matched_name, possible_answers = validate_swim_answer(
                    game_df,
                    answer_to_check,
                    row_value,
                    col_value,
                    row_col,
                    col_col
                )

                if is_correct:
                    st.session_state.swim_toe_board[i][j] = st.session_state.swim_toe_turn
                    st.session_state.swim_toe_answers[i][j] = matched_name
                    st.session_state.swim_toe_used_names.append(normalize_answer(matched_name))

                    new_winner = check_swim_game_winner(st.session_state.swim_toe_board)
                    st.session_state.swim_toe_winner = new_winner

                    if new_winner is None:
                        st.session_state.swim_toe_turn = "⭕" if st.session_state.swim_toe_turn == "❌" else "❌"

                    st.session_state.swim_toe_selected = None
                    st.success(f"Correct! {matched_name} claims the lane.")
                    st.rerun()

                else:
                    st.error("Wrong answer for this square. Try again.")

                    with st.expander("Show possible valid answers for this square"):
                        if possible_answers:
                            st.write(", ".join(possible_answers[:20]))
                        else:
                            st.write("No valid answers available in the dataset.")

    st.markdown("---")

    with st.expander("Used swimmers in this game"):
        if st.session_state.swim_toe_used_names:
            shown_used = [
                st.session_state.swim_toe_answers[i][j]
                for i in range(3)
                for j in range(3)
                if st.session_state.swim_toe_answers[i][j] != ""
            ]
            st.write(", ".join(shown_used))
        else:
            st.write("No swimmer used yet.")

    with st.expander("Why this game belongs in the app"):
        st.markdown(
            """
            This game turns passive exploration into active recall.
            After browsing the records, users can test whether they remember the links between
            swimmers, events, places and historical record moments.
            """
        )
