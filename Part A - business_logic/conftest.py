import sys
import os


_ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if os.path.abspath(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, os.path.abspath(_ROOT_DIR))

# --- קיים מקודם: שימוש לחיבור בין GameSession ל-GUI ---
# (נשאר כמו שהיה, לא נגעתי בו)
sys.path.append(os.path.abspath("Part A - bussines_logic"))

# --- חדש: מבטיח של-pytest תמיד ימצא את המודולים של Part A
# (engine, model, api, events...) לא משנה מאיפה מריצים pytest,
# ולא משנה כמה עמוק טסט מסוים מקונן בתוך tests/ ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))