import streamlit as st
import matplotlib.pyplot as plt

# הגדרות מוצרים
SARGEL_WIDTH = 12  # ס"מ
SARGEL_HEIGHT = 290  # ס"מ
PLATE_WIDTH = 120  # ס"מ
PLATE_HEIGHT = 280  # ס"מ

# ממשק משתמש
st.title("אפליקציית תכנון חיפוי קיר - Welcome Design")
st.subheader("הזן את מידות הקיר בסנטימטרים")

wall_width = st.number_input("רוחב הקיר (ס״מ):", min_value=100, max_value=10000, value=360)
wall_height = st.number_input("גובה הקיר (ס״מ):", min_value=100, max_value=400, value=280)

mode = st.selectbox("בחר סוג תכנון:", ["שילוב סרגלים + פלטות", "רק פלטות", "רק סרגלים"])

# פונקציית ציור
def draw_wall(wall_width, wall_height, mode):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    x = 0

    plate_color = "#D9E4DD"
    sargel_color = "#BFA6A0"

    while x < wall_width:
        if mode == "שילוב סרגלים + פלטות":
            if wall_width - x >= PLATE_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), PLATE_WIDTH, wall_height, edgecolor='black', facecolor=plate_color))
                x += PLATE_WIDTH
                if wall_width - x >= SARGEL_WIDTH:
                    ax.add_patch(plt.Rectangle((x, 0), SARGEL_WIDTH, wall_height, edgecolor='black', facecolor=sargel_color))
                    x += SARGEL_WIDTH
                else:
                    break
            else:
                ax.add_patch(plt.Rectangle((x, 0), wall_width - x, wall_height, edgecolor='black', facecolor=plate_color))
                break
        elif mode == "רק פלטות":
            if wall_width - x >= PLATE_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), PLATE_WIDTH, wall_height, edgecolor='black', facecolor=plate_color))
                x += PLATE_WIDTH
            else:
                ax.add_patch(plt.Rectangle((x, 0), wall_width - x, wall_height, edgecolor='black', facecolor=plate_color))
                break
        elif mode == "רק סרגלים":
            if wall_width - x >= SARGEL_WIDTH:
                ax.add_patch(plt.Rectangle((x, 0), SARGEL_WIDTH, wall_height, edgecolor='black', facecolor=sargel_color))
                x += SARGEL_WIDTH
            else:
                ax.add_patch(plt.Rectangle((x, 0), wall_width - x, wall_height, edgecolor='black', facecolor=sargel_color))
                break

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("הדמיית חיפוי לקיר ברוחב {} ס״מ ובגובה {} ס״מ".format(wall_width, wall_height))
    st.pyplot(fig)

# הצגת ההדמיה
draw_wall(wall_width, wall_height, mode)
