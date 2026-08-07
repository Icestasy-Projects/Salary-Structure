"""
Generate 2 uniform PDFs for Technical Analysis assignment using
chart images extracted from 4 reference PDFs.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black
from reportlab.pdfgen import canvas
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "extracted_images")
LOGO_PATH = os.path.join(IMG_DIR, "vidhi", "img-000.png")

PAGE_W, PAGE_H = A4

TREVOR_CHARTS = [
    {"pattern": "Double Top",            "stock": "Apollo Hospitals Enterprise Ltd. (NSE)", "timeframe": "30 min", "source": "apurva/img-000.png"},
    {"pattern": "Double Bottom",         "stock": "Honasa Consumer Ltd. (NSE)",             "timeframe": "Daily",  "source": "apurva/img-001.png"},
    {"pattern": "Triple Top",            "stock": "Bajaj Holdings & Investment Ltd. (NSE)", "timeframe": "Daily",  "source": "shivanjali/img-002.png"},
    {"pattern": "Triple Bottom",         "stock": "Wipro Ltd. (NSE)",                       "timeframe": "Daily",  "source": "shivanjali/img-001.png"},
    {"pattern": "Rectangle (Box)",       "stock": "Jio Financial Services Ltd. (NSE)",      "timeframe": "Daily",  "source": "apurva/img-004.png"},
    {"pattern": "Descending Triangle",   "stock": "Hindustan Unilever Ltd. (NSE)",          "timeframe": "Daily",  "source": "shivanjali/img-004.png"},
    {"pattern": "Ascending Triangle",    "stock": "Nestle India Ltd. (NSE)",                "timeframe": "Daily",  "source": "vidhi/img-007.png"},
    {"pattern": "Symmetrical Triangle",  "stock": "ABB India Ltd. (NSE)",                   "timeframe": "Daily",  "source": "apurva/img-007.png"},
    {"pattern": "Diamond Top",           "stock": "ICICI Bank Ltd. (NSE)",                  "timeframe": "Daily",  "source": "shivanjali/img-007.png"},
    {"pattern": "Wedge",                 "stock": "Anant Raj Ltd. (NSE)",                   "timeframe": "Daily",  "source": "vidhi/img-010.png"},
]

SHARVARI_CHARTS = [
    {"pattern": "Double Top",            "stock": "DCB Bank Ltd. (NSE)",                    "timeframe": "Daily",  "source": "vidhi/img-001.png"},
    {"pattern": "Double Bottom",         "stock": "Tata Motors Ltd. (NSE)",                 "timeframe": "Daily",  "source": "shivanjali/img-000.png"},
    {"pattern": "Triple Top",            "stock": "Hindustan Zinc Ltd. (NSE)",              "timeframe": "Daily",  "source": "apurva/img-002.png"},
    {"pattern": "Triple Bottom",         "stock": "Mahindra Logistics Ltd. (NSE)",          "timeframe": "30 min", "source": "apurva/img-003.png"},
    {"pattern": "Rectangle (Box)",       "stock": "Kalyan Jewellers India Ltd. (NSE)",      "timeframe": "Daily",  "source": "vidhi/img-005.png"},
    {"pattern": "Descending Triangle",   "stock": "Hindalco Industries Ltd. (NSE)",         "timeframe": "Daily",  "source": "apurva/img-005.png"},
    {"pattern": "Ascending Triangle",    "stock": "Reliance Industries Ltd. (NSE)",         "timeframe": "Daily",  "source": "shivanjali/img-005.png"},
    {"pattern": "Symmetrical Triangle",  "stock": "State Bank of India (NSE)",              "timeframe": "Daily",  "source": "shivanjali/img-006.png"},
    {"pattern": "Diamond Top",           "stock": "Dr. Lal PathLabs Ltd. (NSE)",            "timeframe": "4 Hour", "source": "apurva/img-008.png"},
    {"pattern": "Wedge",                 "stock": "Titan Company Ltd. (NSE)",               "timeframe": "Daily",  "source": "shivanjali/img-008.png"},
]

BLACK = HexColor("#000000")
GRAY = HexColor("#555555")


def draw_cover_page(c, name, roll_no):
    c.setFont("Times-Bold", 26)
    c.setFillColor(BLACK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 3.5 * cm, "TECHNICAL ANALYSIS")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.8 * cm, "PROJECT")

    if os.path.exists(LOGO_PATH):
        logo_size = 6 * cm
        logo_x = (PAGE_W - logo_size) / 2
        logo_y = PAGE_H - 5.5 * cm - logo_size
        try:
            c.drawImage(LOGO_PATH, logo_x, logo_y, logo_size, logo_size,
                       preserveAspectRatio=True, mask='auto')
        except:
            pass

    right_x = PAGE_W - 4 * cm
    info_y = PAGE_H - 13.5 * cm

    c.setFont("Times-Bold", 14)
    c.drawRightString(right_x, info_y, "Submitted To:")
    c.setFont("Times-Roman", 13)
    c.drawRightString(right_x, info_y - 0.6 * cm, "Prof. Satyaprakash Tiwari")

    c.setFont("Times-Bold", 14)
    c.drawRightString(right_x, info_y - 1.8 * cm, "Submitted By:")
    c.setFont("Times-Roman", 13)
    c.drawRightString(right_x, info_y - 2.4 * cm, name)
    c.drawRightString(right_x, info_y - 3.0 * cm, roll_no)

    c.showPage()


def draw_chart_page(c, pattern_num, pattern_name, stock_name, timeframe, image_path):
    top_y = PAGE_H - 2 * cm

    c.setFont("Times-Bold", 16)
    c.setFillColor(BLACK)
    c.drawString(2 * cm, top_y, f"{pattern_num}.  {pattern_name}")

    full_img_path = os.path.join(IMG_DIR, image_path)
    if os.path.exists(full_img_path):
        img = Image.open(full_img_path)
        img_w, img_h = img.size
        aspect = img_w / img_h

        avail_w = PAGE_W - 4 * cm
        avail_h = PAGE_H - 5.5 * cm

        if avail_w / aspect <= avail_h:
            draw_w = avail_w
            draw_h = avail_w / aspect
        else:
            draw_h = avail_h
            draw_w = avail_h * aspect

        img_x = (PAGE_W - draw_w) / 2
        img_y = top_y - 1.2 * cm - draw_h

        c.drawImage(full_img_path, img_x, img_y, draw_w, draw_h,
                   preserveAspectRatio=True)

    c.showPage()


def generate_pdf(filename, name, roll_no, charts):
    output_path = os.path.join(BASE, filename)
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(f"Technical Analysis - {name}")
    c.setAuthor(name)

    draw_cover_page(c, name, roll_no)

    for i, chart in enumerate(charts, 1):
        draw_chart_page(c, i, chart["pattern"], chart["stock"],
                       chart["timeframe"], chart["source"])

    c.save()
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Generated: {output_path} ({size_kb:.1f} KB)")


def main():
    for img_info in TREVOR_CHARTS + SHARVARI_CHARTS:
        full_path = os.path.join(IMG_DIR, img_info["source"])
        if not os.path.exists(full_path):
            print(f"WARNING: Missing image: {full_path}")

    print("Generating Trevor Dcosta MSF07 PDF...")
    generate_pdf("Trevor_Dcosta_MSF07.pdf", "Trevor Dcosta", "MSF07", TREVOR_CHARTS)

    print("Generating Sharvari Itagi MSF14 PDF...")
    generate_pdf("Sharvari_Itagi_MSF14.pdf", "Sharvari Itagi", "MSF14", SHARVARI_CHARTS)

    print("\nDone!")


if __name__ == "__main__":
    main()
