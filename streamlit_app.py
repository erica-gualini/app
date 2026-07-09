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
    initial_sidebar_state="expanded"
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
        color: #24343B;
    }

    .stApp { background-color: #E9F3F2; }
    .main { background-color: transparent; }

    .block-container { padding-top: 0.7rem; max-width: 1180px; }
    header[data-testid="stHeader"] { background: transparent; }

    .fullbleed {
        position: relative;
        left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw;
        width: 100vw;
    }

    .wave-rule {
        height: 12px;
        margin: 4px 0 12px 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='90' height='12'%3E%3Cpath d='M0 6 q11.25 -6 22.5 0 t22.5 0 t22.5 0 t22.5 0' fill='none' stroke='%230C4A5A' stroke-width='2.4' stroke-linecap='round'/%3E%3C/svg%3E") repeat-x left center / 90px 12px;
        opacity: 0.5;
    }

    /* ============================================================
       SECTION HEADERS — bold condensed poster style (per the deck)
    ============================================================ */

    .section-title {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.006em;
        line-height: 0.95;
        color: #0C4A5A;
        font-size: 42px;
        margin-top: 12px;
        margin-bottom: 8px;
    }

    .section-subtitle {
        color: #5A7480;
        font-size: 16.5px;
        font-weight: 500;
        max-width: 840px;
        margin-bottom: 18px;
        line-height: 1.55;
    }

    /* ============================================================
       HOME TOP BAND — title + short description + doodles
    ============================================================ */

    .swim-band {
        position: relative;
        overflow: hidden;
        display: grid;
        grid-template-columns: auto 1fr auto;
        align-items: center;
        gap: 24px;
        background: #FBFEFE;
        border: 1px solid #D8E9E8;
        border-radius: 22px;
        padding: 22px 30px;
        margin: 4px 0 22px 0;
        box-shadow: 0 18px 40px -28px rgba(12,74,90,0.5);
    }

    .swim-band-icon .brand-logo {
        width: 56px; height: 56px;
        filter: drop-shadow(0 8px 16px rgba(12,74,90,0.28));
    }

    .swim-band-title {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.01em;
        line-height: 0.94;
        font-size: 40px;
        color: #0C4A5A;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .swim-sparkle { width: 22px; height: 22px; flex: none; }

    .swim-band-desc {
        margin-top: 8px;
        font-size: 15px;
        font-weight: 500;
        color: #4A6470;
        line-height: 1.5;
        max-width: 720px;
    }

    .swim-band-waves {
        width: 116px; height: 66px;
        border-radius: 14px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='58' height='15'%3E%3Cpath d='M0 8 q7.25 -7 14.5 0 t14.5 0 t14.5 0 t14.5 0' fill='none' stroke='%230C4A5A' stroke-width='2.6' stroke-linecap='round'/%3E%3C/svg%3E") repeat, #EAF6F5;
        background-size: 58px 15px, 100% 100%;
        border: 1px solid #D8E9E8;
        box-shadow: inset 0 0 0 3px #FBFEFE;
    }

    @media (max-width: 850px) {
        .swim-band { grid-template-columns: auto 1fr; padding: 18px 20px; }
        .swim-band-waves { display: none; }
        .swim-band-title { font-size: 30px; }
    }

    /* ============================================================
       MINI POOL — the little pool used as header on inner pages
    ============================================================ */

    .mini-pool {
        background: #FBFEFE;
        border: 1px solid #D8E9E8;
        border-radius: 22px;
        padding: 14px 16px 16px 16px;
        margin: 2px 0 24px 0;
        box-shadow: 0 18px 40px -30px rgba(12,74,90,0.5);
    }

    .mini-pool-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 14px;
        flex-wrap: wrap;
        margin: 2px 6px 12px 6px;
    }

    .mini-pool-brand {
        display: inline-flex;
        align-items: center;
        gap: 9px;
    }

    .mini-pool-brand .brand-logo { width: 30px; height: 30px; }

    .mini-pool-brand span {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.01em;
        font-size: 20px;
        color: #0C4A5A;
    }

    .mini-pool-current {
        font-size: 12.5px;
        font-weight: 600;
        color: #5A7480;
    }

    .mini-pool-current b { color: #0C4A5A; }

    /* ============================================================
       POOL LANES (full on Home, compact via .mini)
    ============================================================ */

    .home-lanes {
        position: relative;
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        gap: 0;
        overflow: hidden;
        background:
            url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='130'%20height='44'%3E%3Cpath%20d='M0%2022%20Q16.25%2014%2032.5%2022%20T65%2022%20T97.5%2022%20T130%2022'%20fill='none'%20stroke='%23FFFFFF'%20stroke-opacity='0.12'%20stroke-width='2'%20stroke-linecap='round'/%3E%3C/svg%3E") repeat,
            url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='220'%20height='74'%3E%3Cpath%20d='M0%2037%20Q27.5%2025%2055%2037%20T110%2037%20T165%2037%20T220%2037'%20fill='none'%20stroke='%23FFFFFF'%20stroke-opacity='0.07'%20stroke-width='3'%20stroke-linecap='round'/%3E%3C/svg%3E") repeat,
            linear-gradient(180deg, #8FD0D6 0%, #2C8093 55%, #145A6B 100%);
        background-size: 130px 44px, 220px 74px, 100% 100%;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.30), inset 0 18px 44px rgba(5,40,50,0.18);
        animation: home-water-drift 26s linear infinite;
    }

    .home-lanes.mini { border-radius: 16px; }

    @keyframes home-water-drift {
        from { background-position: 0 0, 0 0, 0 0; }
        to   { background-position: 130px 44px, -220px 74px, 0 0; }
    }

    .home-lane {
        position: relative;
        display: block;
        min-height: 62vh;
        overflow: hidden;
        text-decoration: none !important;
        transition: background 0.25s ease;
    }

    .home-lanes.mini .home-lane { min-height: 116px; }

    .home-lane:hover { background: rgba(255,255,255,0.08); }

    .pool-rope {
        position: absolute;
        top: 0; bottom: 0;
        width: 6px;
        transform: translateX(-50%);
        z-index: 2;
        pointer-events: none;
        background:
            repeating-linear-gradient(180deg, #E45A63 0px 12px, transparent 12px 22px) center top / 4px 100% no-repeat,
            linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.6)) center top / 1.5px 100% no-repeat;
    }

    .pool-rope:nth-of-type(1) { left: 12.5%; }
    .pool-rope:nth-of-type(2) { left: 25%; }
    .pool-rope:nth-of-type(3) { left: 37.5%; }
    .pool-rope:nth-of-type(4) { left: 50%; }
    .pool-rope:nth-of-type(5) { left: 62.5%; }
    .pool-rope:nth-of-type(6) { left: 75%; }
    .pool-rope:nth-of-type(7) { left: 87.5%; }

    .hl-line {
        position: absolute;
        left: 50%; top: 12%; bottom: 5%;
        width: 4px;
        transform: translateX(-50%);
        z-index: 1;
        pointer-events: none;
        background: rgba(5,40,50,0.16);
        border-radius: 2px;
    }

    .hl-line::before, .hl-line::after {
        content: "";
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 22px; height: 4px;
        background: rgba(5,40,50,0.16);
        border-radius: 2px;
    }

    .hl-line::before { top: 0; }
    .hl-line::after { bottom: 0; }
    .home-lanes.mini .hl-line { top: 8%; bottom: 6%; }

    .hl-btn {
        position: relative;
        z-index: 3;
        display: block;
        margin: 16px 12px 0 12px;
        padding: 12px 7px;
        text-align: center;
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(255,255,255,0.9);
        border-radius: 14px;
        box-shadow: 0 12px 26px -14px rgba(5,40,50,0.5);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .home-lanes.mini .hl-btn { margin: 12px 6px 0 6px; padding: 8px 4px; border-radius: 11px; }

    .hl-name {
        display: block;
        font-family: 'Anton', system-ui, sans-serif;
        color: #0C4A5A;
        font-size: 16px;
        font-weight: 400;
        text-transform: uppercase;
        line-height: 1.05;
        letter-spacing: 0.02em;
    }

    .home-lanes.mini .hl-name { font-size: 13px; }

    .hl-tag {
        display: block;
        color: #5A7480;
        font-size: 9.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 5px;
        line-height: 1.15;
    }

    .home-lanes.mini .hl-tag { font-size: 8px; margin-top: 3px; }

    .home-lane:hover .hl-btn {
        transform: translateY(-3px);
        border-color: #C9A24B;
        box-shadow: 0 18px 32px -14px rgba(5,40,50,0.55);
    }

    .home-lane.active .hl-btn { border-color: #C9A24B; }

    .hl-num {
        position: absolute;
        bottom: 16px; left: 0; right: 0;
        z-index: 1;
        text-align: center;
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 44px;
        font-weight: 400;
        line-height: 1;
        color: rgba(255,255,255,0.34);
        pointer-events: none;
    }

    .home-lanes.mini .hl-num { font-size: 26px; bottom: 8px; }

    .home-lane::after {
        content: "";
        position: absolute;
        top: 100%; left: 50%;
        z-index: 4;
        width: 40px; height: 62px;
        background: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2044%2070'%3E%3Cg%20fill='none'%20stroke='%23FFFFFF'%20stroke-width='4.6'%20stroke-linecap='round'%3E%3Cpath%20d='M15%2020%20L12%204'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='-6%2015%2020%3B16%2015%2020%3B-6%2015%2020'%20dur='1s'%20repeatCount='indefinite'/%3E%3C/path%3E%3Cpath%20d='M29%2020%20L37%2032'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='12%2029%2020%3B-14%2029%2020%3B12%2029%2020'%20dur='1s'%20repeatCount='indefinite'/%3E%3C/path%3E%3Cpath%20d='M19.5%2046%20L17.5%2064'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='-9%2019.5%2046%3B9%2019.5%2046%3B-9%2019.5%2046'%20dur='0.4s'%20repeatCount='indefinite'/%3E%3C/path%3E%3Cpath%20d='M24.5%2046%20L26.5%2062'%3E%3CanimateTransform%20attributeName='transform'%20type='rotate'%20values='9%2024.5%2046%3B-9%2024.5%2046%3B9%2024.5%2046'%20dur='0.4s'%20repeatCount='indefinite'/%3E%3C/path%3E%3C/g%3E%3Ccircle%20cx='22'%20cy='13'%20r='5.6'%20fill='%23FFFFFF'/%3E%3Cpath%20d='M15%2020%20Q22%2015.5%2029%2020%20L26%2045.5%20Q22%2048.5%2018%2045.5%20Z'%20fill='%23FFFFFF'/%3E%3C/svg%3E") center / contain no-repeat;
        opacity: 0;
        transform: translate(-50%, -50%);
        filter: drop-shadow(0 4px 8px rgba(5,40,50,0.35));
        pointer-events: none;
    }

    .home-lanes.mini .home-lane::after { width: 24px; height: 38px; }

    .home-lane:hover::after {
        animation: swim-up 1.7s cubic-bezier(0.3, 0.55, 0.35, 1) forwards;
    }

    @keyframes swim-up {
        0%   { opacity: 0; top: 100%; transform: translate(-50%, -50%) rotate(0deg); }
        7%   { opacity: 1; }
        30%  { transform: translate(-56%, -50%) rotate(-3deg); }
        55%  { transform: translate(-44%, -50%) rotate(3deg); }
        80%  { transform: translate(-53%, -50%) rotate(-2deg); }
        100% { opacity: 1; top: 14%; transform: translate(-50%, -50%) rotate(0deg); }
    }

    @media (max-width: 1150px) {
        .home-lanes { grid-template-columns: repeat(4, 1fr); }
        .home-lane { min-height: 44vh; }
        .home-lanes.mini .home-lane { min-height: 100px; }
        .pool-rope { display: none; }
        .pool-rope:nth-of-type(2n) { display: block; }
    }

    @media (max-width: 650px) {
        .home-lanes { grid-template-columns: repeat(2, 1fr); }
        .home-lane { min-height: 36vh; }
        .home-lanes.mini .home-lane { min-height: 92px; }
        .pool-rope:nth-of-type(2n) { display: none; }
        .pool-rope:nth-of-type(4) { display: block; }
    }

    .pool-foot {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 22px;
        margin: 18px 0 6px 0;
        font-size: 12.5px;
        font-weight: 600;
        color: #5A7480;
    }

    .pool-foot span { display: inline-flex; align-items: center; gap: 7px; }
    .pool-foot i { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }

    /* ============================================================
       CARDS / CALLOUTS
    ============================================================ */

    .kpi-card {
        background-color: #FFFFFF;
        padding: 22px 22px;
        border-radius: 18px;
        border: 1px solid #D8E9E8;
        box-shadow: 0 14px 30px -22px rgba(12,74,90,0.45);
        min-height: 130px;
    }

    .kpi-label {
        font-size: 12px; text-transform: uppercase; color: #5A7480;
        font-weight: 700; letter-spacing: 0.1em;
    }

    .kpi-value {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400; font-size: 44px; color: #0C4A5A;
        margin-top: 6px; line-height: 1;
    }

    .kpi-note { font-size: 13px; color: #5A7480; margin-top: 5px; }

    .info-box {
        background-color: #FFFFFF;
        border-left: 5px solid #1B6E7E;
        border-radius: 16px; padding: 18px 22px; margin: 16px 0;
        box-shadow: 0 14px 30px -24px rgba(12,74,90,0.4);
        color: #2A3B42;
    }

    .warning-box {
        background-color: #FBF4E2;
        border-left: 5px solid #C9A24B;
        border-radius: 16px; padding: 18px 22px; margin: 16px 0;
        color: #4A3E1E;
    }

    .small-caption { font-size: 13px; color: #5A7480; line-height: 1.45; }
    div[data-testid="stMetricValue"] { color: #0C4A5A; }
    div[data-testid="stSidebar"] { background-color: #DFF0EF; }

    /* stat chips kept available (not used on Home now) */
    .pool-stats { display: flex; justify-content: center; flex-wrap: wrap; gap: 12px 40px; margin: 22px auto 6px auto; }
    .pool-stat { display: flex; flex-direction: column; align-items: center; background: transparent; border: none; box-shadow: none; padding: 0; }
    .ps-num { font-family: 'Anton', system-ui, sans-serif; font-weight: 400; font-size: 34px; line-height: 1; color: #0C4A5A; }
    .ps-lab { margin-top: 2px; font-size: 10.5px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #5A7480; }

    /* ============================================================
       SWIM PHOTOS (with graceful placeholder)
    ============================================================ */

    .swim-figure {
        position: relative; overflow: hidden;
        border-radius: 20px; border: 1px solid #D8E9E8;
        box-shadow: 0 24px 50px -30px rgba(12,74,90,0.55);
        background: #CFE6E6;
    }

    .swim-figure-inner { position: relative; width: 100%; }

    .swim-figure-inner > img,
    .swim-figure-inner > .img-ph-label {
        position: absolute; inset: 0; width: 100%; height: 100%;
    }

    .swim-figure-inner > img { object-fit: cover; display: block; }

    .swim-figure.is-placeholder {
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='40'%3E%3Cg fill='none' stroke='%231B6E7E' stroke-opacity='0.26' stroke-width='2.2' stroke-linecap='round'%3E%3Cpath d='M0 12 q15 -8 30 0 t30 0 t30 0 t30 0'/%3E%3Cpath d='M0 28 q15 -8 30 0 t30 0 t30 0 t30 0'/%3E%3C/g%3E%3C/svg%3E") repeat, linear-gradient(135deg, #E6F0EC 0%, #CFE6E6 100%);
    }

    .img-ph-label {
        display: flex; align-items: center; justify-content: center;
        text-align: center; color: #3C6672;
        font-weight: 600; font-size: 14px; line-height: 1.4; padding: 18px;
    }

    .img-ph-label b { color: #1B6E7E; }

    /* ============================================================
       SWIM RECORD TOE — GAME
    ============================================================ */

    .game-turn-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #E4F2F1 100%);
        border: 1px solid #D8E9E8; border-radius: 20px;
        padding: 16px 20px; box-shadow: 0 10px 24px -16px rgba(12,74,90,0.4);
        color: #0C4A5A; text-align: center;
    }

    .game-turn-card .gt-label {
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.09em;
        font-weight: 700; color: #5A7480;
    }

    .game-turn-card .gt-value {
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400; color: #0C4A5A; margin-top: 4px; line-height: 1.05;
    }

    .game-axis-label {
        font-family: 'Anton', system-ui, sans-serif;
        text-transform: uppercase; letter-spacing: 0.02em;
        font-size: 15px; font-weight: 400;
        background: #0C4A5A; color: white; border-radius: 16px;
        padding: 12px 10px; text-align: center; min-height: 64px;
        display: flex; align-items: center; justify-content: center;
        line-height: 1.1; box-shadow: 0 10px 20px -10px rgba(12,74,90,0.4);
    }

    .game-row-label {
        font-family: 'Anton', system-ui, sans-serif;
        text-transform: uppercase; letter-spacing: 0.02em;
        font-size: 15px; font-weight: 400;
        background: linear-gradient(135deg, #1B6E7E 0%, #2C8093 100%); color: white;
        border-radius: 16px; padding: 12px 10px; text-align: center; min-height: 72px;
        display: flex; align-items: center; justify-content: center;
        line-height: 1.1; box-shadow: 0 10px 20px -10px rgba(12,74,90,0.35);
    }

    .game-empty-corner { background: transparent; min-height: 64px; }

    div[data-testid="stButton"] button {
        font-family: 'Barlow', system-ui, sans-serif;
        border-radius: 16px;
        border: 1.5px solid rgba(27,110,126,0.28);
        background: linear-gradient(135deg, #EAF6F5 0%, #C7E7E7 48%, #9AD5D6 100%);
        color: #0C4A5A; font-weight: 700; min-height: 62px;
        box-shadow: 0 10px 22px -14px rgba(12,74,90,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        white-space: pre-line;
    }

    div[data-testid="stButton"] button:hover {
        border-color: #1B6E7E; transform: translateY(-2px);
        box-shadow: 0 16px 28px -14px rgba(12,74,90,0.4);
    }

    div[data-testid="stButton"] button:disabled {
        background: #E1EEED; color: #7A93A0; border-color: #D2E6E5;
        box-shadow: none; transform: none;
    }

    /* ============================================================
       HOME HEADER — free, poster-style, fills the whole top area.
       Logo + kicker line, big two-tone title (no box), tagline,
       waves + site description.
    ============================================================ */

    .home-head { margin: 2px 0 14px 0; }

    .home-topline {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 12px;
    }

    .home-logo .brand-logo {
        width: 46px;
        height: 46px;
        flex: none;
        filter: drop-shadow(0 8px 16px rgba(12,74,90,0.28));
    }

    .home-kicker {
        flex: 1;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #1B6E7E;
        line-height: 1.2;
    }

    .home-chevrons {
        color: #22B8CF;
        font-weight: 800;
        letter-spacing: -0.08em;
        font-size: 22px;
        flex: none;
    }

    .home-title {
        margin: 0;
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        line-height: 0.86;
        letter-spacing: 0.01em;
        color: #0C4A5A;
        font-size: clamp(46px, 6.4vw, 88px);
    }

    .home-title .l2 { color: #C9A24B; }

    /* two-column body: text on the left, photo on the right (fills the space) */
    .home-main {
        display: grid;
        grid-template-columns: 1.3fr 0.82fr;
        gap: 34px;
        align-items: stretch;
        margin-top: 2px;
    }

    .home-media {
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        min-height: 240px;
        border: 1px solid #D2E6E5;
        box-shadow: 0 22px 46px -28px rgba(12,74,90,0.55);
        background: #CFE6E6;
    }

    .home-media img {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .home-media .img-ph-label {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .home-tagline {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        margin: 10px 0 12px 0;
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        font-size: clamp(20px, 2.7vw, 34px);
        line-height: 1;
        color: #1B6E7E;
    }

    .home-tagline .chev {
        color: #22B8CF;
        font-family: 'Barlow', system-ui, sans-serif;
        font-weight: 800;
        font-size: 0.66em;
        letter-spacing: -0.08em;
    }

    .home-waves {
        display: flex;
        gap: 10px;
        align-items: center;
        margin: 2px 0 12px 0;
    }

    .home-waves span {
        display: block;
        height: 9px;
        flex: 1;
        max-width: 260px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='42' height='9'%3E%3Cpath d='M0 4.5 q5.25 -4.5 10.5 0 t10.5 0 t10.5 0 t10.5 0' fill='none' stroke='%231B6E7E' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E") repeat-x left center / 42px 9px;
        opacity: 0.5;
    }

    .home-waves span:nth-child(2) { max-width: 180px; }
    .home-waves span:nth-child(3) { max-width: 110px; }

    .home-desc {
        margin: 0;
        font-size: 16.5px;
        font-weight: 500;
        color: #3E5964;
        line-height: 1.5;
    }

    .home-desc b { color: #0C4A5A; }

    @media (max-width: 850px) {
        .home-main { grid-template-columns: 1fr; gap: 18px; }
        .home-media { min-height: 200px; }
        .home-title { font-size: 46px; }
        .home-tagline { font-size: 20px; }
    }

    /* ============================================================
       CINEMATIC HOME HERO — full-bleed, dark, poster style
    ============================================================ */

    .home-cine {
        position: relative;
        overflow: hidden;
        min-height: 56vh;
        display: flex;
        align-items: center;
        background: #06222B;
        margin-bottom: 12px;
    }

    .cine-bg { position: absolute; inset: 0; z-index: 0; }
    .cine-bg img {
        width: 100%; height: 100%;
        object-fit: cover;
        filter: brightness(0.5) saturate(0.85) contrast(1.05);
    }

    .cine-overlay {
        position: absolute; inset: 0; z-index: 1;
        background:
            linear-gradient(90deg, rgba(4,22,28,0.97) 0%, rgba(4,22,28,0.86) 28%, rgba(4,22,28,0.45) 55%, rgba(4,22,28,0.35) 100%),
            linear-gradient(180deg, rgba(4,22,28,0.35) 0%, rgba(4,22,28,0.15) 45%, rgba(4,22,28,0.55) 100%);
    }

    .cine-inner {
        position: relative;
        z-index: 4;
        width: 100%;
        max-width: 1560px;
        margin: 0 auto;
        padding: 5vh clamp(26px, 6vw, 96px);
        display: grid;
        grid-template-columns: 1.12fr 0.88fr;
        gap: 30px;
        align-items: center;
    }

    .cine-kicker {
        display: flex;
        align-items: center;
        gap: 11px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.17em;
        text-transform: uppercase;
        color: #6FD3DE;
        margin-bottom: 16px;
    }

    .cine-kicker .brand-logo { width: 42px; height: 42px; flex: none; }

    .cine-title {
    margin: 0;
    font-family: 'Anton', system-ui, sans-serif;
    font-weight: 400;
    text-transform: uppercase;
    color: #E7B94A !important;
    font-size: clamp(92px, 12vw, 180px);
    line-height: 0.82;
    letter-spacing: 0.01em;
    transform: skewX(-8deg);
    transform-origin: left;
    text-shadow: 0 12px 38px rgba(0,0,0,0.62);
}

.cine-title span,
.cine-title .gold {
    color: #E7B94A !important;
}

    .cine-tag {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        margin: 18px 0 14px 0;
        font-family: 'Anton', system-ui, sans-serif;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        font-size: clamp(20px, 2.7vw, 34px);
        line-height: 1;
        color: #6FD3DE;
        transform: skewX(-8deg);
        transform-origin: left;
    }

    .cine-tag .chev {
        color: #FFFFFF;
        font-family: 'Barlow', system-ui, sans-serif;
        font-weight: 800;
        font-size: 0.6em;
        letter-spacing: -0.06em;
    }

    .cine-desc {
        margin: 0;
        max-width: 560px;
        color: #C7DBDE;
        font-size: 16px;
        font-weight: 500;
        line-height: 1.5;
    }

    .cine-desc b { color: #FFFFFF; }

    .cine-cards {
        position: relative;
        height: 44vh;
        min-height: 300px;
    }

    .cine-card {
        position: absolute;
        border-radius: 10px;
        overflow: hidden;
        border: 3px solid rgba(255,255,255,0.92);
        box-shadow: 0 34px 60px -22px rgba(0,0,0,0.65);
    }

    .cine-card img { width: 100%; height: 100%; object-fit: cover; display: block; }

    .cine-card.c1 { width: 46%; height: 76%; top: 6%; left: 6%; transform: rotate(-6deg); z-index: 2; }
    .cine-card.c2 { width: 46%; height: 86%; top: 10%; left: 46%; transform: rotate(5deg); z-index: 3; }

    .cine-chev {
        position: absolute;
        z-index: 5;
        color: #FFFFFF;
        font-family: 'Barlow', system-ui, sans-serif;
        font-weight: 800;
        letter-spacing: 0.02em;
        font-size: 26px;
        opacity: 0.95;
        text-shadow: 0 4px 14px rgba(0,0,0,0.5);
    }

    .cine-chev.tr { top: 56px; right: 40px; }
    .cine-chev.br { bottom: 20px; left: 50%; transform: translateX(-50%); }

@media (max-width: 900px) {
    .cine-inner { grid-template-columns: 1fr; padding: 4vh 24px; }
    .cine-cards { display: none; }
    .cine-title { font-size: 72px; }
    .home-cine { min-height: 48vh; }
}


    .fact-box {
        margin: -14px 0 28px 0;
        max-width: 680px;
        background: linear-gradient(135deg, #FFFFFF 0%, #EAF6F5 100%);
        border: 1px solid #D8E9E8;
        border-left: 6px solid #C9A24B;
        border-radius: 18px;
        padding: 18px 22px;
        box-shadow: 0 18px 38px -28px rgba(12,74,90,0.55);
    }

    .timeline-record-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #EAF6F5 100%);
        border: 1px solid #D8E9E8;
        border-left: 6px solid #C9A24B;
        border-radius: 18px;
        padding: 16px 20px;
        margin-top: 2px;
        box-shadow: 0 16px 34px -26px rgba(12,74,90,0.55);
    }

    .timeline-control-row {
        margin-top: 18px;
        margin-bottom: 28px;
    }

    .timeline-metrics-row {
        margin-top: 10px;
        margin-bottom: 26px;
    }

    .timeline-chart-spacer {
        height: 10px;
    }


    .timeline-record-kicker {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #C9A24B;
        margin-bottom: 6px;
    } 

    .timeline-record-main {
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 30px;
        line-height: 1.05;
        color: #0C4A5A;
        text-transform: uppercase;
    }

    .timeline-record-sub {
        margin-top: 7px;
        font-size: 14px;
        font-weight: 500;
        color: #3E5964;
        line-height: 1.4;
    }

    .timeline-selector-note {
        font-size: 13px;
        font-weight: 500;
        color: #5A7480;
        margin-top: -6px;
        margin-bottom: 8px;
    }

    .fact-kicker {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #C9A24B;
        margin-bottom: 7px;
    }

    .fact-text {
        font-size: 16px;
        font-weight: 500;
        line-height: 1.5;
        color: #24343B;
    }

    .fact-text b {
        color: #0C4A5A;
    }

    .glossary-wrap {
        max-width: 1100px;
        margin: 34px auto 10px auto;
        padding: 0 8px;
    }

    .glossary-title {
        font-family: 'Anton', system-ui, sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        font-size: 26px;
        color: #0C4A5A;
        margin-bottom: 4px;
    }

    .glossary-intro {
        font-size: 14.5px;
        font-weight: 500;
        color: #5A7480;
        margin-bottom: 16px;
    }

    .glossary-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }

    .glossary-item {
        flex: 1 1 240px;
        background: linear-gradient(135deg, #FFFFFF 0%, #EAF6F5 100%);
        border: 1px solid #D8E9E8;
        border-left: 5px solid #C9A24B;
        border-radius: 14px;
        padding: 12px 16px;
    }

    .glossary-term {
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 19px;
        color: #0C4A5A;
        letter-spacing: 0.02em;
    }

    .glossary-def {
        font-size: 13.5px;
        font-weight: 500;
        color: #3E5964;
        line-height: 1.45;
        margin-top: 3px;
    }

    .athlete-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #EAF6F5 100%);
        border: 1px solid #D8E9E8;
        border-left: 6px solid #C9A24B;
        border-radius: 18px;
        padding: 20px 24px;
        margin: 6px 0 18px 0;
        box-shadow: 0 18px 38px -28px rgba(12,74,90,0.55);
    }

    .athlete-card-kicker {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #C9A24B;
        margin-bottom: 6px;
    }

    .athlete-card-name {
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 34px;
        line-height: 1.05;
        color: #0C4A5A;
        text-transform: uppercase;
    }

    .athlete-card-meta {
        margin-top: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #3E5964;
        line-height: 1.5;
    }

    .athlete-stat-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
    }

    .athlete-stat {
        flex: 1 1 110px;
        background: rgba(255,255,255,0.75);
        border: 1px solid #D8E9E8;
        border-radius: 12px;
        padding: 10px 12px;
        text-align: center;
    }

    .athlete-stat-value {
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 24px;
        color: #0C4A5A;
        line-height: 1.1;
    }

    .athlete-stat-label {
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: #5A7480;
        margin-top: 4px;
    }

    .vs-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 160px;
    }

    .vs-badge-inner {
        font-family: 'Anton', system-ui, sans-serif;
        font-size: 46px;
        color: #C9A24B;
        background: #FFFFFF;
        border: 3px solid #C9A24B;
        border-radius: 50%;
        width: 92px;
        height: 92px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 16px 34px -24px rgba(12,74,90,0.65);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def fix_mojibake(value):
    """Repair double-encoded text (UTF-8 read as cp1252/latin-1).

    The source files contain artefacts like "ZoltAn" or "4x100m" where the
    original accented characters were mangled. Re-encoding and decoding
    restores them. Applied repeatedly because some strings were mangled twice.
    """
    for _ in range(3):
        if not any(marker in value for marker in ("\u00c3", "\u00c2", "\u00e2\u20ac")):
            break
        repaired = None
        for encoding in ("cp1252", "latin-1"):
            try:
                repaired = value.encode(encoding).decode("utf-8")
                break
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
        if repaired is None or repaired == value:
            break
        value = repaired
    return value


def clean_text(value):
    """Clean text values, repairing mojibake and collapsing whitespace."""
    if pd.isna(value):
        return ""
    value = fix_mojibake(str(value))
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def athlete_key(value):
    """A single identity key shared by both datasets.

    The world record file writes "Jonty Skinner", the top-200 file writes
    "SKINNER, Jonty". Without this key the same swimmer never matches across
    the two sources. Accents are folded so "Zoltan" and "Zoltán" agree.
    """
    if not isinstance(value, str):
        return ""
    text = clean_text(value)
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )
    if "," in text:
        last, first = text.split(",", 1)
        text = f"{first.strip()} {last.strip()}"
    text = re.sub(r"[^A-Za-z ]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def pretty_name(value):
    """Turn 'SKINNER, Jonty' into 'Jonty Skinner'; leave normal names alone."""
    text = clean_text(value)
    if "," in text:
        last, first = text.split(",", 1)
        text = f"{first.strip()} {last.strip()}"
    parts = [p.capitalize() if p.isupper() else p for p in text.split()]
    return " ".join(parts)


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
        font=dict(family="Arial", size=13, color=NAVY),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=70, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    if title:
        fig.update_layout(title=title, title_font=dict(size=22, color=NAVY))
    fig.update_xaxes(showgrid=True, gridcolor="rgba(5,43,68,0.10)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(5,43,68,0.10)", zeroline=False)
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
        # pandas >= 3 returns StringDtype (not object) for text columns, so a
        # plain object check would silently skip cleaning them.
        if df[col].dtype == "object" or pd.api.types.is_string_dtype(df[col]):
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

    # Relay rows store four swimmers concatenated in a single "name" cell
    # (e.g. "Steve Clark (52.9)Mike Austin..."). Flag them so athlete-level
    # views can exclude them instead of treating the blob as one person.
    if "event" in df.columns:
        df["is_relay"] = df["event"].astype(str).str.contains("Relay", case=False, na=False)
    else:
        df["is_relay"] = False

    df["athlete_key"] = np.where(df["is_relay"], "", df["name"].apply(athlete_key))

    df = df.sort_values(["event_label", "date", "seconds"], ascending=[True, True, True])

    return df


@st.cache_data
def load_top_performances():
    if not TOP_FILE.exists():
        return pd.DataFrame()

    df = pd.read_excel(TOP_FILE)
    df.columns = [snake_case(c) for c in df.columns]

    for col in df.columns:
        # pandas >= 3 returns StringDtype (not object) for text columns, so a
        # plain object check would silently skip cleaning them.
        if df[col].dtype == "object" or pd.api.types.is_string_dtype(df[col]):
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

    df["is_relay"] = df["event_label"].astype(str).str.contains("Relay", case=False, na=False)
    df["athlete_key"] = np.where(df["is_relay"], "", df["athlete"].apply(athlete_key))

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

    # Relay rows hold four swimmers in one cell, so they can never be a valid
    # single-name answer in the quiz.
    if "is_relay" in game_df.columns:
        game_df = game_df[~game_df["is_relay"]].copy()

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
        link_target = "_blank" if page_name == "Game" else "_self"
        lanes += (
            f'<a class="home-lane{active_class}" href="?page={page_url}" target="{link_target}">'
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
# Brand logo (inline SVG): a stopwatch — for records/times — whose
# dial holds swimming waves, with a gold hand and crown (achievement).
# Recalls both swimming and records.
# ------------------------------------------------------------

LOGO_SVG = (
    '<svg class="brand-logo" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">'
    '<defs><linearGradient id="swlg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#0C4A5A"/>'
    '<stop offset="0.55" stop-color="#1B6E7E"/>'
    '<stop offset="1" stop-color="#22B8CF"/>'
    '</linearGradient></defs>'
    '<rect x="1" y="1" width="46" height="46" rx="13" fill="url(#swlg)"/>'
    # stopwatch crown + gold button
    '<rect x="21.5" y="5.5" width="5" height="4.6" rx="1.6" fill="#FFFFFF"/>'
    '<circle cx="24" cy="4.2" r="2.6" fill="#C9A24B"/>'
    # dial
    '<circle cx="24" cy="28" r="14" fill="#FFFFFF"/>'
    # swimming waves inside the dial
    '<path d="M13 33 q2.75 -3.2 5.5 0 t5.5 0 t5.5 0" fill="none" '
    'stroke="#0C4A5A" stroke-width="2.2" stroke-linecap="round"/>'
    '<path d="M14.5 37 q2.4 -2.8 4.8 0 t4.8 0 t4.8 0" fill="none" '
    'stroke="#1B6E7E" stroke-width="1.8" stroke-linecap="round" opacity="0.55"/>'
    # timer hand + pin (record accent)
    '<path d="M24 28 L24 16.5" fill="none" stroke="#C9A24B" '
    'stroke-width="2.6" stroke-linecap="round"/>'
    '<circle cx="24" cy="28" r="1.9" fill="#C9A24B"/>'
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
    names = set(wr.loc[wr["athlete_key"] != "", "athlete_key"]) | set(
        top.loc[top["athlete_key"] != "", "athlete_key"]
    )
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


def render_home_head():
    """Full-bleed cinematic Home hero (dark poster style): dark swim photo,
    big skewed white title, cyan tagline, tilted photo cards and chevrons."""

    def uri(name):
        p = ASSETS_DIR / name
        return _img_data_uri(p) if p.exists() else ""

    bg = uri("home_side.jpg")
    c1 = uri("athletes.jpg")
    c2 = uri("nations.jpg")

    bg_html = f'<div class="cine-bg"><img src="{bg}" alt=""/></div>' if bg else ''
    card1 = f'<div class="cine-card c1"><img src="{c1}" alt=""/></div>' if c1 else ''
    card2 = f'<div class="cine-card c2"><img src="{c2}" alt=""/></div>' if c2 else ''
    cards = f'<div class="cine-cards">{card1}{card2}</div>' if (c1 or c2) else '<div></div>'

    html = (
        '<div class="fullbleed home-cine">'
        f'{bg_html}'
        '<div class="cine-overlay"></div>'
        '<div class="cine-chev tr">&#187;&#187;&#187;&#187;&#187;</div>'
        '<div class="cine-chev br">&#187;&#187;&#187;&#187;&#187;</div>'
        '<div class="cine-inner">'
        '<div class="cine-text">'
        f'<div class="cine-kicker">{LOGO_SVG}<span>World records &middot; Rankings &middot; Athletes &middot; Nations</span></div>'
        '<h1 class="cine-title">Swim <span class="gold">Records</span><br>Explorer</h1>'
        '<div class="cine-tag">'
        'Let\'s dive in and swim through records '
        '<span class="chev">&#187;&#187;&#187;</span>'
        '</div>'
        '<p class="cine-desc">'
        'A century of official <b>world records</b>, all-time <b>top-200</b> rankings, and '
        'the swimmers, nations and pools behind every mark — plus a game to test yourself. '
        'Pick a lane below to dive in.'
        '</p>'
        '</div>'
        f'{cards}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_compact_pool(active_page):
    """Little pool used as the header/navigation on inner pages."""
    html = (
        '<div class="mini-pool">'
        '<div class="mini-pool-head">'
        f'<span class="mini-pool-brand">{LOGO_SVG}<span>Swim Records Explorer</span></span>'
        f'<span class="mini-pool-current">You are in <b>{PAGE_LABELS[active_page]}</b></span>'
        '</div>'
        f'<div class="home-lanes mini">{build_pool_lanes()}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# Inner pages get the little pool as their header; the Home builds its own below.
if page != "Home":
    render_compact_pool(page)


if page in ("World Record Timeline", "All-Time Top 200 Rankings", "Nations & Places", "Compare Events"):
    with st.sidebar:
        st.markdown("## 🏊 Filters")


# ============================================================
# PAGE 1 - HOME
# ============================================================

if page == "Home":

    # The sidebar has no purpose on the Home — hide it completely here.
    st.markdown(
        "<style>"
        "section[data-testid='stSidebar']{display:none !important;}"
        "div[data-testid='stSidebarCollapsedControl']{display:none !important;}"
        "[data-testid='collapsedControl']{display:none !important;}"
        "button[data-testid='stSidebarCollapseButton']{display:none !important;}"
        "</style>",
        unsafe_allow_html=True
    )

    # Big, impactful header: logo + large title + site description.
    render_home_head()

    # The pool is the only navigation: eight lanes filling the page.
    st.markdown(
        f'<div class="fullbleed"><div class="home-lanes">{build_pool_lanes()}</div></div>',
        unsafe_allow_html=True
    )

    # Glossary: the acronyms used across every page, explained once, up front.
    glossary = [
        ("LC", "Long course. Races swum in a 50-metre Olympic pool. Times are usually slower, "
               "because there are fewer turns to push off from."),
        ("SC", "Short course. Races swum in a 25-metre pool. More walls means more push-offs, "
               "so times are typically faster than long course."),
        ("WR", "World record. The fastest time ever officially recognised for an event. "
               "Records are kept separately for long and short course."),
        ("IM", "Individual medley. One swimmer covers all four strokes in a single race, "
               "in the order butterfly, backstroke, breaststroke, freestyle."),
        ("Relay", "A team race: four swimmers each swim an equal leg. Relay records belong to the "
                  "team, so they are excluded from the individual athlete pages."),
        ("Top 200", "The 200 fastest performances ever recorded in an event. Unlike a world record, "
                    "one swimmer can appear many times."),
    ]

    items = "".join(
        f"<div class='glossary-item'><div class='glossary-term'>{term}</div>"
        f"<div class='glossary-def'>{definition}</div></div>"
        for term, definition in glossary
    )

    st.markdown(
        "<div class='glossary-wrap'>"
        "<div class='glossary-title'>Reading the numbers</div>"
        "<div class='glossary-intro'>A few abbreviations appear on every page. "
        "Here is what they mean.</div>"
        f"<div class='glossary-grid'>{items}</div>"
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# PAGE 2 - WORLD RECORD TIMELINE
# ============================================================

elif page == "World Record Timeline":

    # --- Editorial header: identical markup to page_header so it matches other sections ---
    col_txt, col_img = st.columns([1.45, 1], gap="large")

    with col_txt:
        st.markdown("<div class='section-title'>World Record Timeline</div>", unsafe_allow_html=True)
        st.markdown("<div class='wave-rule'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Follow how the fastest official world record in each "
            "event changed over time. Lower seconds mean faster performance.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class=\"fact-box\">"
            "<div class=\"fact-kicker\">Did you know?</div>"
            "<div class=\"fact-text\">At the first modern Olympic Games in <b>Athens 1896</b>, "
            "swimming was not held in a pool: the races took place in the open waters of the "
            "<b>Bay of Zea</b>, with water reported at about <b>13&deg;C</b>. From cold open water "
            "to today's controlled pools, every record on this page is a step in the evolution of "
            "swimming speed.</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with col_img:
        st.markdown(
            swim_figure("timeline.jpg", alt="Vintage Olympic swimming start", ratio="70%"),
            unsafe_allow_html=True,
        )

    filtered = apply_common_filters(
        wr,
        gender=True,
        course=True,
        stroke=True,
        distance=True,
        key_prefix="timeline"
    )

    if filtered.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    # On-page hint so users notice the sidebar filters (same as Nations & Places).
    st.info(
        "Use the **Filters** in the sidebar on the left (gender, course, stroke, distance) "
        "— the chart and table below update live."
    )

    available_events = safe_unique(filtered["event_label"])

    st.markdown("<div class='timeline-control-row'>", unsafe_allow_html=True)

    selector_col, record_col = st.columns([1, 1.45], gap="large")

    with selector_col:
        selected_event = st.selectbox(
            "Choose a race to explore",
            available_events,
            index=0 if available_events else None,
            key="timeline_event_selector"
        )

        st.markdown(
            "<div class=\"timeline-selector-note\">Select one event and follow every historical "
            "step that led to the current world record.</div>",
            unsafe_allow_html=True,
        )

    data = filtered[filtered["event_label"] == selected_event].copy()
    data = data.dropna(subset=["seconds"]).sort_values("date")

    if data.empty:
        st.warning("No data available for the selected race.")
        st.stop()

    current_rows = data[data["is_current_bool"] == True].copy()

    if not current_rows.empty:
        current_record = current_rows.sort_values("date").iloc[-1]
    else:
        current_record = data.sort_values("date").iloc[-1]

    first_record = data.iloc[0]
    improvement = first_record["seconds"] - current_record["seconds"]
    improvement_pct = improvement / first_record["seconds"] * 100 if first_record["seconds"] else np.nan

    current_time = clean_text(current_record["time"])
    current_name = clean_text(current_record["name"])
    current_nat = clean_text(current_record["nationality"])
    current_meet = clean_text(current_record["meet"])
    current_location = clean_text(current_record["location"])

    if pd.notna(current_record["date"]):
        current_date_label = current_record["date"].strftime("%d %b %Y")
    else:
        current_date_label = "Unknown date"

    with record_col:
        st.markdown(
            f"<div class=\"timeline-record-card\">"
            f"<div class=\"timeline-record-kicker\">Current world record</div>"
            f"<div class=\"timeline-record-main\">{current_time} &middot; {current_name}</div>"
            f"<div class=\"timeline-record-sub\">{selected_event}<br>"
            f"{current_nat} &middot; {current_date_label} &middot; {current_meet} &middot; {current_location}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Metrics: 3 columns (the long event name lived here before and got truncated with "…").
    st.markdown("<div class='timeline-metrics-row'>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Record entries", len(data))

    with c2:
        st.metric("Total improvement", f"{improvement:.2f} s")

    with c3:
        st.metric("Improvement", f"{improvement_pct:.1f}%")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='timeline-chart-spacer'></div>", unsafe_allow_html=True)

    chart_data = data.copy()

    chart_data["date_label"] = chart_data["date"].apply(
        lambda x: x.strftime("%d %b %Y") if pd.notna(x) else "Unknown date"
    )

    for col in ["event_label", "time", "name", "nationality", "meet", "location", "course"]:
        chart_data[col] = chart_data[col].astype(str).apply(clean_text)
        chart_data.loc[chart_data[col] == "", col] = "—"

    chart_data["current_point"] = chart_data.index == current_record.name

    custom_cols = [
        "event_label",
        "time",
        "date_label",
        "name",
        "nationality",
        "meet",
        "location",
        "course"
    ]

    chart_title = (
        f"<b>{selected_event}</b><br>"
        f"<span style='font-size:14px;color:#52616B'>"
        f"Current world record: <b>{current_time}</b> · {current_name} · {current_nat} · {current_date_label}"
        f"</span>"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_data["date"],
            y=chart_data["seconds"],
            mode="lines+markers",
            name="World record progression",
            line=dict(color=BLUE, width=3),
            marker=dict(
                size=8,
                color=BLUE,
                line=dict(color="white", width=1.4)
            ),
            customdata=chart_data[custom_cols].to_numpy(),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "Time: <b>%{customdata[1]}</b> (%{y:.2f} s)<br>"
                "Date: %{customdata[2]}<br>"
                "Swimmer: %{customdata[3]}<br>"
                "Nationality: %{customdata[4]}<br>"
                "Course: %{customdata[7]}<br>"
                "Meet: %{customdata[5]}<br>"
                "Location: %{customdata[6]}"
                "<extra></extra>"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[current_record["date"]],
            y=[current_record["seconds"]],
            mode="markers+text",
            name="Current record",
            marker=dict(
                size=21,
                color=GOLD,
                symbol="star",
                line=dict(color="white", width=1.5)
            ),
            text=["Current WR"],
            textposition="top center",
            customdata=pd.DataFrame(
                [[
                    selected_event,
                    current_time,
                    current_date_label,
                    current_name,
                    current_nat,
                    current_meet,
                    current_location,
                    clean_text(current_record["course"])
                ]],
                columns=custom_cols
            ).to_numpy(),
            hovertemplate=(
                "<b>Current world record</b><br><br>"
                "Event: %{customdata[0]}<br>"
                "Time: <b>%{customdata[1]}</b> (%{y:.2f} s)<br>"
                "Date: %{customdata[2]}<br>"
                "Swimmer: %{customdata[3]}<br>"
                "Nationality: %{customdata[4]}<br>"
                "Course: %{customdata[7]}<br>"
                "Meet: %{customdata[5]}<br>"
                "Location: %{customdata[6]}"
                "<extra></extra>"
            )
        )
    )

    fig.add_hline(
        y=current_record["seconds"],
        line_dash="dot",
        line_color=GOLD,
        opacity=0.75,
        annotation_text=f"Current WR · {current_time}",
        annotation_position="top left",
        annotation_font=dict(color=GOLD, size=12)
    )

    fig.update_layout(
        title=dict(
            text=chart_title,
            x=0.02,
            xanchor="left"
        )
    )

    fig.update_xaxes(
        title="Year of world record",
        tickformat="%Y"
    )

    fig.update_yaxes(
        autorange="reversed",
        title="Time in seconds — lower is faster"
    )

    fig = plotly_clean_layout(fig, height=650)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class=\"small-caption\">Design note: the y-axis is reversed because in swimming a "
        "lower time represents a better performance. The gold marker highlights the current world "
        "record.</div>",
        unsafe_allow_html=True,
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
        "A world record is a single number: one swimmer, one day. The top-200 tells a different "
        "story — how crowded the summit really is. In most events the 200 fastest swims in history "
        "are separated by barely a couple of seconds. This page is about that depth: how tightly "
        "packed the elite are, when their times were swum, and who keeps coming back.",
        image_file="top200.jpg",
        alt="Underwater view of swimmers",
        ratio="70%"
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
            "Rows to list in the table",
            min_value=5,
            max_value=min(200, max_rank),
            value=30,
            step=5
        )

    st.info(
        "Use the **Filters** and **Ranking selection** panels in the sidebar on the left to change "
        "event — every chart below updates live."
    )

    # The distribution charts always use the full ranking; only the table is trimmed.
    event_data = filtered[filtered["event_label"] == selected_event].dropna(subset=["time_seconds"]).copy()

    if event_data.empty:
        st.warning("No ranking data available for the selected filters.")
        st.stop()

    event_data = event_data.sort_values(["rank", "time_seconds"])
    event_data["year"] = event_data["date"].dt.year

    table_data = event_data[event_data["rank"] <= rank_limit].copy()

    best_time = event_data["time_seconds"].min()
    slowest_time = event_data["time_seconds"].max()
    field_spread = slowest_time - best_time
    best_row = event_data.iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Fastest ever", format_time(best_time))

    with c2:
        st.metric("Whole field spans", f"{field_spread:.2f} s")

    with c3:
        st.metric("Different athletes", event_data["athlete"].nunique())

    with c4:
        st.metric("Different nations", event_data["team_name"].nunique())

    # ------------------------------------------------------------------
    # 1. HOW TIGHT IS THE FIELD?  Box-and-whisker with every swim drawn on top.
    #    Each dot is one performance: nothing is aggregated away, and position
    #    along a common axis is the most accurately read visual channel.
    # ------------------------------------------------------------------
    st.markdown("### How tight is the elite field?")
    st.caption(
        f"Every one of the {len(event_data)} fastest swims ever recorded in this event, placed on a "
        f"single time axis. The box covers the middle half of them; the whiskers reach the rest. "
        f"Each dot is one swim — hover to see who."
    )

    swarm = go.Figure()
    swarm.add_trace(go.Box(
        x=event_data["time_seconds"],
        name="",
        boxpoints="all",
        jitter=0.6,
        pointpos=0,
        marker=dict(color=BLUE, size=6, opacity=0.55),
        line=dict(color=NAVY),
        fillcolor="rgba(34,184,207,0.18)",
        customdata=np.stack(
            [event_data["athlete"], event_data["time_label"], event_data["rank"], event_data["team_name"]],
            axis=-1
        ),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} · rank %{customdata[2]}"
                      "<br>%{customdata[3]}<extra></extra>",
        showlegend=False,
    ))
    swarm.add_trace(go.Scatter(
        x=[best_time],
        y=[0],
        mode="markers",
        marker=dict(color=GOLD, size=18, symbol="star", line=dict(color="white", width=1.4)),
        name="Fastest ever",
        hovertemplate=f"<b>{clean_text(best_row['athlete'])}</b><br>"
                      f"{clean_text(best_row['time_label'])} · the fastest ever<extra></extra>",
    ))
    swarm.update_xaxes(title="Time in seconds — further left is faster")
    swarm.update_yaxes(showticklabels=False, title="")
    swarm = plotly_clean_layout(swarm, height=360, title=f"{selected_event}")
    st.plotly_chart(swarm, use_container_width=True)

    st.markdown(
        f"<div class='small-caption'>The gold star is the fastest swim of all time in this event "
        f"({clean_text(best_row['athlete'])}, {clean_text(best_row['time_label'])}). Everything else "
        f"crowds in behind it: the 200th-fastest swim in history is only "
        f"<b>{field_spread:.2f} seconds</b> slower. Bars or bins would hide that crowding, so every "
        f"performance is drawn individually.</div>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 2. WHEN were these swims performed?
    # ------------------------------------------------------------------
    st.markdown("### When were these swims performed?")

    suit_era = event_data[event_data["year"].between(2008, 2009)]
    suit_share = len(suit_era) / len(event_data) * 100 if len(event_data) else 0

    st.caption(
        "Each dot is the same swim as above, now placed by the date it happened. A flat cloud means "
        "the event has barely moved; a downward drift means the whole elite got faster."
    )

    era = go.Figure()
    era.add_trace(go.Scatter(
        x=event_data["date"],
        y=event_data["time_seconds"],
        mode="markers",
        marker=dict(color=BLUE, size=7, opacity=0.65, line=dict(color="white", width=0.6)),
        customdata=np.stack([event_data["athlete"], event_data["time_label"], event_data["rank"]], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} · rank %{customdata[2]}"
                      "<br>%{x|%d %b %Y}<extra></extra>",
        showlegend=False,
    ))
    era.add_vrect(
        x0="2008-01-01", x1="2009-12-31",
        fillcolor=GOLD, opacity=0.16, line_width=0,
        annotation_text="Polyurethane suits", annotation_position="top left",
        annotation_font=dict(color=DARK_GREY, size=12),
    )
    era.update_xaxes(title="Date of the swim")
    era.update_yaxes(autorange="reversed", title="Time in seconds — lower is faster")
    era = plotly_clean_layout(era, height=440, title="The all-time top 200, placed in history")
    st.plotly_chart(era, use_container_width=True)

    st.markdown(
        f"<div class='small-caption'>The shaded band marks 2008–2009, when full-body polyurethane "
        f"suits were legal; they were banned from 2010. In this event "
        f"<b>{len(suit_era)} of the {len(event_data)} best swims ever ({suit_share:.0f}%)</b> come "
        f"from those two seasons alone. It is a reminder that a ranking table records the conditions "
        f"of a performance as much as the athlete.</div>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 3. WHO recurs, and WHICH nations have depth?
    # ------------------------------------------------------------------
    st.markdown("### Who gets here, and who gets here often")
    st.caption(
        "On the left, the swimmers with most performances inside this top 200 — depth belongs to "
        "athletes who repeat, not only to record holders. On the right, the same question asked of "
        "nations: a short box means a country's swimmers cluster tightly near the top."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        athlete_counts = (
            event_data.groupby("athlete")
            .size()
            .reset_index(name="entries")
            .sort_values("entries", ascending=False)
            .head(12)
        )

        fig_ath = px.bar(
            athlete_counts,
            x="entries",
            y="athlete",
            orientation="h",
            color_discrete_sequence=[BLUE],
        )
        fig_ath.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        fig_ath.update_xaxes(title="Swims inside this top 200")
        fig_ath.update_yaxes(title="")
        fig_ath = plotly_clean_layout(fig_ath, height=460, title="Most recurring swimmers")
        st.plotly_chart(fig_ath, use_container_width=True)

    with col_b:
        nation_order = event_data["team_name"].value_counts().head(6).index.tolist()
        nation_data = event_data[event_data["team_name"].isin(nation_order)]

        fig_nat = px.box(
            nation_data,
            x="time_seconds",
            y="team_name",
            orientation="h",
            category_orders={"team_name": nation_order},
            color_discrete_sequence=[AQUA],
            points="all",
        )
        fig_nat.update_traces(marker=dict(size=5, opacity=0.5, color=BLUE), line=dict(color=NAVY))
        fig_nat.update_layout(showlegend=False)
        fig_nat.update_xaxes(title="Time in seconds — further left is faster")
        fig_nat.update_yaxes(title="")
        fig_nat = plotly_clean_layout(fig_nat, height=460, title="Which nations have depth")
        st.plotly_chart(fig_nat, use_container_width=True)

    # ------------------------------------------------------------------
    # 4. The exact numbers. A table is the right tool for looking up a value.
    # ------------------------------------------------------------------
    st.markdown(f"### The first {len(table_data)} places, exactly")
    st.caption(
        "Charts show shape; a table shows values. Use the slider in the sidebar to lengthen this list."
    )

    st.dataframe(
        table_data[
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
        "Every swimmer here has an identity card built from two different sources: the world record "
        "book, which tracks who pushed the limit, and the all-time top-200 rankings, which show how "
        "consistently fast a swimmer really was. Pick an athlete in the sidebar, then scroll down to "
        "put two of them head to head.",
        image_file="athletes.jpg",
        alt="Swimmer racing butterfly",
        ratio="70%"
    )

    # ------------------------------------------------------------------
    # Identity keys and relay handling are built once in the loaders, so every
    # page shares them. Relay rows pack four swimmers into a single cell, so
    # they are excluded from every athlete-level view.
    # ------------------------------------------------------------------
    wr_a = wr[~wr["is_relay"] & (wr["athlete_key"] != "")].copy()
    top_a = top[~top["is_relay"] & (top["athlete_key"] != "")].copy()

    # Display name: prefer the world-record spelling, else prettify the top-200 one.
    top_pairs = (
        top_a.loc[top_a["athlete_key"] != "", ["athlete_key", "athlete"]]
        .drop_duplicates("athlete_key")
    )
    wr_pairs = (
        wr_a.loc[wr_a["athlete_key"] != "", ["athlete_key", "name"]]
        .drop_duplicates("athlete_key")
    )
    display_names = {r.athlete_key: pretty_name(r.athlete) for r in top_pairs.itertuples()}
    display_names.update({r.athlete_key: clean_text(r.name) for r in wr_pairs.itertuples()})

    all_keys = sorted([k for k in display_names if k], key=lambda k: display_names[k])

    def build_profile(key):
        """Everything the identity card needs, gathered from both datasets."""
        a_wr = wr_a[wr_a["athlete_key"] == key]
        a_top = top_a[top_a["athlete_key"] == key]

        nationality = "—"
        if not a_wr.empty:
            nats = a_wr["nationality"].apply(clean_text).replace("", np.nan).dropna()
            if not nats.empty:
                nationality = nats.mode().iloc[0]
        if nationality == "—" and not a_top.empty:
            teams = a_top["team_name"].apply(clean_text).replace("", np.nan).dropna()
            if not teams.empty:
                nationality = teams.mode().iloc[0]

        birth_year = None
        if not a_top.empty and "athlete_birth_date" in a_top.columns:
            births = pd.to_datetime(a_top["athlete_birth_date"], errors="coerce").dropna()
            if not births.empty:
                birth_year = int(births.iloc[0].year)

        years = []
        if not a_wr.empty:
            years += a_wr["date"].dropna().dt.year.tolist()
        if not a_top.empty:
            years += a_top["date"].dropna().dt.year.tolist()
        career = f"{min(years)}–{max(years)}" if years else "—"

        best_rank = "—"
        if not a_top.empty and a_top["rank"].notna().any():
            best_rank = int(a_top["rank"].min())

        signature = "—"
        if not a_top.empty:
            signature = a_top["event_label"].value_counts().index[0]
        elif not a_wr.empty:
            signature = a_wr["event_label"].value_counts().index[0]

        return {
            "key": key,
            "name": display_names.get(key, key.title()),
            "nationality": nationality,
            "birth_year": birth_year,
            "career": career,
            "wr_entries": len(a_wr),
            "current_wr": int(a_wr["is_current_bool"].sum()) if not a_wr.empty else 0,
            "top_entries": len(a_top),
            "best_rank": best_rank,
            "signature": signature,
            "wr_rows": a_wr,
            "top_rows": a_top,
        }

    def render_id_card(p, kicker="Athlete identity card"):
        birth = f"Born {p['birth_year']}" if p["birth_year"] else "Birth year not recorded"
        st.markdown(
            f"<div class='athlete-card'>"
            f"<div class='athlete-card-kicker'>{kicker}</div>"
            f"<div class='athlete-card-name'>{p['name']}</div>"
            f"<div class='athlete-card-meta'>"
            f"{p['nationality']} &middot; {birth} &middot; Active {p['career']}<br>"
            f"Signature event: <b>{p['signature']}</b>"
            f"</div>"
            f"<div class='athlete-stat-grid'>"
            f"<div class='athlete-stat'><div class='athlete-stat-value'>{p['wr_entries']}</div>"
            f"<div class='athlete-stat-label'>World records set</div></div>"
            f"<div class='athlete-stat'><div class='athlete-stat-value'>{p['current_wr']}</div>"
            f"<div class='athlete-stat-label'>Still standing</div></div>"
            f"<div class='athlete-stat'><div class='athlete-stat-value'>{p['top_entries']}</div>"
            f"<div class='athlete-stat-label'>Top-200 swims</div></div>"
            f"<div class='athlete-stat'><div class='athlete-stat-value'>{p['best_rank']}</div>"
            f"<div class='athlete-stat-label'>Best all-time rank</div></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------
    # Athlete selection
    # ------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### Athlete selection")
        search = st.text_input("Search athlete", "")
        if search:
            shown_keys = [k for k in all_keys if search.lower() in display_names[k].lower()]
        else:
            shown_keys = all_keys

        selected_key = st.selectbox(
            "Choose athlete",
            shown_keys,
            index=0 if shown_keys else None,
            format_func=lambda k: display_names.get(k, k),
            key="athlete_pick"
        )

    st.info(
        "Use the **Athlete selection** panel in the sidebar on the left to search and pick a "
        "swimmer — the identity card and charts below update live."
    )

    if not selected_key:
        st.warning("No athlete matches your search.")
        st.stop()

    profile = build_profile(selected_key)
    athlete_wr = profile["wr_rows"].sort_values("date")
    athlete_top = profile["top_rows"]

    render_id_card(profile)

    # ------------------------------------------------------------------
    # 1. SMALL MULTIPLES.
    #    A swimmer's records span events of wildly different length: Phelps set
    #    marks at 49 seconds and at 251 seconds. Forcing both onto one y-axis
    #    makes the short events a flat line at the bottom. Replicating one small
    #    panel per event, each with its own scale, is the standard remedy.
    # ------------------------------------------------------------------
    st.markdown("### How this swimmer moved each record")

    if not athlete_wr.empty:
        panel_events = athlete_wr["event_label"].value_counts().head(6).index.tolist()
        panels = athlete_wr[athlete_wr["event_label"].isin(panel_events)].sort_values("date")

        st.caption(
            f"One panel per event, because a 50-metre sprint and a 400-metre medley cannot share a "
            f"vertical axis. Inside each panel the line falls as {profile['name']} took time off the "
            f"world record. Each panel keeps its own scale, so read the shape of the descent, not "
            f"the height."
        )

        fig_sm = px.line(
            panels,
            x="date",
            y="seconds",
            facet_col="event_label",
            facet_col_wrap=3,
            markers=True,
            color_discrete_sequence=[BLUE],
            custom_data=["time", "meet", "location"],
        )
        fig_sm.update_yaxes(matches=None, showticklabels=True, title="")
        fig_sm.update_xaxes(matches=None, title="")
        fig_sm.update_traces(
            line=dict(width=2.4),
            marker=dict(size=7, line=dict(color="white", width=1)),
            hovertemplate="%{customdata[0]} · %{x|%b %Y}<br>%{customdata[1]}<extra></extra>",
        )
        # Facet titles arrive as "event_label=Men 200m Butterfly (LC)".
        fig_sm.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=12)))

        rows_needed = int(np.ceil(len(panel_events) / 3))
        fig_sm = plotly_clean_layout(fig_sm, height=200 + 190 * rows_needed, title=None)
        fig_sm.update_layout(showlegend=False)
        st.plotly_chart(fig_sm, use_container_width=True)

        st.caption(
            "Seconds on every vertical axis, earlier dates to the left. A steep step means one swim "
            "took a large chunk off the record; a gentle slope means it was chipped away."
        )
    else:
        st.info("This athlete never held a world record in the world record dataset.")

    # ------------------------------------------------------------------
    # 2. Two questions that need a reference, not a raw number.
    # ------------------------------------------------------------------
    st.markdown("### Measured against the best there has ever been")
    st.caption(
        "On the left, how close this swimmer's personal best comes to the fastest swim ever recorded "
        "in each event. Zero means they own it. On the right, all 200 of the fastest swims ever in "
        "their signature event, with their own swims picked out."
    )

    col_a, col_b = st.columns([1, 1])

    with col_a:
        if not athlete_top.empty:
            event_best = top.groupby("event_label")["time_seconds"].min()
            personal_best = athlete_top.groupby("event_label")["time_seconds"].min()
            reference = event_best.reindex(personal_best.index)

            gap = pd.DataFrame({
                "event_label": personal_best.index,
                "pct_behind": (personal_best - reference) / reference * 100,
                "personal_best": personal_best.values,
            }).sort_values("pct_behind").head(12)

            gap["is_best_ever"] = gap["pct_behind"] <= 0.001
            gap["bar_color"] = np.where(gap["is_best_ever"], GOLD, BLUE)

            fig_gap = go.Figure()
            fig_gap.add_trace(go.Bar(
                x=gap["pct_behind"],
                y=gap["event_label"],
                orientation="h",
                marker_color=gap["bar_color"],
                customdata=np.stack([gap["personal_best"]], axis=-1),
                hovertemplate="%{y}<br>Personal best %{customdata[0]:.2f} s"
                              "<br>%{x:.2f}% behind the all-time best<extra></extra>",
                showlegend=False,
            ))
            fig_gap.add_vline(
                x=0, line_color=GOLD, line_width=2,
                annotation_text="Fastest ever", annotation_position="top",
                annotation_font=dict(color=DARK_GREY, size=11),
            )
            fig_gap.update_layout(yaxis=dict(autorange="reversed"))
            fig_gap.update_xaxes(title="Percent behind the fastest swim ever in that event")
            fig_gap.update_yaxes(title="")
            fig_gap = plotly_clean_layout(fig_gap, height=480, title="Distance from the summit")
            st.plotly_chart(fig_gap, use_container_width=True)

            owned = int(gap["is_best_ever"].sum())
            if owned:
                st.caption(
                    f"A gold bar of zero length means {profile['name']} is the fastest human ever "
                    f"recorded in that event ({owned} of them here)."
                )
            else:
                st.caption(
                    "Percent, not seconds: it is the only unit that lets a sprint and a distance "
                    "race be judged against the same reference."
                )
        else:
            st.info("This athlete has no entries in the all-time top-200 dataset.")

    with col_b:
        if not athlete_top.empty:
            signature = athlete_top["event_label"].value_counts().index[0]
            field = top[top["event_label"] == signature].dropna(subset=["time_seconds"])
            mine = athlete_top[athlete_top["event_label"] == signature].dropna(subset=["time_seconds"])

            fig_field = go.Figure()
            fig_field.add_trace(go.Box(
                x=field["time_seconds"],
                name="",
                boxpoints="all",
                jitter=0.6,
                pointpos=0,
                marker=dict(color="rgba(82,97,107,0.30)", size=6),
                line=dict(color=DARK_GREY),
                fillcolor="rgba(34,184,207,0.10)",
                hoverinfo="skip",
                showlegend=False,
            ))
            fig_field.add_trace(go.Scatter(
                x=mine["time_seconds"],
                y=np.zeros(len(mine)),
                mode="markers",
                marker=dict(color=GOLD, size=11, line=dict(color="white", width=1.2)),
                name=profile["name"],
                customdata=np.stack([mine["time_label"], mine["rank"]], axis=-1),
                hovertemplate="%{customdata[0]} · rank %{customdata[1]}<extra></extra>",
            ))
            fig_field.update_xaxes(title="Time in seconds — further left is faster")
            fig_field.update_yaxes(showticklabels=False, title="")
            fig_field = plotly_clean_layout(fig_field, height=480, title=f"Inside the top 200: {signature}")
            st.plotly_chart(fig_field, use_container_width=True)

            st.caption(
                f"{len(mine)} of the 200 fastest swims ever in this event belong to "
                f"{profile['name']} (best rank {int(mine['rank'].min())})."
            )
        else:
            st.info("No top-200 entries, so there is no field to place this swimmer in.")
    # ------------------------------------------------------------------
    # Global context
    # ------------------------------------------------------------------
    section(
        "Global athlete rankings",
        "How the selected swimmer compares with the names that recur most often across the whole "
        "archive. These charts count appearances, so they reward longevity as much as raw speed."
    )

    col_1, col_2 = st.columns(2)

    with col_1:
        wr_rank = (
            wr_a[wr_a["athlete_key"] != ""]
            .groupby("athlete_key")
            .size()
            .reset_index(name="world_record_entries")
            .sort_values("world_record_entries", ascending=False)
            .head(15)
        )
        wr_rank["athlete"] = wr_rank["athlete_key"].map(display_names)
        wr_rank["highlight"] = np.where(
            wr_rank["athlete_key"] == selected_key, "Selected athlete", "Other athletes"
        )

        fig = px.bar(
            wr_rank,
            x="world_record_entries",
            y="athlete",
            orientation="h",
            color="highlight",
            color_discrete_map={"Selected athlete": GOLD, "Other athletes": BLUE},
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), legend_title_text="")
        fig.update_xaxes(title="World records set")
        fig.update_yaxes(title="")
        fig = plotly_clean_layout(fig, height=520, title="Most world records set")
        st.plotly_chart(fig, use_container_width=True)

    with col_2:
        top_rank = (
            top_a[top_a["athlete_key"] != ""]
            .groupby("athlete_key")
            .size()
            .reset_index(name="top_200_entries")
            .sort_values("top_200_entries", ascending=False)
            .head(15)
        )
        top_rank["athlete"] = top_rank["athlete_key"].map(display_names)
        top_rank["highlight"] = np.where(
            top_rank["athlete_key"] == selected_key, "Selected athlete", "Other athletes"
        )

        fig = px.bar(
            top_rank,
            x="top_200_entries",
            y="athlete",
            orientation="h",
            color="highlight",
            color_discrete_map={"Selected athlete": GOLD, "Other athletes": AQUA},
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), legend_title_text="")
        fig.update_xaxes(title="Swims inside the all-time top 200")
        fig.update_yaxes(title="")
        fig = plotly_clean_layout(fig, height=520, title="Most all-time top-200 swims")
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "If the selected swimmer appears in a chart, the bar is highlighted in gold."
    )

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

    # ------------------------------------------------------------------
    # HEAD TO HEAD
    # ------------------------------------------------------------------
    section(
        "Head to head",
        "Pick two swimmers and compare them directly. The chart below only uses events both of them "
        "actually swam, so the two bars always measure the same thing in the same unit."
    )

    pick_l, pick_vs, pick_r = st.columns([1, 0.22, 1], gap="medium")

    default_left = all_keys.index(selected_key) if selected_key in all_keys else 0
    default_right = 1 if len(all_keys) > 1 else 0
    if default_right == default_left and len(all_keys) > 1:
        default_right = 0 if default_left != 0 else 1

    with pick_l:
        key_left = st.selectbox(
            "First swimmer",
            all_keys,
            index=default_left,
            format_func=lambda k: display_names.get(k, k),
            key="vs_left"
        )

    with pick_r:
        key_right = st.selectbox(
            "Second swimmer",
            all_keys,
            index=default_right,
            format_func=lambda k: display_names.get(k, k),
            key="vs_right"
        )

    if key_left == key_right:
        st.warning("Choose two different swimmers to see the comparison.")
    else:
        p_left = build_profile(key_left)
        p_right = build_profile(key_right)

        card_l, card_vs, card_r = st.columns([1, 0.22, 1], gap="medium")

        with card_l:
            render_id_card(p_left, kicker="Challenger")

        with card_vs:
            st.markdown(
                "<div class='vs-badge'><div class='vs-badge-inner'>VS</div></div>",
                unsafe_allow_html=True,
            )

        with card_r:
            render_id_card(p_right, kicker="Challenger")

        # --- Same reference, same unit: how far each sits from the all-time best ---
        event_best = top.groupby("event_label")["time_seconds"].min()

        def gap_per_event(p):
            rows = p["top_rows"].dropna(subset=["time_seconds"])
            if rows.empty:
                return pd.Series(dtype=float)
            personal = rows.groupby("event_label")["time_seconds"].min()
            reference = event_best.reindex(personal.index)
            return (personal - reference) / reference * 100

        gap_l = gap_per_event(p_left)
        gap_r = gap_per_event(p_right)
        shared_events = sorted(set(gap_l.index) & set(gap_r.index))

        if not shared_events:
            st.info(
                "These two swimmers share no event inside the all-time top-200 dataset, so a "
                "like-for-like comparison is not possible. The identity cards above still "
                "summarise each career."
            )
        else:
            duel = pd.DataFrame({
                "event_label": shared_events,
                "left": gap_l[shared_events].values,
                "right": gap_r[shared_events].values,
            })

            fig = go.Figure()

            for _, row in duel.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row["left"], row["right"]],
                    y=[row["event_label"], row["event_label"]],
                    mode="lines",
                    line=dict(color="rgba(82,97,107,0.35)", width=4),
                    showlegend=False,
                    hoverinfo="skip",
                ))

            fig.add_trace(go.Scatter(
                x=duel["left"], y=duel["event_label"], mode="markers",
                name=p_left["name"],
                marker=dict(size=15, color=BLUE, line=dict(color="white", width=1.4)),
                hovertemplate="%{y}<br>" + p_left["name"] + ": %{x:.2f}% behind<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=duel["right"], y=duel["event_label"], mode="markers",
                name=p_right["name"],
                marker=dict(size=15, color=GOLD, line=dict(color="white", width=1.4)),
                hovertemplate="%{y}<br>" + p_right["name"] + ": %{x:.2f}% behind<extra></extra>",
            ))

            fig.add_vline(
                x=0, line_color=NAVY, line_width=2, line_dash="dot",
                annotation_text="Fastest ever", annotation_position="top",
                annotation_font=dict(color=DARK_GREY, size=11),
            )
            fig.update_xaxes(title="Percent behind the fastest swim ever in that event — left is better")
            fig.update_yaxes(title="")
            fig = plotly_clean_layout(
                fig,
                height=200 + 80 * len(duel),
                title="How far each one sits from the all-time best"
            )
            st.plotly_chart(fig, use_container_width=True)

            wins_l = int((duel["left"] < duel["right"]).sum())
            wins_r = int((duel["right"] < duel["left"]).sum())

            st.markdown(
                f"<div class='small-caption'>Across the {len(duel)} shared "
                f"event{'s' if len(duel) != 1 else ''}, <b>{p_left['name']}</b> is the closer to the "
                f"all-time best {wins_l} time{'s' if wins_l != 1 else ''} and "
                f"<b>{p_right['name']}</b> {wins_r} time{'s' if wins_r != 1 else ''}. "
                f"Both swimmers are measured against the same fixed reference — the fastest swim ever "
                f"recorded in each event — so the horizontal gap between two dots is the real "
                f"difference between them, whatever the length of the race.</div>",
                unsafe_allow_html=True,
            )
# ============================================================
# PAGE 5 - NATIONS & PLACES
# ============================================================

elif page == "Nations & Places":

    # Filters (rendered in the sidebar) applied first so the map/charts react live.
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

    # --- Nationality cleaning + ISO-3 mapping (needed for the world map) ---
    
    NAT_TO_ISO3 = {
        "Argentina": "ARG", "Australia": "AUS", "Australasia": "AUS", "Austria": "AUT",
        "Belarus": "BLR", "Belgium": "BEL", "Brazil": "BRA", "Canada": "CAN",
        "Cayman Islands": "CYM", "China": "CHN", "Costa Rica": "CRI", "Croatia": "HRV",
        "Denmark": "DNK", "East Germany": "DEU", "West Germany": "DEU", "Germany": "DEU",
        "Finland": "FIN", "France": "FRA", "Great Britain": "GBR", "Hong Kong": "HKG",
        "Hungary": "HUN", "Ireland": "IRL", "Italy": "ITA", "Jamaica": "JAM", "Japan": "JPN",
        "Lithuania": "LTU", "Mexico": "MEX", "Netherlands": "NLD", "New Zealand": "NZL",
        "Poland": "POL", "Romania": "ROU", "Russia": "RUS", "Soviet Union": "RUS",
        "Unified Team at the Olympics": "RUS", "Serbia": "SRB", "Serbia and Montenegro": "SRB",
        "Slovakia": "SVK", "South Africa": "ZAF", "Spain": "ESP", "Sweden": "SWE",
        "Switzerland": "CHE", "Trinidad and Tobago": "TTO", "Turkey": "TUR", "USA": "USA",
        "United States": "USA", "United States(Cali Condors)": "USA", "Ukraine": "UKR",
        "Zimbabwe": "ZWE",
    }
    ISO3_TO_NAME = {
        "USA": "United States", "AUS": "Australia", "DEU": "Germany", "RUS": "Russia",
        "GBR": "Great Britain", "NLD": "Netherlands", "JPN": "Japan", "CHN": "China",
        "SWE": "Sweden", "HUN": "Hungary", "CAN": "Canada", "FRA": "France",
        "ITA": "Italy", "ESP": "Spain", "BRA": "Brazil", "ZAF": "South Africa",
        "NZL": "New Zealand", "POL": "Poland", "ROU": "Romania", "UKR": "Ukraine",
        "SRB": "Serbia", "AUT": "Austria", "BEL": "Belgium", "DNK": "Denmark",
        "FIN": "Finland", "CHE": "Switzerland", "IRL": "Ireland", "HRV": "Croatia",
        "SVK": "Slovakia", "LTU": "Lithuania", "BLR": "Belarus", "ARG": "Argentina",
        "MEX": "Mexico", "CRI": "Costa Rica", "JAM": "Jamaica", "TTO": "Trinidad and Tobago",
        "TUR": "Turkey", "HKG": "Hong Kong", "CYM": "Cayman Islands", "ZWE": "Zimbabwe",
    }

    filtered_wr = filtered_wr.copy()
    filtered_wr["iso3"] = filtered_wr["nationality"].map(NAT_TO_ISO3)

    # On-page hint so users notice the sidebar filters.
    st.info(
        "Use the **Filters** in the sidebar on the left (gender, course, stroke, distance) "
        "— the map and charts below update live."
    )

    # --- Build the world map data (WR entries per nation) ---
    map_data = (
        filtered_wr.dropna(subset=["iso3"])
        .groupby("iso3")
        .size()
        .reset_index(name="world_record_entries")
    )
    map_data["country"] = map_data["iso3"].map(ISO3_TO_NAME).fillna(map_data["iso3"])

    fig_map = px.choropleth(
        map_data,
        locations="iso3",                 # mark = country area
        color="world_record_entries",     # channel = colour (sequential)
        hover_name="country",
        color_continuous_scale=[[0.0, "#7FD4E0"], [0.5, BLUE], [1.0, NAVY]],
        labels={"world_record_entries": "WR entries"},
    )
    fig_map.update_traces(marker_line_color="white", marker_line_width=0.6)
    fig_map.update_geos(
        showframe=False,
        showcoastlines=False,
        showland=True, landcolor="#EDEFF2",     # no-data land = light grey
        showocean=True, oceancolor="#CFE3EE",   # ocean = soft blue
        showcountries=True, countrycolor="white",
        projection_type="natural earth",
    )
    fig_map.update_geos(bgcolor="rgba(0,0,0,0)")
    fig_map.update_layout(
        height=430,
        margin=dict(l=0, r=0, t=6, b=0),
        font=dict(family="Arial", size=13, color=NAVY),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="WR entries"),
    )

    # --- Editorial header: title + description + MAP on the left, photo on the right ---
    head_txt, head_img = st.columns([1.45, 1], gap="large")

    with head_txt:
        st.markdown("<div class='section-title'>Nations &amp; Places</div>", unsafe_allow_html=True)
        st.markdown("<div class='wave-rule'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Which countries produced the most world records? "
            "The map shows the all-time <b>volume of records by nation</b> — darker means more "
            "records. Historical states (East/West Germany, USSR) are folded into their modern "
            "country.</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with head_img:
        st.markdown(
            swim_figure("nations.jpg", alt="Underwater backstroke swimmer", ratio="126%"),
            unsafe_allow_html=True,
        )

    # --- Two non-redundant breakdowns: who holds records now, and where they were set ---
    st.markdown("### Reading the numbers behind the map")
    st.caption(
        "The map answers *which nations* dominate overall. These two charts add what a map "
        "reads less precisely: the exact ranking of who holds records **today**, and the "
        "**pools and cities** where records are actually set."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        current_nations = (
            filtered_wr[filtered_wr["is_current_bool"] == True]
            .dropna(subset=["iso3"])
            .assign(country=lambda d: d["iso3"].map(ISO3_TO_NAME).fillna(d["nationality"]))
            .groupby("country")
            .size()
            .reset_index(name="current_records")
            .sort_values("current_records", ascending=False)
            .head(15)
        )

        fig = px.bar(
            current_nations,
            x="current_records",
            y="country",
            orientation="h",
            color_discrete_sequence=[GOLD],
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            xaxis_title="Current world records held",
            yaxis_title="",
        )
        fig = plotly_clean_layout(fig, height=520, title="Who holds world records today")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        locations = (
            filtered_wr[filtered_wr["location"].astype(str).str.strip() != ""]
            .groupby("location")
            .size()
            .reset_index(name="records")
            .sort_values("records", ascending=False)
            .head(15)
        )

        fig = px.bar(
            locations,
            x="records",
            y="location",
            orientation="h",
            color_discrete_sequence=[BLUE],
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            xaxis_title="World records set at this location",
            yaxis_title="",
        )
        fig = plotly_clean_layout(fig, height=520, title="Where records are set")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div class="small-caption">
        Interpretation note: these views show representation inside the available datasets.
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
        "A 50m sprint and a 1500m distance race are not measured on the same clock: one lasts twenty "
        "seconds, the other a quarter of an hour. To compare how they evolved we have to strip away "
        "the absolute times and ask the same questions of each: how often has this record fallen, "
        "how much faster has it become, and how long has the current mark survived? Pick the events "
        "you want to put side by side."
    )

    filtered = apply_common_filters(
        wr,
        gender=True,
        course=True,
        stroke=True,
        distance=True,
        key_prefix="compare"
    )

    # Relay records belong to a team of four, not to a single event progression,
    # so they are left out of an event-to-event comparison.
    filtered = filtered[~filtered["is_relay"]]
    filtered = filtered.dropna(subset=["seconds", "date"])

    if filtered.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    st.info(
        "Use the **Filters** in the sidebar on the left to narrow the pool of events, then choose "
        "which ones to compare in the selector below."
    )

    # ------------------------------------------------------------------
    # One row per event: the four questions above, answered numerically.
    # ------------------------------------------------------------------
    summary_rows = []

    for event, group in filtered.groupby("event_label"):
        group = group.sort_values("date")

        if len(group) < 3:
            continue

        first = group.iloc[0]
        last = group.iloc[-1]

        current_rows = group[group["is_current_bool"] == True]
        if not current_rows.empty:
            current = current_rows.iloc[-1]
        else:
            current = last

        current_date = current["date"]
        age_years = (pd.Timestamp.today() - current_date).days / 365.25 if pd.notna(current_date) else np.nan
        history_years = (last["date"] - first["date"]).days / 365.25

        summary_rows.append(
            {
                "event_label": event,
                "records": len(group),
                "first_year": first["year"],
                "latest_year": last["year"],
                "improvement_s": first["seconds"] - last["seconds"],
                "improvement_pct": (first["seconds"] - last["seconds"]) / first["seconds"] * 100
                if first["seconds"] else np.nan,
                "current_record_age_years": age_years,
                "history_years": history_years,
                "current_holder": clean_text(current["name"]),
                "current_time": clean_text(current["time"]),
            }
        )

    summary = pd.DataFrame(summary_rows)

    if summary.empty:
        st.warning("No comparable event summary available.")
        st.stop()

    oldest = summary.sort_values("current_record_age_years", ascending=False).iloc[0]
    biggest = summary.sort_values("improvement_pct", ascending=False).iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Events compared", len(summary))

    with c2:
        st.metric("Oldest current record", f"{oldest['current_record_age_years']:.1f} years")

    with c3:
        st.metric("Biggest improvement", f"{biggest['improvement_pct']:.1f}%")

    st.caption(
        f"The longest-standing mark belongs to **{oldest['event_label']}** "
        f"({clean_text(oldest['current_holder'])}). The event that has improved most since its first "
        f"recorded world record is **{biggest['event_label']}**."
    )

    # ------------------------------------------------------------------
    # Selection interface (two or more events), as prescribed for a
    # comparison task: pick the subjects first, then compare them.
    # ------------------------------------------------------------------
    all_events = sorted(summary["event_label"].tolist())

    preferred = [
        e for e in [
            "Men 100m Freestyle (LC)",
            "Women 100m Freestyle (LC)",
            "Men 1500m Freestyle (LC)",
            "Men 50m Freestyle (LC)",
        ] if e in all_events
    ]
    default_events = preferred if preferred else all_events[:3]

    chosen = st.multiselect(
        "Events to compare (two to six work best)",
        all_events,
        default=default_events,
        key="compare_events_pick"
    )

    if len(chosen) < 2:
        st.warning("Choose at least two events to compare.")
        st.stop()

    if len(chosen) > 6:
        st.info("Showing the first six events — beyond that the lines become hard to follow.")
        chosen = chosen[:6]

    series_colors = [BLUE, GOLD, AQUA, NAVY, RED, DARK_GREY]
    color_of = {event: series_colors[i % len(series_colors)] for i, event in enumerate(chosen)}

    # ------------------------------------------------------------------
    # 1. Progression on a shared scale.
    #    Each event is indexed to its own first world record = 100, which is the
    #    only way a 20-second sprint and a 15-minute race can share a y-axis.
    # ------------------------------------------------------------------
    st.markdown("### How far each record has travelled")
    st.caption(
        "Every event starts at 100: its own first world record. A line falling to 70 means the "
        "record is now 30% faster than when the archive began. Grey lines are the other events, "
        "kept as background so each selection can be read against the whole field."
    )

    fig_index = go.Figure()

    for event, group in filtered.groupby("event_label"):
        if event in chosen or len(group) < 3:
            continue
        group = group.sort_values("date")
        base = group["seconds"].iloc[0]
        if not base:
            continue
        fig_index.add_trace(go.Scatter(
            x=group["date"],
            y=group["seconds"] / base * 100,
            mode="lines",
            line=dict(color="rgba(82,97,107,0.12)", width=1),
            showlegend=False,
            hoverinfo="skip",
        ))

    for event in chosen:
        group = filtered[filtered["event_label"] == event].sort_values("date")
        base = group["seconds"].iloc[0]
        fig_index.add_trace(go.Scatter(
            x=group["date"],
            y=group["seconds"] / base * 100,
            mode="lines+markers",
            name=event,
            line=dict(color=color_of[event], width=2.6),
            marker=dict(size=5, color=color_of[event]),
            customdata=np.stack([group["name"], group["time"]], axis=-1),
            hovertemplate=f"<b>{event}</b><br>%{{customdata[0]}} · %{{customdata[1]}}"
                          "<br>%{y:.1f}% of the first record<extra></extra>",
        ))

    fig_index.add_hline(
        y=100, line_dash="dot", line_color=DARK_GREY, opacity=0.7,
        annotation_text="First recorded world record", annotation_position="bottom left",
        annotation_font=dict(color=DARK_GREY, size=11),
    )
    fig_index.update_xaxes(title="Year the record was set")
    fig_index.update_yaxes(title="Record time as % of that event's first record")
    fig_index = plotly_clean_layout(fig_index, height=560, title="World record progression, on a shared scale")
    fig_index.update_layout(
        margin=dict(l=30, r=30, t=130, b=40),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, xanchor="left"),
    )
    st.plotly_chart(fig_index, use_container_width=True)

    # ------------------------------------------------------------------
    # 2. The same events on four axes at once.
    #    A radar is the standard answer to "compare a few subjects across
    #    several metrics"; every axis is rescaled 0-100 against the strongest
    #    event in the archive, because the four metrics have different units.
    # ------------------------------------------------------------------
    st.markdown("### The same events, four questions at a time")
    st.caption(
        "Each spoke is one question, rescaled so that 100 is the highest value reached by any event "
        "in the archive. A wide shape means an event that has been broken often, improved a lot, and "
        "has a long history. Because the four metrics have different units, only the shapes should "
        "be compared, never the raw distances."
    )

    radar_metrics = [
        ("records", "Times broken"),
        ("improvement_pct", "Total improvement"),
        ("current_record_age_years", "Age of current record"),
        ("history_years", "Years of history"),
    ]
    maxima = {col: summary[col].max() for col, _ in radar_metrics}

    fig_radar = go.Figure()

    for event in chosen:
        row = summary[summary["event_label"] == event].iloc[0]
        values = [
            (row[col] / maxima[col] * 100) if maxima[col] else 0
            for col, _ in radar_metrics
        ]
        labels = [label for _, label in radar_metrics]
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=event,
            line=dict(color=color_of[event], width=2),
            opacity=0.55,
        ))

    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(5,43,68,0.12)"),
            angularaxis=dict(gridcolor="rgba(5,43,68,0.12)"),
        )
    )
    fig_radar = plotly_clean_layout(fig_radar, height=560, title="Event profiles compared")
    fig_radar.update_layout(
        margin=dict(l=60, r=60, t=90, b=110),
        legend=dict(orientation="h", y=-0.12, yanchor="top", x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ------------------------------------------------------------------
    # 3. Where the chosen events sit inside the whole archive.
    # ------------------------------------------------------------------
    st.markdown("### Do records that fall often also stay young?")
    st.caption(
        "Every dot is one event. Events far to the right have been broken many times; events high up "
        "are still holding a record set long ago. The chosen events are drawn in colour."
    )

    summary["is_chosen"] = summary["event_label"].isin(chosen)

    fig_scatter = go.Figure()

    others = summary[~summary["is_chosen"]]
    fig_scatter.add_trace(go.Scatter(
        x=others["records"],
        y=others["current_record_age_years"],
        mode="markers",
        marker=dict(size=9, color="rgba(82,97,107,0.28)", line=dict(color="white", width=0.6)),
        name="Other events",
        customdata=np.stack([others["event_label"], others["improvement_pct"]], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>%{x} records<br>"
                      "current mark %{y:.1f} years old<br>improved %{customdata[1]:.1f}%<extra></extra>",
    ))

    for event in chosen:
        row = summary[summary["event_label"] == event].iloc[0]
        fig_scatter.add_trace(go.Scatter(
            x=[row["records"]],
            y=[row["current_record_age_years"]],
            mode="markers+text",
            marker=dict(size=16, color=color_of[event], line=dict(color="white", width=1.4)),
            text=[event],
            textposition="top center",
            textfont=dict(size=11, color=NAVY),
            name=event,
            showlegend=False,
            hovertemplate=f"<b>{event}</b><br>%{{x}} records<br>"
                          f"current mark %{{y:.1f}} years old<extra></extra>",
        ))

    fig_scatter.update_xaxes(title="Number of times the record has been broken")
    fig_scatter.update_yaxes(title="Age of the current record, in years")
    fig_scatter = plotly_clean_layout(fig_scatter, height=560, title="Record turnover against record age")
    fig_scatter.update_layout(
        margin=dict(l=30, r=30, t=110, b=40),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, xanchor="left"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown(
        "<div class='small-caption'>Reading note: an event can be broken often and still hold an old "
        "record, if its progress stopped recently. Counts depend on how completely the archive "
        "recorded each event, so an event with few entries is not necessarily a stable one.</div>",
        unsafe_allow_html=True
    )

    st.dataframe(
        summary.drop(columns=["is_chosen"]).sort_values("records", ascending=False).rename(
            columns={
                "event_label": "Event",
                "records": "Number of records",
                "first_year": "First year",
                "latest_year": "Latest year",
                "improvement_s": "Improvement, seconds",
                "improvement_pct": "Improvement, %",
                "current_record_age_years": "Current record age, years",
                "history_years": "Years of history",
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
        ratio="70%"
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
