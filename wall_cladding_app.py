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
import os
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

def draw_wall(wall_width, wall_height, mode, num_sargels_manual=0, sargel_position='סוף הקיר'):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')

    sargels = []
    plates = []
    x = 0

    if mode == 'תכנון אוטומטי':
        while x < wall_width:
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
        if sargel_position == 'תחילת הקיר':
            for i in range(num_sargels_manual):
                if x + SARGEL_WIDTH <= wall_width:
                    sargels.append((x, 0))
                    x += SARGEL_WIDTH
        elif sargel_position == 'אמצע הקיר':
            x = (wall_width - (num_sargels_manual * SARGEL_WIDTH)) // 2
            for i in range(num_sargels_manual):
                sargels.append((x + i * SARGEL_WIDTH, 0))
            x = 0
        # לאחר סרגלים, נתחיל להכניס פלטות מההתחלה או מאיפה שנגמר הסרגלים
        current_x = 0
        while current_x + PLATE_WIDTH <= wall_width:
            plates.append((current_x, 0))
            current_x += PLATE_WIDTH
        if sargel_position == 'סוף הקיר':
            current_x = wall_width - num_sargels_manual * SARGEL_WIDTH
            for i in range(num_sargels_manual):
                if current_x + SARGEL_WIDTH <= wall_width:
                    sargels.append((current_x + i * SARGEL_WIDTH, 0))

    for x, y in plates:
        ax.add_patch(plt.Rectangle((x, y), PLATE_WIDTH, wall_height, color='lightgray', edgecolor='black'))
    for x, y in sargels:
        ax.add_patch(plt.Rectangle((x, y), SARGEL_WIDTH, wall_height, color='dimgray', edgecolor='black'))

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(rtl("הדמיית קיר"), fontsize=14)
    ax.text(wall_width / 2, -10, rtl(f"רוחב: {wall_width} ס\"מ"), ha='center', fontsize=12)
    ax.text(-10, wall_height / 2, rtl(f"גובה: {wall_height} ס\"מ"), va='center', fontsize=12, rotation=90)
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
    c.drawRightString(width - 50, height - 100, rtl(f"כמות פלטות: {num_plates}"))
    c.drawRightString(width - 50, height - 120, rtl(f"כמות סרגלים: {num_sargels}"))
    c.drawRightString(width - 50, height - 140, rtl("הסבר התקנה: יש להתחיל בהצמדת הפלטות מהקצה הימני של הקיר ולסיים בהצמדת הסרגלים בהתאם למיקום שנבחר. יש לוודא יישור מלא לפני קיבוע סופי."))

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, bbox_inches='tight')
            c.drawImage(ImageReader(tmpfile.name), 50, height - 520, width=500, preserveAspectRatio=True)
        os.unlink(tmpfile.name)
    except Exception as e:
        c.drawRightString(width - 50, height - 180, rtl(f"שגיאה ביצירת תמונה: {str(e)}"))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
