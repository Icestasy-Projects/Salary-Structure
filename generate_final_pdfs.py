"""
Generate 2 uniform PDFs for Technical Analysis assignment using
chart images extracted from 4 reference PDFs.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "extracted_images")
LOGO_PATH = os.path.join(IMG_DIR, "vidhi", "img-000.png")

PAGE_W, PAGE_H = A4

TREVOR_CHARTS = [
    {"pattern": "Double Top",            "stock": "Apollo Hospitals Enterprise Ltd. (NSE)", "timeframe": "30 min", "source": "apurva/img-000.png"},
    {"pattern": "Double Bottom",         "stock": "HDFC Bank Ltd. (NSE)",                  "timeframe": "Daily",  "source": "vidhi/img-002.png"},
    {"pattern": "Triple Top",            "stock": "Bajaj Holdings & Investment Ltd. (NSE)", "timeframe": "Daily",  "source": "shivanjali/img-002.png"},
    {"pattern": "Triple Bottom",         "stock": "Larsen & Toubro Ltd. (NSE)",             "timeframe": "Daily",  "source": "vidhi/img-004.png"},
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
    {"pattern": "Triple Bottom",         "stock": "Wipro Ltd. (NSE)",                       "timeframe": "Daily",  "source": "shivanjali/img-001.png"},
    {"pattern": "Rectangle (Box)",       "stock": "Kalyan Jewellers India Ltd. (NSE)",      "timeframe": "Daily",  "source": "vidhi/img-005.png"},
    {"pattern": "Descending Triangle",   "stock": "Hindalco Industries Ltd. (NSE)",         "timeframe": "Daily",  "source": "apurva/img-005.png"},
    {"pattern": "Ascending Triangle",    "stock": "Reliance Industries Ltd. (NSE)",         "timeframe": "Daily",  "source": "shivanjali/img-005.png"},
    {"pattern": "Symmetrical Triangle",  "stock": "State Bank of India (NSE)",              "timeframe": "Daily",  "source": "shivanjali/img-006.png"},
    {"pattern": "Diamond Top",           "stock": "Dr. Lal PathLabs Ltd. (NSE)",            "timeframe": "4 Hour", "source": "apurva/img-008.png"},
    {"pattern": "Wedge",                 "stock": "Titan Company Ltd. (NSE)",               "timeframe": "Daily",  "source": "shivanjali/img-008.png"},
]

DARK_BLUE = HexColor("#1a237e")
MEDIUM_BLUE = HexColor("#283593")
LIGHT_BLUE = HexColor("#e8eaf6")
ACCENT = HexColor("#1565c0")
TEXT_DARK = HexColor("#212121")
TEXT_GRAY = HexColor("#616161")
WHITE = HexColor("#ffffff")
BORDER_COLOR = HexColor("#90caf9")


def draw_cover_page(c, name, roll_no):
    c.setFillColor(WHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    header_h = 3.2 * cm
    c.setFillColor(DARK_BLUE)
    c.rect(0, PAGE_H - header_h, PAGE_W, header_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.3 * cm, "TECHNICAL ANALYSIS")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.5 * cm, "Chart Pattern Recognition Project")

    if os.path.exists(LOGO_PATH):
        logo_w, logo_h = 5 * cm, 5 * cm
        logo_x = (PAGE_W - logo_w) / 2
        logo_y = PAGE_H - header_h - logo_h - 1.5 * cm
        try:
            c.drawImage(LOGO_PATH, logo_x, logo_y, logo_w, logo_h,
                       preserveAspectRatio=True, mask='auto')
        except:
            pass

    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 14)
    college_y = PAGE_H - header_h - 7.5 * cm
    c.drawCentredString(PAGE_W / 2, college_y, "Sydenham Institute of Management Studies,")
    c.drawCentredString(PAGE_W / 2, college_y - 0.6 * cm, "Research & Entrepreneurship Education")

    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    line_y = college_y - 1.5 * cm
    c.line(3 * cm, line_y, PAGE_W - 3 * cm, line_y)

    info_y = line_y - 1.5 * cm
    left_x = 4.5 * cm
    right_x = PAGE_W - 4.5 * cm

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(TEXT_DARK)
    labels = [
        ("Submitted By:", name),
        ("Roll No:", roll_no),
        ("Semester:", "3"),
        ("Subject:", "Technical Analysis"),
    ]
    for i, (label, value) in enumerate(labels):
        y = info_y - i * 1.0 * cm
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(TEXT_GRAY)
        c.drawString(left_x, y, label)
        c.setFont("Helvetica", 12)
        c.setFillColor(TEXT_DARK)
        c.drawString(left_x + 4.5 * cm, y, value)

    sub_y = info_y - 5.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(TEXT_GRAY)
    c.drawString(left_x, sub_y, "Submitted To:")
    c.setFont("Helvetica", 12)
    c.setFillColor(TEXT_DARK)
    c.drawString(left_x + 4.5 * cm, sub_y, "Prof. Satyaprakash Tiwari")

    footer_h = 1.2 * cm
    c.setFillColor(DARK_BLUE)
    c.rect(0, 0, PAGE_W, footer_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, 0.4 * cm, "Semester 3  |  Technical Analysis  |  Chart Pattern Recognition")

    c.showPage()


def draw_chart_page(c, pattern_num, pattern_name, stock_name, timeframe, image_path):
    c.setFillColor(WHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    header_h = 1.8 * cm
    c.setFillColor(DARK_BLUE)
    c.rect(0, PAGE_H - header_h, PAGE_W, header_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.2 * cm,
                       f"{pattern_num}. {pattern_name}")

    info_y = PAGE_H - header_h - 1.0 * cm
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, info_y, f"Stock: {stock_name}")
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT_GRAY)
    c.drawString(2 * cm, info_y - 0.5 * cm, f"Timeframe: {timeframe}")

    full_img_path = os.path.join(IMG_DIR, image_path)
    if os.path.exists(full_img_path):
        img = Image.open(full_img_path)
        img_w, img_h = img.size
        aspect = img_w / img_h

        avail_w = PAGE_W - 3 * cm
        avail_h = PAGE_H - header_h - 5 * cm

        if avail_w / aspect <= avail_h:
            draw_w = avail_w
            draw_h = avail_w / aspect
        else:
            draw_h = avail_h
            draw_w = avail_h * aspect

        img_x = (PAGE_W - draw_w) / 2
        img_y = PAGE_H - header_h - 2.5 * cm - draw_h

        c.setStrokeColor(BORDER_COLOR)
        c.setLineWidth(1)
        border_pad = 4
        c.rect(img_x - border_pad, img_y - border_pad,
               draw_w + 2 * border_pad, draw_h + 2 * border_pad,
               fill=0, stroke=1)

        c.drawImage(full_img_path, img_x, img_y, draw_w, draw_h,
                   preserveAspectRatio=True)
    else:
        c.setFillColor(TEXT_GRAY)
        c.setFont("Helvetica", 14)
        c.drawCentredString(PAGE_W / 2, PAGE_H / 2, f"[Chart image not found: {image_path}]")

    footer_h = 1.2 * cm
    c.setFillColor(DARK_BLUE)
    c.rect(0, 0, PAGE_W, footer_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, 0.4 * cm,
                       f"Technical Analysis  |  Pattern {pattern_num}/10  |  Chart Pattern Recognition Project")

    c.showPage()


def generate_pdf(filename, name, roll_no, charts):
    output_path = os.path.join(BASE, filename)
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(f"Technical Analysis - Chart Pattern Recognition - {name}")
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

    print("\nDone! Both PDFs generated.")
    print("\nTrevor's stocks: " + ", ".join(c["stock"].split("(")[0].strip() for c in TREVOR_CHARTS))
    print("Sharvari's stocks: " + ", ".join(c["stock"].split("(")[0].strip() for c in SHARVARI_CHARTS))


if __name__ == "__main__":
    main()
