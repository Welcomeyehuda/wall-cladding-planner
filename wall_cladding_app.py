# wall_cladding_app.py
import streamlit as st
import matplotlib.pyplot as plt
import random
import math
import urllib.parse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime
import tempfile

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
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 50, "Wall Cladding Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(50, height - 110, f"Wall size: {wall_width} x {wall_height} cm")
    c.drawString(50, height - 140, f"Plates: {num_plates}")
    c.drawString(50, height - 170, f"Strips: {num_sargels}")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        img = ImageReader(tmpfile.name)
        c.drawImage(img, 50, 250, width=500, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# פונקציית שרטוט
def draw_wall(wall_width, wall_height, mode, manual_sargels=0, sargel_position="End"):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    plate_color = "#D9E4DD"
    sargel_color = "#BFA6A0"
    x = 0
    num_plates, num_sargels = 0, 0

    if mode == "Manual":
        while x < wall_width:
            if wall_width - x >= PLATE_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), PLATE_WIDTH, wall_height, edgecolor='black', facecolor=plate_color))
                x += PLATE_WIDTH
                num_plates += 1
            else:
                ax.add_patch(plt.Rectangle((x, 0), wall_width - x, wall_height, edgecolor='black', facecolor=plate_color))
                num_plates += 1
                break
        if sargel_position == "Start":
            x = 0
        elif sargel_position == "Center":
            x = wall_width / 2 - (manual_sargels * SARGEL_WIDTH) / 2
        elif sargel_position == "End":
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
    ax.text(wall_width / 2, -10, f"Width: {wall_width} cm", ha='center', fontsize=12)
    ax.text(-10, wall_height / 2, f"Height: {wall_height} cm", va='center', rotation=90, fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Wall Layout")
    st.pyplot(fig)
    return num_plates, num_sargels, fig

# ממשק ראשי
st.title("Wall Cladding App - Welcome Design")
st.markdown("Enter dimensions and choose layout method")

wall_width = st.number_input("Wall Width (cm):", min_value=100, max_value=10000, value=360)
wall_height = st.number_input("Wall Height (cm):", min_value=100, max_value=400, value=280)
layout_type = st.radio("Layout type:", ["Automatic", "Manual"])
manual_sargels = 0
sargel_position = "End"

if layout_type == "Manual":
    manual_sargels = st.number_input("Number of strips to add:", min_value=0, value=2)
    sargel_position = st.selectbox("Strip placement on wall:", ["Start", "Center", "End"])

if st.button("📐 Generate Layout"):
    num_plates, num_sargels, fig = draw_wall(wall_width, wall_height, layout_type, manual_sargels, sargel_position)

    pdf_buffer = create_pdf(wall_width, wall_height, num_plates, num_sargels, fig)
    st.download_button(label="📄 Download PDF", data=pdf_buffer, file_name="wall_cladding_plan.pdf")

    text = f"Wall Cladding Plan\nWidth: {wall_width} cm | Height: {wall_height} cm\nPlates: {num_plates} | Strips: {num_sargels}"
    encoded = urllib.parse.quote(text)
    whatsapp_url = f"https://wa.me/?text={encoded}"
    st.markdown(f"[📤 Share via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
