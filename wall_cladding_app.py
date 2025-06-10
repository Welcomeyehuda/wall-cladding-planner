# wall_cladding_app.py
import streamlit as st
import matplotlib.pyplot as plt
import random
import math
import urllib.parse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from datetime import datetime
import tempfile

# הרשמת גופן תומך עברית
pdfmetrics.registerFont(TTFont('David', 'DavidLibre-Medium.ttf'))

# הגדרות מוצרים
SARGEL_WIDTH = 12
SARGEL_HEIGHT = 290
PLATE_WIDTH = 120
PLATE_HEIGHT = 280

# פונקציה ליצירת PDF עם תמונה

def create_pdf(wall_width, wall_height, num_plates, num_sargels, fig):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("David", 14)
    c.drawRightString(width - 50, height - 50, "דו""ח חיפוי קיר")
    c.setFont("David", 12)
    c.drawRightString(width - 50, height - 80, f"תאריך: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawRightString(width - 50, height - 110, f"מידות קיר: {wall_width}x{wall_height} ס""מ")
    c.drawRightString(width - 50, height - 140, f"פלטות: {num_plates}")
    c.drawRightString(width - 50, height - 170, f"סרגלים: {num_sargels}")

    # שמירת התרשים לתמונה זמנית והוספה ל-PDF
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        img = ImageReader(tmpfile.name)
        c.drawImage(img, 50, 250, width=500, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# פונקציית שרטוט

def draw_wall(wall_width, wall_height, mode, manual_sargels=0, sargel_position="סוף"):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    plate_color = "#D9E4DD"
    sargel_color = "#BFA6A0"
    x = 0
    num_plates, num_sargels = 0, 0

    if mode == "תכנון ידני":
        while x < wall_width:
            if wall_width - x >= PLATE_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), PLATE_WIDTH, wall_height, edgecolor='black', facecolor=plate_color))
                x += PLATE_WIDTH
                num_plates += 1
            else:
                ax.add_patch(plt.Rectangle((x, 0), wall_width - x, wall_height, edgecolor='black', facecolor=plate_color))
                num_plates += 1
                break
        if sargel_position == "תחילת הקיר":
            x = 0
        elif sargel_position == "אמצע הקיר":
            x = wall_width / 2 - (manual_sargels * SARGEL_WIDTH) / 2
        elif sargel_position == "סוף הקיר":
            x = wall_width - (manual_sargels * SARGEL_WIDTH)

        for _ in range(manual_sargels):
            if x + SARGEL_WIDTH <= wall_width:
                ax.add_patch(plt.Rectangle((x, 0), SARGEL_WIDTH, wall_height, edgecolor='black', facecolor=sargel_color))
                x += SARGEL_WIDTH
                num_sargels += 1

    else:
        while wall_width - x >= min(PLATE_WIDTH, SARGEL_WIDTH):
            choice = random.choice(["plates", "sargels"])
            if choice == "plates" and wall_width - x >= PLATE_WIDTH:
                for _ in range(random.randint(1, 2)):
                    if wall_width - x >= PLATE_WIDTH:
                        ax.add_patch(plt.Rectangle((x, 0), PLATE_WIDTH, wall_height, edgecolor='black', facecolor=plate_color))
                        x += PLATE_WIDTH
                        num_plates += 1
            elif choice == "sargels" and wall_width - x >= SARGEL_WIDTH:
                for _ in range(random.randint(1, 5)):
                    if wall_width - x >= SARGEL_WIDTH:
                        ax.add_patch(plt.Rectangle((x, 0), SARGEL_WIDTH, wall_height, edgecolor='black', facecolor=sargel_color))
                        x += SARGEL_WIDTH
                        num_sargels += 1

        remaining = wall_width - x
        if remaining > 0:
            color = plate_color if random.choice([True, False]) else sargel_color
            ax.add_patch(plt.Rectangle((x, 0), remaining, wall_height, edgecolor='black', facecolor=color))

    # תוספת טקסט מידות
    ax.text(wall_width / 2, -10, f"רוחב: {wall_width} ס""מ", ha='center', fontsize=12)
    ax.text(-10, wall_height / 2, f"גובה: {wall_height} ס""מ", va='center', rotation=90, fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("הדמיית קיר")
    st.pyplot(fig)
    return num_plates, num_sargels, fig

# ממשק ראשי
st.markdown("""
<div dir="rtl">
<h3>אפליקציית תכנון חיפוי קיר - Welcome Design</h3>
<p>הזן את המידות ובחר את סוג וסידור הסרגלים</p>
</div>
""", unsafe_allow_html=True)

wall_width = st.number_input("רוחב הקיר (ס\"מ):", min_value=100, max_value=10000, value=360)
wall_height = st.number_input("גובה הקיר (ס\"מ):", min_value=100, max_value=400, value=280)
layout_type = st.radio("בחר שיטת תכנון:", ["תכנון אוטומטי", "תכנון ידני"])
manual_sargels = 0
sargel_position = "סוף הקיר"

if layout_type == "תכנון ידני":
    manual_sargels = st.number_input("כמה סרגלים להוסיף:", min_value=0, value=2)
    sargel_position = st.selectbox("מיקום הסרגלים בקיר:", ["תחילת הקיר", "אמצע הקיר", "סוף הקיר"])

if st.button("📐 צור הדמיה"):
    num_plates, num_sargels, fig = draw_wall(wall_width, wall_height, layout_type, manual_sargels, sargel_position)

    pdf_buffer = create_pdf(wall_width, wall_height, num_plates, num_sargels, fig)
    st.download_button(label="📄 הורד PDF", data=pdf_buffer, file_name="wall_cladding_plan.pdf")

    # שיתוף בוואטסאפ
    text = f"תכנון חיפוי קיר\nרוחב: {wall_width} ס\"מ | גובה: {wall_height} ס\"מ\nפלטות: {num_plates} | סרגלים: {num_sargels}"
    encoded = urllib.parse.quote(text)
    whatsapp_url = f"https://wa.me/?text={encoded}"
    st.markdown(f"[📤 שתף בוואטסאפ]({whatsapp_url})", unsafe_allow_html=True)
