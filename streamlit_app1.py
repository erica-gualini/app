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
    "Game",
    "Data & Methods"
]

PAGE_LABELS = {
    "Home": "Home",
    "World Record Timeline": "Timeline",
    "All-Time Top 200 Rankings": "Top 200",
    "Athletes Hall of Fame": "Athletes",
    "Nations & Places": "Nations",
    "Compare Events": "Compare",
    "Game": "Game",
    "Data & Methods": "Methods"
}

PAGE_TAGS = {
    "Home": "Start block",
    "World Record Timeline": "Record flow",
    "All-Time Top 200 Rankings": "Elite depth",
    "Athletes Hall of Fame": "Legends",
    "Nations & Places": "Maps & flags",
    "Compare Events": "Race match",
    "Game": "Play & guess",
    "Data & Methods": "Behind data"
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


if page != "Home":
    with st.sidebar:
        st.markdown("## 🏊 Filters")
        st.caption("Use this panel only when a page requires filtering.")
        st.markdown("---")
        st.caption("Gold = current record / best performance. Blue = long course. Aqua = short course.")


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
# PAGE 7 - GAME (SWIM RECORD TOE)
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
