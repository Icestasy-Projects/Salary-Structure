"""
TradingView Auto-Screenshot Script
===================================
Run this on YOUR computer (not in Claude Code) to automatically
take TradingView screenshots of chart patterns.

REQUIREMENTS:
    pip install playwright
    playwright install chromium

USAGE:
    python auto_screenshot_tradingview.py

It will open TradingView, navigate to each stock, wait for the chart
to load, and save screenshots. You may need to log in manually on
the first run.
"""

import time
import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "tradingview_screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# EDIT THESE: Stocks and patterns for each PDF
# ============================================================

# PDF 1: Trevor Dcosta (MSF07)
TREVOR_PATTERNS = [
    {"stock": "NSE:RELIANCE",   "pattern": "Double Top",            "timeframe": "D",  "filename": "trevor_01_double_top.png"},
    {"stock": "NSE:HDFCBANK",   "pattern": "Double Bottom",         "timeframe": "D",  "filename": "trevor_02_double_bottom.png"},
    {"stock": "NSE:INFY",       "pattern": "Triple Top",            "timeframe": "W",  "filename": "trevor_03_triple_top.png"},
    {"stock": "NSE:ICICIBANK",  "pattern": "Triple Bottom",         "timeframe": "D",  "filename": "trevor_04_triple_bottom.png"},
    {"stock": "NSE:BHARTIARTL", "pattern": "Rectangle",             "timeframe": "D",  "filename": "trevor_05_rectangle.png"},
    {"stock": "NSE:WIPRO",      "pattern": "Descending Triangle",   "timeframe": "D",  "filename": "trevor_06_desc_triangle.png"},
    {"stock": "NSE:TATASTEEL",  "pattern": "Ascending Triangle",    "timeframe": "W",  "filename": "trevor_07_asc_triangle.png"},
    {"stock": "NSE:MARUTI",     "pattern": "Symmetrical Triangle",  "timeframe": "D",  "filename": "trevor_08_sym_triangle.png"},
    {"stock": "NSE:SUNPHARMA",  "pattern": "Diamond Top",           "timeframe": "240","filename": "trevor_09_diamond_top.png"},
    {"stock": "NSE:BAJFINANCE", "pattern": "Wedge",                 "timeframe": "D",  "filename": "trevor_10_wedge.png"},
]

# PDF 2: Sharvari Itagi (MSF14)
SHARVARI_PATTERNS = [
    {"stock": "NSE:TCS",          "pattern": "Double Top",            "timeframe": "D",  "filename": "sharvari_01_double_top.png"},
    {"stock": "NSE:SBIN",         "pattern": "Double Bottom",         "timeframe": "D",  "filename": "sharvari_02_double_bottom.png"},
    {"stock": "NSE:ASIANPAINT",   "pattern": "Triple Top",            "timeframe": "W",  "filename": "sharvari_03_triple_top.png"},
    {"stock": "NSE:LT",           "pattern": "Triple Bottom",         "timeframe": "D",  "filename": "sharvari_04_triple_bottom.png"},
    {"stock": "NSE:ITC",          "pattern": "Rectangle",             "timeframe": "D",  "filename": "sharvari_05_rectangle.png"},
    {"stock": "NSE:TATACONSUM",   "pattern": "Descending Triangle",   "timeframe": "D",  "filename": "sharvari_06_desc_triangle.png"},
    {"stock": "NSE:POWERGRID",    "pattern": "Ascending Triangle",    "timeframe": "W",  "filename": "sharvari_07_asc_triangle.png"},
    {"stock": "NSE:KOTAKBANK",    "pattern": "Symmetrical Triangle",  "timeframe": "D",  "filename": "sharvari_08_sym_triangle.png"},
    {"stock": "NSE:NESTLEIND",    "pattern": "Diamond Top",           "timeframe": "240","filename": "sharvari_09_diamond_top.png"},
    {"stock": "NSE:ADANIPORTS",   "pattern": "Wedge",                 "timeframe": "D",  "filename": "sharvari_10_wedge.png"},
]


def take_screenshots(patterns, browser_context):
    page = browser_context.new_page()

    for i, item in enumerate(patterns):
        stock = item["stock"]
        tf = item["timeframe"]
        fname = item["filename"]
        pattern = item["pattern"]

        print(f"\n[{i+1}/{len(patterns)}] Opening {stock} ({tf}) - Looking for: {pattern}")

        url = f"https://in.tradingview.com/chart/?symbol={stock}&interval={tf}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Wait for chart to render
        time.sleep(8)

        # Try to close any popups/banners
        try:
            page.click('button:has-text("Got it")', timeout=3000)
        except:
            pass
        try:
            page.click('[data-name="close"]', timeout=2000)
        except:
            pass

        # Wait a bit more for chart to fully load
        time.sleep(3)

        filepath = os.path.join(OUTPUT_DIR, fname)
        page.screenshot(path=filepath, full_page=False)
        print(f"   Saved: {filepath}")
        print(f"   >>> NOW: Draw the {pattern} pattern lines on the chart <<<")
        print(f"   >>> Press ENTER when you're done annotating to continue <<<")

        # PAUSE: Let user draw pattern annotations manually
        input(f"   [Waiting] Draw '{pattern}' on {stock}, then press ENTER...")

        # Take the annotated screenshot
        annotated_path = os.path.join(OUTPUT_DIR, fname.replace('.png', '_annotated.png'))
        page.screenshot(path=annotated_path, full_page=False)
        print(f"   Annotated screenshot saved: {annotated_path}")

    page.close()


def main():
    print("=" * 60)
    print("TradingView Chart Pattern Screenshot Tool")
    print("=" * 60)
    print()
    print("This script will:")
    print("1. Open each stock on TradingView")
    print("2. Wait for you to draw pattern annotations")
    print("3. Save the annotated screenshot")
    print()
    print("IMPORTANT: Make sure you're logged into TradingView")
    print("in your default browser first!")
    print()

    with sync_playwright() as p:
        # Launch with headed mode so you can see and interact
        browser = p.chromium.launch(
            headless=False,  # VISIBLE browser so you can draw!
            slow_mo=500
        )
        context = browser.new_context(
            viewport={'width': 1400, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        print("\n--- PDF 1: Trevor Dcosta (MSF07) ---")
        take_screenshots(TREVOR_PATTERNS, context)

        print("\n--- PDF 2: Sharvari Itagi (MSF14) ---")
        take_screenshots(SHARVARI_PATTERNS, context)

        browser.close()

    print("\n" + "=" * 60)
    print("ALL DONE!")
    print(f"Screenshots saved in: {OUTPUT_DIR}/")
    print("Share these with Claude to build the final PDFs.")
    print("=" * 60)


if __name__ == "__main__":
    main()
