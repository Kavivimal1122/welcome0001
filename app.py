import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# =========================================================
# 📂 DATA REPOSITORY: ALL YOUR PATTERNS INTEGRATED
# =========================================================

# Model 1: Exact matches (100% Accuracy)
EXACT_PATTERNS = {
    "SSSBSBSBBS": "B",
    "SSBBSBSSBBB": "S",
    "GGRRRGRRRRRG": "G",
    "BRBRBRBGSGSR": "BG",
    "9955": "6",
    "BRSRBGBGSRSRSG": "BG",
    "SGBGSGBRBRBGSGSR": "SG"
}

# Model 2: Structural matches (Shape logic)
STRUCTURAL_PATTERNS = {
    "011010000011": "R", # Col 2
    "011111101111": "B", # Col 1
    "000001100101": "R", # Col 2
    "010000100000": "R"  # Col 2
}

# Model 3: Cycle matches (Repeating sequences)
CYCLE_PATTERNS = {
    "GGGRRGGGGG": ["G", "G", "G", "G", "G", "G", "R", "R"],
    "GRRRGGGGRR": ["R", "R", "G", "G", "G", "G", "G", "G"],
    "GRRGGGRRRR": ["R", "G", "G", "G", "R", "G", "R"],
    "BBBSBSSSBBS": ["B", "B", "B", "B", "B", "S"],
    "SBSSSBBBSS": ["B", "B", "S", "B", "S", "B", "B"],
    "RGRGRGGGRG": ["R", "R", "G", "R", "G", "G"]
}

# =========================================================
# ⚙️ ENGINE LOGIC
# =========================================================

class GameEngine:
    def __init__(self):
        # Keeps track of how many times a specific pattern has occurred to handle cycles
        if 'occurrences' not in st.session_state:
            st.session_state.occurrences = Counter()

    def get_relative_structure(self, seq):
        """Converts any sequence into Model 2 numeric format (e.g. SR -> 01)"""
        mapping = {}
        return "".join([mapping.setdefault(char, str(len(mapping))) for char in seq])

    def engine_1_tracker(self, history):
        """Checks Exact Patterns and Cycle Patterns"""
        for length in [12, 11, 10, 8, 7, 6, 4]: # Search from longest to shortest
            if len(history) < length: continue
            
            # 1. Check Exact Matches
            curr_chunk = "".join(history[-length:])
            if curr_chunk in EXACT_PATTERNS:
                return EXACT_PATTERNS[curr_chunk], "Engine 1 (Deterministic)"

            # 2. Check Cycle Matches
            if curr_chunk in CYCLE_PATTERNS:
                cycle = CYCLE_PATTERNS[curr_chunk]
                count = st.session_state.occurrences[curr_chunk]
                prediction = cycle[count % len(cycle)]
                return prediction, f"Engine 1 (Cycle Pos: {count % len(cycle)})"
        
        return None, None

    def engine_2_subber_ai(self, history):
        """Checks Structural Patterns (Model 2)"""
        for length in [12]: # Your Model 2 patterns are all length 12
            if len(history) < length: continue
            
            curr_struct = self.get_relative_structure(history[-length:])
            if curr_struct in STRUCTURAL_PATTERNS:
                return STRUCTURAL_PATTERNS[curr_struct], "Engine 2 (Subber AI Structure)"
        
        return None, None

# =========================================================
# 📱 STREAMLIT UI
# =========================================================

st.set_page_config(page_title="2-Engg Pattern AI", layout="wide")
st.title("🛡️ Dual-Engine Pattern Track & Prediction")

# Initialize Session State
if 'live_history' not in st.session_state: st.session_state.live_history = []
if 'streak_log' not in st.session_state: st.session_state.streak_log = []

eng = GameEngine()

# Input Section
st.subheader("Input Live Results")
col1, col2, col3, col4 = st.columns(4)

def handle_input(val):
    # Get predictions BEFORE adding new input
    p1, m1 = eng.engine_1_tracker(st.session_state.live_history)
    p2, m2 = eng.engine_2_subber_ai(st.session_state.live_history)

    # If it was a cycle pattern, update its occurrence count
    for length in [10, 11]:
        if len(st.session_state.live_history) >= length:
            chunk = "".join(st.session_state.live_history[-length:])
            if chunk in CYCLE_PATTERNS:
                st.session_state.occurrences[chunk] += 1

    # Log the result
    st.session_state.streak_log.append({
        "Time": datetime.datetime.now().strftime("%H:%M:%S"),
        "Entered": val,
        "Eng1_Pred": p1 if p1 else "-",
        "Eng2_Pred": p2 if p2 else "-",
        "Status": "✅" if (p1 == val or p2 == val) else "❌" if (p1 or p2) else "-"
    })
    st.session_state.live_history.append(val)

if col1.button("SR (Small Red)", use_container_width=True): handle_input("SR")
if col2.button("SG (Small Green)", use_container_width=True): handle_input("SG")
if col3.button("BR (Big Red)", use_container_width=True): handle_input("BR")
if col4.button("BG (Big Green)", use_container_width=True): handle_input("BG")

# Predictions Dashboard
st.divider()
next_p1, msg1 = eng.engine_1_tracker(st.session_state.live_history)
next_p2, msg2 = eng.engine_2_subber_ai(st.session_state.live_history)

res1, res2 = st.columns(2)
with res1:
    st.metric("Engine 1 Prediction", str(next_p1) if next_p1 else "Searching...")
    st.caption(msg1 if msg1 else "Waiting for pattern match...")

with res2:
    st.metric("Engine 2 Prediction", str(next_p2) if next_p2 else "Analyzing...")
    st.caption(msg2 if msg2 else "Analyzing structural shape...")

# History Table
st.subheader("📊 Tracking Log")
if st.session_state.streak_log:
    df = pd.DataFrame(st.session_state.streak_log).iloc[::-1]
    st.table(df)
    
    csv = pd.DataFrame(st.session_state.streak_log).to_csv(index=False)
    st.download_button("📥 Download Results", csv, "streak_tracking.csv", "text/csv")

if st.button("Reset Session"):
    st.session_state.live_history = []
    st.session_state.streak_log = []
    st.session_state.occurrences = Counter()
    st.rerun()