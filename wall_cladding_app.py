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
import arabic_reshaper
from bidi.algorithm import get_display

# הרשמת גופן תומך עברית
pdfmetrics.registerFont(TTFont('David', 'DavidLibre-Medium.ttf'))

def rtl(text):
    return get_display(arabic_reshaper.reshape(text))

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
    c.drawRightString(width - 50, height - 50, rtl("דו""ח חיפוי קיר"))
    c.setFont("David", 12)
    c.drawRightString(width - 50, height - 80, rtl(f"תאריך: {datetime.now().strftime('%d/%m/%Y')}"))
    c.drawRightString(width - 50, height - 110, rtl(f"מידות קיר: {wall_width}x{wall_height} ס""מ"))
    c.drawRightString(width - 50, height - 140, rtl(f"פלטות: {num_plates}"))
    c.drawRightString(width - 50, height - 170, rtl(f"סרגלים: {num_sargels}"))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        img = ImageReader(tmpfile.name)
        c.drawImage(img, 50, 250, width=500, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# (שאר הקוד נשאר זהה...)
