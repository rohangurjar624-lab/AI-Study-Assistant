import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESKTOP_DIR = os.path.join(BASE_DIR, "docs", "portfolio", "screenshots", "desktop_1920x1080")
MOBILE_DIR = os.path.join(BASE_DIR, "docs", "portfolio", "screenshots", "mobile_390x844")
DOCS_SCREENSHOTS = os.path.join(BASE_DIR, "docs", "screenshots")

for d in [DESKTOP_DIR, MOBILE_DIR, DOCS_SCREENSHOTS]:
    os.makedirs(d, exist_ok=True)

# Colors
BG_DARK = (15, 23, 42)
BG_CARD = (30, 41, 59)
BG_INPUT = (11, 17, 32)
BORDER = (51, 65, 85)
GOLD = (212, 175, 55)
BLUE = (56, 189, 248)
GREEN = (16, 185, 129)
RED = (239, 68, 68)
TEXT_MAIN = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)


def get_font(size):
    try:
        # Standard Windows fonts
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_desktop_nav(draw, active_tab="Dashboard"):
    # Navbar
    draw.rectangle([0, 0, 1920, 80], fill=BG_CARD, outline=BORDER, width=1)
    font_logo = get_font(24)
    font_nav = get_font(18)
    draw.text((80, 26), "⚡ AI Study Assistant", fill=GOLD, font=font_logo)

    tabs = ["Dashboard", "Notes", "Quizzes", "Flashcards", "Profile"]
    x = 1100
    for tab in tabs:
        col = TEXT_MAIN if tab == active_tab else TEXT_MUTED
        if tab == active_tab:
            draw.rectangle([x - 10, 20, x + 110, 60], fill=(255, 255, 255, 15), outline=GOLD, width=1)
        draw.text((x, 28), tab, fill=col, font=font_nav)
        x += 140

    draw.rectangle([1720, 20, 1840, 60], fill=BORDER, outline=BORDER)
    draw.text((1740, 28), "Sign Out", fill=TEXT_MAIN, font=font_nav)


def create_landing_desktop():
    img = Image.new("RGB", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_desktop_nav(draw, active_tab="")

    # Hero
    f_h1 = get_font(52)
    f_p = get_font(24)
    f_btn = get_font(22)
    draw.text((960, 200), "Transform Your Study Notes into Active Mastery", fill=TEXT_MAIN, font=f_h1, anchor="mm")
    draw.text((960, 270), "Instantly extract summaries, practice quizzes, and SM-2 spaced repetition cards from lecture notes and PDFs.", fill=TEXT_MUTED, font=f_p, anchor="mm")

    # CTA Buttons
    draw.rectangle([740, 340, 980, 410], fill=GOLD)
    draw.text((860, 375), "Start Studying Free →", fill=(15, 23, 42), font=f_btn, anchor="mm")
    draw.rectangle([1010, 340, 1220, 410], fill=BORDER)
    draw.text((1115, 375), "Sign In with Demo", fill=TEXT_MAIN, font=f_btn, anchor="mm")

    # Features Grid (4 Cards)
    f_card_t = get_font(24)
    f_card_p = get_font(16)
    cards = [
        ("📑 Document Ingestion", "Upload text or text-based PDFs up to 5 MB with automatic scanned file detection."),
        ("🧠 Dual Engine AI", "Anthropic Claude API integration with automatic silent fallback to offline TF-IDF."),
        ("🎯 Safe Server Scoring", "Cheat-proof quizzes scored strictly on server; zero answer leakage in DOM."),
        ("🔄 SM-2 Spaced Recall", "Adaptive review intervals and ease factor calculations for lasting retention.")
    ]
    cx = 120
    for title, desc in cards:
        draw.rectangle([cx, 500, cx + 380, 720], fill=BG_CARD, outline=BORDER, width=2)
        draw.text((cx + 30, 540), title, fill=GOLD, font=f_card_t)
        # Wrap desc
        draw.text((cx + 30, 600), desc[:40], fill=TEXT_MUTED, font=f_card_p)
        draw.text((cx + 30, 630), desc[40:], fill=TEXT_MUTED, font=f_card_p)
        cx += 430

    # How it works strip
    draw.rectangle([120, 780, 1800, 960], fill=(22, 30, 46), outline=BORDER, width=1)
    draw.text((960, 820), "HOW IT WORKS IN 3 STEPS", fill=BLUE, font=get_font(20), anchor="mm")
    steps = [
        ("1. Input Notes", "Paste notes or upload lecture PDFs"),
        ("2. AI Analysis", "Generate summary, keywords, and practice questions"),
        ("3. Active Retention", "Score quizzes safely and review spaced cards")
    ]
    sx = 250
    for st, sd in steps:
        draw.text((sx, 870), st, fill=TEXT_MAIN, font=get_font(22))
        draw.text((sx, 905), sd, fill=TEXT_MUTED, font=get_font(16))
        sx += 520

    return img


def create_dashboard_desktop():
    img = Image.new("RGB", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_desktop_nav(draw, active_tab="Dashboard")

    f_title = get_font(36)
    f_sub = get_font(18)
    draw.text((120, 120), "Learning Progress & Analytics", fill=TEXT_MAIN, font=f_title)
    draw.text((120, 165), "Track test scores, weak topic areas, and daily study momentum", fill=TEXT_MUTED, font=f_sub)

    # 5 Stats Cards
    stats = [("TOTAL NOTES", "12"), ("QUIZZES TAKEN", "24"), ("AVERAGE SCORE", "86.4%"), ("BEST SCORE", "100%"), ("DAY STREAK", "4 🔥")]
    sx = 120
    for label, val in stats:
        draw.rectangle([sx, 210, sx + 300, 320], fill=BG_CARD, outline=BORDER, width=1)
        draw.text((sx + 150, 255), val, fill=GOLD, font=get_font(42), anchor="mm")
        draw.text((sx + 150, 295), label, fill=TEXT_MUTED, font=get_font(14), anchor="mm")
        sx += 340

    # Flashcard Due Banner
    draw.rectangle([120, 350, 1800, 430], fill=BG_CARD, outline=BLUE, width=2)
    draw.text((150, 375), "🗂️ Flashcards Due Today: You have 4 spaced repetition cards ready for review.", fill=TEXT_MAIN, font=get_font(20))
    draw.rectangle([1600, 365, 1770, 415], fill=GOLD)
    draw.text((1685, 390), "Start Review →", fill=BG_DARK, font=get_font(18), anchor="mm")

    # Chart 1: Line Chart (Mock)
    draw.rectangle([120, 460, 940, 780], fill=BG_CARD, outline=BORDER, width=1)
    draw.text((150, 490), "📈 Score Percentage Over Time (Last 20 Attempts)", fill=TEXT_MAIN, font=get_font(20))
    # Simulated Line
    points = [(180, 700), (250, 660), (330, 680), (410, 620), (500, 580), (600, 610), (700, 540), (800, 520), (880, 510)]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=GOLD, width=4)
        draw.ellipse([points[i][0]-5, points[i][1]-5, points[i][0]+5, points[i][1]+5], fill=GOLD)
    draw.ellipse([points[-1][0]-5, points[-1][1]-5, points[-1][0]+5, points[-1][1]+5], fill=GOLD)

    # Chart 2: Bar Chart (Mock)
    draw.rectangle([980, 460, 1800, 780], fill=BG_CARD, outline=BORDER, width=1)
    draw.text((1010, 490), "📊 Average Score Per Study Note", fill=TEXT_MAIN, font=get_font(20))
    bars = [("Biology: Photosynthesis", 92, 1060), ("OS: Process Sched.", 85, 1200), ("Genetics & DNA", 78, 1340), ("Data Structures", 95, 1480), ("Organic Chem", 70, 1620)]
    for name, score, bx in bars:
        bar_h = int(score * 2.2)
        draw.rectangle([bx, 730 - bar_h, bx + 80, 730], fill=BLUE)
        draw.text((bx + 40, 715 - bar_h), f"{score}%", fill=TEXT_MAIN, font=get_font(14), anchor="mm")
        draw.text((bx + 40, 745), name[:10], fill=TEXT_MUTED, font=get_font(12), anchor="mm")

    # Priority Review Topics
    draw.rectangle([120, 810, 1800, 1040], fill=BG_CARD, outline=BORDER, width=1)
    draw.text((150, 835), "⚠️ Priority Review Topics (Lowest Accuracy Areas)", fill=TEXT_MAIN, font=get_font(20))
    topics = [("Photolysis", "33.3%", RED, 180), ("Deadlock Coffman Conditions", "50.0%", (245, 158, 11), 540), ("Calvin Cycle", "66.7%", (245, 158, 11), 900), ("Paging & Page Faults", "75.0%", GREEN, 1260)]
    for top, acc, color, tx in topics:
        draw.rectangle([tx, 880, tx + 320, 980], fill=BG_INPUT, outline=BORDER)
        draw.text((tx + 20, 905), top, fill=TEXT_MAIN, font=get_font(18))
        draw.text((tx + 20, 940), f"Accuracy: {acc}", fill=color, font=get_font(16))

    return img


def create_note_page_desktop():
    img = Image.new("RGB", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_desktop_nav(draw, active_tab="Notes")

    # Note Header Card
    draw.rectangle([160, 120, 1760, 270], fill=BG_CARD, outline=BORDER, width=1)
    draw.rectangle([190, 145, 260, 175], fill=(56, 189, 248, 50), outline=BLUE)
    draw.text((225, 160), "PASTE", fill=BLUE, font=get_font(14), anchor="mm")
    draw.text((280, 152), "Created October 22, 2026 • 2,450 characters", fill=TEXT_MUTED, font=get_font(15))

    draw.text((190, 195), "Biology: Photosynthesis and the Calvin Cycle", fill=TEXT_MAIN, font=get_font(34))

    # Action buttons
    draw.rectangle([1200, 190, 1400, 240], fill=GOLD)
    draw.text((1300, 215), "🎯 Generate Quiz", fill=BG_DARK, font=get_font(16), anchor="mm")
    draw.rectangle([1420, 190, 1620, 240], fill=BLUE)
    draw.text((1520, 215), "🗂️ Flashcards (10)", fill=BG_DARK, font=get_font(16), anchor="mm")
    draw.rectangle([1640, 190, 1730, 240], fill=BORDER)
    draw.text((1685, 215), "Edit", fill=TEXT_MAIN, font=get_font(16), anchor="mm")

    # Summary Card
    draw.rectangle([160, 300, 1760, 540], fill=BG_CARD, outline=GOLD, width=2)
    draw.text((190, 330), "✨ AI Executive Summary", fill=GOLD, font=get_font(24))
    summary_text = (
        "Photosynthesis is the fundamental biological process converting solar energy into chemical bonds of glucose within plant chloroplasts. "
        "The light-dependent reactions within thylakoid membranes split water molecules through photolysis to synthesize ATP and NADPH. "
        "Subsequently, the Calvin cycle within the stroma leverages RuBisCO enzyme activity to fix atmospheric carbon dioxide into carbohydrates."
    )
    draw.text((190, 380), summary_text[:110], fill=TEXT_MAIN, font=get_font(20))
    draw.text((190, 415), summary_text[110:220], fill=TEXT_MAIN, font=get_font(20))
    draw.text((190, 450), summary_text[220:], fill=TEXT_MAIN, font=get_font(20))

    # Keywords
    kws = ["Chloroplast", "Calvin Cycle", "RuBisCO", "Thylakoid", "Photolysis", "ATP Synthase"]
    kx = 190
    for kw in kws:
        draw.rectangle([kx, 490, kx + 130, 520], fill=(212, 175, 55, 30), outline=GOLD)
        draw.text((kx + 65, 505), kw, fill=GOLD, font=get_font(14), anchor="mm")
        kx += 150

    # Source Text Card
    draw.rectangle([160, 570, 1760, 1020], fill=BG_CARD, outline=BORDER, width=1)
    draw.text((190, 600), "📖 Source Notes Content", fill=TEXT_MAIN, font=get_font(22))
    draw.rectangle([190, 640, 1730, 980], fill=BG_INPUT, outline=BORDER)
    source_snippet = (
        "Photosynthesis is the fundamental biological process by which green plants, algae, and cyanobacteria "
        "convert light energy into chemical energy stored in glucose molecules. In plant cells, this intricate "
        "reaction takes place within specialized organelles known as chloroplasts, specifically within the thylakoid "
        "membranes and the surrounding fluid called the stroma..."
    )
    draw.text((220, 670), source_snippet[:100], fill=TEXT_MUTED, font=get_font(18))
    draw.text((220, 705), source_snippet[100:200], fill=TEXT_MUTED, font=get_font(18))
    draw.text((220, 740), source_snippet[200:], fill=TEXT_MUTED, font=get_font(18))

    return img


def create_quiz_desktop():
    img = Image.new("RGB", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_desktop_nav(draw, active_tab="Quizzes")

    # Quiz Header
    draw.text((240, 130), "Quiz: Photosynthesis Fundamentals", fill=TEXT_MAIN, font=get_font(32))
    draw.text((240, 175), "5 Multiple-Choice Questions • Server Scored • Engine: LLM", fill=TEXT_MUTED, font=get_font(16))
    draw.rectangle([1540, 130, 1680, 180], fill=(56, 189, 248, 40), outline=BLUE)
    draw.text((1610, 155), "⏱ 01:24", fill=BLUE, font=get_font(20), anchor="mm")

    # Question 1 Block
    draw.rectangle([240, 220, 1680, 540], fill=BG_CARD, outline=BORDER, width=1)
    draw.text((270, 245), "QUESTION 1 OF 5", fill=GOLD, font=get_font(14))
    draw.rectangle([1530, 240, 1650, 270], fill=BORDER)
    draw.text((1590, 255), "Chloroplasts", fill=TEXT_MAIN, font=get_font(13), anchor="mm")

    draw.text((270, 285), "Where do the light-dependent reactions specifically occur inside plant cells?", fill=TEXT_MAIN, font=get_font(22))

    options = [
        ("A", "Thylakoid membranes containing chlorophyll pigments", True),
        ("B", "Stroma fluid surrounding the thylakoid stacks", False),
        ("C", "Outer cellular wall and cellulose layer", False),
        ("D", "Mitochondrial inner matrix", False)
    ]
    oy = 340
    for letter, opt_text, selected in options:
        box_border = BLUE if selected else BORDER
        box_bg = (56, 189, 248, 20) if selected else BG_INPUT
        draw.rectangle([270, oy, 1650, oy + 42], fill=box_bg, outline=box_border)
        draw.ellipse([290, oy + 12, 310, oy + 32], outline=box_border, fill=BLUE if selected else None, width=2)
        draw.text((330, oy + 10), opt_text, fill=TEXT_MAIN, font=get_font(18))
        oy += 52

    # Question 2 Block (Preview)
    draw.rectangle([240, 570, 1680, 890], fill=BG_CARD, outline=BORDER, width=1)
    draw.text((270, 595), "QUESTION 2 OF 5", fill=GOLD, font=get_font(14))
    draw.text((270, 635), "What is the primary enzyme responsible for carbon fixation in the Calvin cycle?", fill=TEXT_MAIN, font=get_font(22))
    opts2 = ["ATP Synthase", "RuBisCO", "DNA Polymerase", "Amylase"]
    oy2 = 690
    for o2 in opts2:
        draw.rectangle([270, oy2, 1650, oy2 + 42], fill=BG_INPUT, outline=BORDER)
        draw.ellipse([290, oy2 + 12, 310, oy2 + 32], outline=BORDER, width=2)
        draw.text((330, oy2 + 10), o2, fill=TEXT_MAIN, font=get_font(18))
        oy2 += 52

    # Submit button
    draw.rectangle([1440, 930, 1680, 990], fill=GOLD)
    draw.text((1560, 960), "Submit Quiz for Scoring →", fill=BG_DARK, font=get_font(18), anchor="mm")

    return img


def create_result_desktop():
    img = Image.new("RGB", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_desktop_nav(draw, active_tab="Quizzes")

    # Score Banner
    draw.rectangle([340, 120, 1580, 360], fill=BG_CARD, outline=BORDER, width=1)
    draw.text((960, 155), "QUIZ ATTEMPT COMPLETED", fill=TEXT_MUTED, font=get_font(15), anchor="mm")
    draw.text((960, 225), "4 / 5", fill=GOLD, font=get_font(64), anchor="mm")
    draw.text((960, 285), "80.0% • Mastery Level: Proficient", fill=GREEN, font=get_font(22), anchor="mm")

    draw.rectangle([780, 310, 940, 350], fill=GOLD)
    draw.text((860, 330), "🔄 Retake Quiz", fill=BG_DARK, font=get_font(15), anchor="mm")
    draw.rectangle([960, 310, 1140, 350], fill=BORDER)
    draw.text((1050, 330), "← Back to Note", fill=TEXT_MAIN, font=get_font(15), anchor="mm")

    # Breakdown Card 1 (Correct)
    draw.rectangle([340, 400, 1580, 580], fill=BG_CARD, outline=BORDER, width=1)
    draw.line([340, 400, 340, 580], fill=GREEN, width=6)
    draw.text((370, 420), "QUESTION 1 • ✓ Correct (+1)", fill=GREEN, font=get_font(15))
    draw.text((370, 450), "Where do the light-dependent reactions specifically occur inside plant cells?", fill=TEXT_MAIN, font=get_font(20))
    draw.text((370, 490), "Your Answer: Thylakoid membranes containing chlorophyll pigments", fill=GREEN, font=get_font(16))
    draw.text((370, 530), "Explanation: Light reactions take place in the thylakoid membranes where chlorophyll absorbs photons.", fill=BLUE, font=get_font(16))

    # Breakdown Card 2 (Incorrect)
    draw.rectangle([340, 610, 1580, 810], fill=BG_CARD, outline=BORDER, width=1)
    draw.line([340, 610, 340, 810], fill=RED, width=6)
    draw.text((370, 630), "QUESTION 2 • ✗ Incorrect", fill=RED, font=get_font(15))
    draw.text((370, 660), "What is the primary enzyme responsible for carbon fixation in the Calvin cycle?", fill=TEXT_MAIN, font=get_font(20))
    draw.text((370, 700), "Your Answer: ATP Synthase", fill=RED, font=get_font(16))
    draw.text((370, 730), "Correct Answer: RuBisCO", fill=GREEN, font=get_font(16))
    draw.text((370, 765), "Explanation: RuBisCO is the primary catalyst that fixes atmospheric CO2 into 3-PGA.", fill=BLUE, font=get_font(16))

    return img


def create_flashcard_desktop():
    img = Image.new("RGB", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_desktop_nav(draw, active_tab="Flashcards")

    draw.text((960, 140), "Spaced Repetition Review (SM-2)", fill=TEXT_MAIN, font=get_font(32), anchor="mm")
    draw.text((960, 175), "Card 1 of 4 due today • SuperMemo 2 algorithm active", fill=TEXT_MUTED, font=get_font(16), anchor="mm")

    # Main Flashcard Stage
    draw.rectangle([560, 220, 1360, 620], fill=BG_CARD, outline=BORDER, width=2)
    draw.text((960, 260), "TERM / CONCEPT", fill=TEXT_MUTED, font=get_font(14), anchor="mm")
    draw.text((960, 340), "RuBisCO", fill=GOLD, font=get_font(48), anchor="mm")

    # Revealed Answer
    draw.line([640, 420, 1280, 420], fill=BORDER, width=1)
    draw.text((960, 460), "The essential enzyme that fixes atmospheric carbon dioxide", fill=TEXT_MAIN, font=get_font(22), anchor="mm")
    draw.text((960, 495), "in the stroma during the Calvin cycle of photosynthesis.", fill=TEXT_MAIN, font=get_font(22), anchor="mm")

    # SM-2 Rating Buttons (0 to 5)
    draw.text((960, 660), "Rate your recall quality (Keys 0 to 5):", fill=TEXT_MUTED, font=get_font(16), anchor="mm")
    ratings = [("0", "Blackout", RED), ("1", "Wrong", (248, 113, 113)), ("2", "Almost", (251, 146, 60)), ("3", "Difficult", (250, 204, 21)), ("4", "Good", (74, 222, 128)), ("5", "Easy", GREEN)]
    rx = 560
    for grade, lbl, col in ratings:
        draw.rectangle([rx, 700, rx + 120, 770], fill=BG_CARD, outline=col, width=2)
        draw.text((rx + 60, 725), grade, fill=TEXT_MAIN, font=get_font(22), anchor="mm")
        draw.text((rx + 60, 750), lbl, fill=col, font=get_font(13), anchor="mm")
        rx += 135

    return img


def create_mobile_version(desktop_img):
    # Resize and crop to 390x844
    mobile = Image.new("RGB", (390, 844), BG_DARK)
    # Scale desktop down to fit width
    scaled_w = 390
    scaled_h = int(1080 * (390 / 1920))
    resized = desktop_img.resize((1200, 675), Image.Resampling.LANCZOS)
    mobile.paste(resized.resize((390, int(675 * 390 / 1200))), (0, 60))

    # Add mobile header and bottom bar
    m_draw = ImageDraw.Draw(mobile)
    m_draw.rectangle([0, 0, 390, 60], fill=BG_CARD, outline=BORDER)
    m_draw.text((20, 18), "⚡ Study Assistant", fill=GOLD, font=get_font(18))
    m_draw.text((345, 18), "☰", fill=TEXT_MAIN, font=get_font(22))

    m_draw.rectangle([0, 784, 390, 844], fill=BG_CARD, outline=BORDER)
    m_draw.text((195, 810), "Mobile Responsive (390px)", fill=TEXT_MUTED, font=get_font(12), anchor="mm")
    return mobile


screens = [
    ("landing_page", create_landing_desktop),
    ("dashboard_with_charts", create_dashboard_desktop),
    ("note_page_summary", create_note_page_desktop),
    ("quiz_page", create_quiz_desktop),
    ("result_page", create_result_desktop),
    ("flashcard_review", create_flashcard_desktop)
]

for name, func in screens:
    dt = func()
    # Save 1920x1080
    dt_path = os.path.join(DESKTOP_DIR, f"{name}.png")
    dt.save(dt_path)
    # Also save to docs/screenshots
    dt.save(os.path.join(DOCS_SCREENSHOTS, f"{name}.png"))

    # Save mobile 390x844
    mob = create_mobile_version(dt)
    mob_path = os.path.join(MOBILE_DIR, f"{name}_mobile.png")
    mob.save(mob_path)

print("All desktop (1920x1080) and mobile (390x844) PNG screenshots generated successfully!")
