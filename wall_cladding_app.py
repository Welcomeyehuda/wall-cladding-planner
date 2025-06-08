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
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# רישום גופן עברי
pdfmetrics.registerFont(TTFont('David', 'DavidLibre-Medium.ttf'))

def rtl(text):
    return get_display(arabic_reshaper.reshape(text))

# הגדרות מוצרים
SARGEL_WIDTH = 12
SARGEL_HEIGHT = 290
PLATE_WIDTH = 120
PLATE_HEIGHT = 280

# פונקציית שרטוט
def draw_wall(wall_width, wall_height, mode, num_sargels_manual=0):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')

    sargels = []
    plates = []
    x = 0
    while x < wall_width:
        if mode == 'תכנון אוטומטי':
            choice = random.choice(['plate', 'sargel', 'mix'])
            if choice == 'plate' and x + PLATE_WIDTH <= wall_width:
                plates.append((x, 0))
                x += PLATE_WIDTH
            elif choice == 'sargel' and x + SARGEL_WIDTH <= wall_width:
                sargels.append((x, 0))
                x += SARGEL_WIDTH
            elif choice == 'mix' and x + PLATE_WIDTH + SARGEL_WIDTH <= wall_width:
                plates.append((x, 0))
                x += PLATE_WIDTH
                sargels.append((x, 0))
                x += SARGEL_WIDTH
            else:
                break
        else:  # תכנון ידני
            for _ in range(num_sargels_manual):
                if x + PLATE_WIDTH <= wall_width:
                    plates.append((x, 0))
                    x += PLATE_WIDTH
                    sargels.append((x, 0))
                    x += SARGEL_WIDTH
            break

    for x, y in plates:
        ax.add_patch(plt.Rectangle((x, y), PLATE_WIDTH, wall_height, color='lightgray', edgecolor='black'))
    for x, y in sargels:
        ax.add_patch(plt.Rectangle((x, y), SARGEL_WIDTH, wall_height, color='dimgray', edgecolor='black'))

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("הדמיית קיר")
    return fig, len(plates), len(sargels)

# פונקציה ליצירת PDF עם תמונה + חישוב כמויות
def create_pdf(wall_width, wall_height, num_plates, num_sargels, fig):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("David", 14)
    c.drawRightString(width - 50, height - 50, rtl('דו"ח חיפוי קיר'))
    c.setFont("David", 12)
    c.drawRightString(width - 50, height - 80, rtl(f"מידות קיר: {wall_width}x{wall_height} ס\"מ"))
    c.drawRightString(width - 50, height - 110, rtl(f"פלטות נדרשות: {num_plates} יחידות"))
    c.drawRightString(width - 50, height - 140, rtl(f"סרגלים נדרשים: {num_sargels} יחידות"))

    c.drawRightString(width - 50, height - 180, rtl("הנחיות התקנה:"))
    c.setFont("David", 10)
    c.drawRightString(width - 50, height - 200, rtl("1. יש לוודא שהקיר ישר ונקי לפני תחילת ההתקנה."))
    c.drawRightString(width - 50, height - 220, rtl("2. מומלץ להתחיל מהמרכז או לפי סימון מראש."))
    c.drawRightString(width - 50, height - 240, rtl("3. להשתמש בדבק מתאים לפי סוג המשטח."))
    c.drawRightString(width - 50, height - 260, rtl("4. את הסרגלים יש למקם בהתאם לתכנון."))
    c.drawRightString(width - 50, height - 280, rtl("5. לבצע חיתוכים לפי צורך, תוך שמירה על מראה רציף."))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        img = ImageReader(tmpfile.name)
        c.drawImage(img, 50, 20, width=500, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ממשק Streamlit
st.set_page_config(page_title="מתכנן חיפוי קיר", layout="centered")
st.title("🧱 מתכנן חיפוי קיר - Welcome Design")

wall_width = st.number_input("רוחב הקיר (ס\"מ):", min_value=50, max_value=1000, value=360)
wall_height = st.number_input("גובה הקיר (ס\"מ):", min_value=50, max_value=300, value=280)

mode = st.radio("בחר שיטת תכנון:", ["תכנון אוטומטי", "תכנון ידני"])
num_sargels_manual = 0
if mode == "תכנון ידני":
    num_sargels_manual = st.number_input("כמה סרגלים למקם (מיד אחרי כל פלטה)?", min_value=1, max_value=20, value=3)

if st.button("📐 צור הדמיה"):
    fig, num_plates, num_sargels = draw_wall(wall_width, wall_height, mode, num_sargels_manual)
    st.pyplot(fig)

    pdf = create_pdf(wall_width, wall_height, num_plates, num_sargels, fig)
    st.download_button("📄 הורד דו\"ח PDF", data=pdf, file_name="wall_cladding_plan.pdf")

    text = f"תכננתי קיר ברוחב {wall_width} ס\"מ וגובה {wall_height} ס\"מ עם {num_plates} פלטות ו-{num_sargels} סרגלים."
    url = "https://api.whatsapp.com/send?text=" + urllib.parse.quote(text)
    st.markdown(f"[📤 שתף בוואטסאפ]({url})")
