# wall_cladding_app.py
import streamlit as st
import matplotlib.pyplot as plt
import random
import math
import urllib.parse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

# הגדרות מוצרים
SARGEL_WIDTH = 12  # ס"מ
SARGEL_HEIGHT = 290
PLATE_WIDTH = 120
PLATE_HEIGHT = 280

# פונקציה ליצירת PDF

def create_pdf(wall_width, wall_height, num_plates, num_sargels):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 14)
    c.drawString(50, height - 50, "דו\"ח חיפוי קיר")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"תאריך: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(50, height - 110, f"מידות קיר: {wall_width}x{wall_height} ס\"מ")
    c.drawString(50, height - 140, f"פלטות: {num_plates}")
    c.drawString(50, height - 170, f"סרגלים: {num_sargels}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# פונקציית שרטוט

def draw_wall(wall_width, wall_height, mode, manual_sargels=0):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    x = 0

    plate_color = "#D9E4DD"
    sargel_color = "#BFA6A0"
    num_plates, num_sargels = 0, 0

    if mode == "תכנון ידני":
        while x < wall_width:
            if wall_width - x >= PLATE_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), PLATE_WIDTH, wall_height, edgecolor='black', facecolor=plate_color))
                x += PLATE_WIDTH
                num_plates += 1
                if manual_sargels > 0:
                    ax.add_patch(plt.Rectangle((x, 0), SARGEL_WIDTH, wall_height, edgecolor='black', facecolor=sargel_color))
                    x += SARGEL_WIDTH
                    num_sargels += 1
                    manual_sargels -= 1
            else:
                ax.add_patch(plt.Rectangle((x, 0), wall_width - x, wall_height, edgecolor='black', facecolor=plate_color))
                num_plates += 1
                break
    else:  # תכנון אוטומטי עם רנדומליות
        pattern = random.choice(["start_sargel", "start_plate"])
        while x < wall_width:
            if pattern == "start_sargel" and wall_width - x >= SARGEL_WIDTH:
                num = random.randint(1, 3)
                for _ in range(num):
                    if wall_width - x >= SARGEL_WIDTH:
                        ax.add_patch(plt.Rectangle((x, 0), SARGEL_WIDTH, wall_height, edgecolor='black', facecolor=sargel_color))
                        x += SARGEL_WIDTH
                        num_sargels += 1
                pattern = "plate"
            elif pattern == "plate" and wall_width - x >= PLATE_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), PLATE_WIDTH, wall_height, edgecolor='black', facecolor=plate_color))
                x += PLATE_WIDTH
                num_plates += 1
                pattern = random.choice(["sargel", "plate"])
            elif pattern == "sargel" and wall_width - x >= SARGEL_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), SARGEL_WIDTH, wall_height, edgecolor='black', facecolor=sargel_color))
                x += SARGEL_WIDTH
                num_sargels += 1
                pattern = "plate"
            else:
                break

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("הדמיית קיר")
    st.pyplot(fig)
    return num_plates, num_sargels

# ממשק ראשי
st.title("אפליקציית תכנון חיפוי קיר - Welcome Design")
st.markdown("הזן את המידות ובחר סוג תכנון")

wall_width = st.number_input("רוחב הקיר (ס\"מ):", min_value=100, max_value=10000, value=360)
wall_height = st.number_input("גובה הקיר (ס\"מ):", min_value=100, max_value=400, value=280)

layout_type = st.radio("בחר שיטת תכנון:", ["תכנון אוטומטי", "תכנון ידני"])
manual_sargels = 0

if layout_type == "תכנון ידני":
    manual_sargels = st.number_input("כמה סרגלים להוסיף (אחרי כל פלטה שלמה):", min_value=0, value=2)

if st.button("📐 צור הדמיה"):
    num_plates, num_sargels = draw_wall(wall_width, wall_height, layout_type, manual_sargels)

    pdf_buffer = create_pdf(wall_width, wall_height, num_plates, num_sargels)
    st.download_button(label="📄 הורד PDF", data=pdf_buffer, file_name="wall_cladding_plan.pdf")

    # שיתוף בוואטסאפ
    text = f"תכנון חיפוי קיר\nרוחב: {wall_width} ס\"מ | גובה: {wall_height} ס\"מ\nפלטות: {num_plates} | סרגלים: {num_sargels}"
    encoded = urllib.parse.quote(text)
    whatsapp_url = f"https://wa.me/?text={encoded}"
    st.markdown(f"[📤 שתף בוואטסאפ]({whatsapp_url})", unsafe_allow_html=True)
