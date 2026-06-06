import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Who Knows Me Better?", page_icon="👀", layout="centered")

# ─── QUESTIONS ──────────────────────────────────────────────────────────────
QUESTIONS = [
    {"q": "If I had to express love using only one of these, I'd choose:", "opts": ["A perfectly made playlist", "Showing up unannounced with food", "Remembering the small things nobody else noticed", "Being there in the boring, ordinary moments"]},
    {"q": "When I'm upset, what do I actually do?", "opts": ["Go completely quiet", "Talk about it immediately", "Pretend everything is fine until it isn't"]},
    {"q": "The situationship I never talk about:", "opts": ["Doesn't exist, I'm an open book", "Exists, they know who they are", "Existed, we don't talk about it", "Is somehow still ongoing and I have no explanation"]},
    {"q": "When I walk into a room full of people I don't know, I am:", "opts": ["Quietly observing until I'm comfortable", "Already introducing myself", "Looking for the one person I know and staying there"]},
    {"q": "If I could live anywhere in the world, I'd choose:", "opts": ["A busy city with energy and noise", "Somewhere quiet, close to nature", "Wherever the people I love are"]},
    {"q": "What's something small and ordinary that secretly makes me deeply happy?", "opts": ["Something in nature — a view, weather, stillness", "Something domestic — food, warmth, familiar sounds", "Both, depends on the day"]},
    {"q": "If I could sit with one emotion I've been avoiding, what would it be?", "opts": ["Grief", "Fear", "Anger", "None, I face my emotions"]},
    {"q": "The thing I do when I like someone but won't admit it:", "opts": ["I become weirdly attentive to everything they say", "I act slightly more unbothered than usual", "I find small excuses to be around them"]},
    {"q": "When making a big decision, I rely on:", "opts": ["My gut, always", "Logic and facts", "Prayer and patience"]},
    {"q": "If I were a time of day, I'd be:", "opts": ["Early morning, before the world wakes up", "Golden hour, warm and a little nostalgic", "Midnight, still and full of thoughts"]},
    {"q": "What do I think about death?", "opts": ["I think about it more than people realise", "I avoid the thought completely", "I've made a kind of peace with it"]},
    {"q": "Buried or cremated?", "opts": ["Buried", "Cremated", "Haven't thought about it honestly"]},
    {"q": "If this person could know one true thing about me I've never said — would I want them to know it?", "opts": ["Yes, some things are better known than carried alone", "No, not yet", "I'm not sure I'm ready for that"]},
    {"q": "Do I think I've ever been truly and completely understood by another person?", "opts": ["Yes, by at least one person", "No, not completely", "Close, but not yet"]},
    {"q": "The version of myself most people see is:", "opts": ["Pretty much the real me", "A curated version, the real one is for very few people", "Somewhere in between"]},
    {"q": "Do I think people can truly change?", "opts": ["Yes, I've seen it", "No, they just get better at managing who they are", "Only if they really want to"]},
    {"q": "When I love someone, I show it by:", "opts": ["Showing up, actions over words always", "Saying it, words matter to me", "Small things, consistently, over time"]},
    {"q": "What's my most irrational fear?", "opts": ["Worms", "Being alone permanently", "Dying without having done something that actually mattered"]},
    {"q": "Is there something I believe about myself I've never said out loud to anyone?", "opts": ["Yes, and I'm not ready to say it yet", "Yes, and I'd say it right now if asked", "No, I'm pretty open about who I am"]},
    {"q": "If I were a weather type, I'd be:", "opts": ["Sunny but with a chance of thunder", "Overcast, calm, unbothered", "A storm that clears into something beautiful"]},
]

TOTAL = len(QUESTIONS)

# ─── GOOGLE SHEETS SETUP ────────────────────────────────────────────────────
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("WhoKnowsMeBetter").sheet1
    return sheet

def save_answers(role, answers):
    sheet = get_sheet()
    row = [role, json.dumps(answers), datetime.now().isoformat()]
    sheet.append_row(row)

def load_answers(role):
    sheet = get_sheet()
    records = sheet.get_all_values()
    for row in reversed(records):
        if row[0] == role:
            return json.loads(row[1])
    return None

def all_roles_complete():
    roles = ["tawo_self", "tawo_guess", "ishe_self", "ishe_guess"]
    return all(load_answers(r) is not None for r in roles)

def calc_score(guess_role, key_role):
    guesses = load_answers(guess_role)
    key = load_answers(key_role)
    if not guesses or not key:
        return 0
    return sum(1 for i in range(TOTAL) if guesses[i] == key[i])

# ─── SESSION STATE ───────────────────────────────────────────────────────────
if "phase" not in st.session_state:
    st.session_state.phase = "landing"
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "role" not in st.session_state:
    st.session_state.role = None

# ─── STYLES ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main { max-width: 600px; margin: auto; }
.big-title { font-size: 28px; font-weight: 600; margin-bottom: 0.25rem; }
.sub { font-size: 15px; color: #777; margin-bottom: 1.5rem; line-height: 1.7; }
.mode-tag { display: inline-block; background: #eef0fd; color: #5a6ad4; padding: 3px 12px; border-radius: 20px; font-size: 12px; margin-bottom: 1rem; }
.q-text { font-size: 18px; font-weight: 500; margin-bottom: 1rem; line-height: 1.55; }
.progress-text { font-size: 13px; color: #aaa; margin-bottom: 0.5rem; }
.score-box { background: #f9f9f7; border-radius: 12px; padding: 1.5rem; text-align: center; border: 1px solid #e5e5e0; margin-bottom: 1rem; }
.score-big { font-size: 52px; font-weight: 600; }
.score-sub { font-size: 14px; color: #888; margin-top: 0.25rem; }
.verdict { font-size: 15px; font-weight: 500; margin-top: 0.75rem; }
.result-hit { background: #edf7f1; border: 1px solid #b8e0c8; border-radius: 8px; padding: 8px 12px; font-size: 13px; color: #1a5c33; margin-bottom: 6px; }
.result-miss { background: #fdf0f0; border: 1px solid #f0c0c0; border-radius: 8px; padding: 8px 12px; font-size: 13px; color: #8b1a1a; margin-bottom: 6px; }
.compare-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; font-size: 15px; }
.winner-box { background: #f9f9f7; border-radius: 12px; padding: 1.25rem; border: 1px solid #e5e5e0; font-size: 15px; line-height: 1.7; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ─── LANDING ────────────────────────────────────────────────────────────────
if st.session_state.phase == "landing":
    st.markdown('<p class="big-title">Who knows me better? 👀</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">20 questions. Two players. One winner. This is not a drill.</p>', unsafe_allow_html=True)

    st.markdown("**How it works:**")
    st.markdown("""
1. **Tawo** answers all 20 questions about herself — then guesses how Ishe would answer.
2. **Ishe** opens the same link, answers about himself — then guesses how Tawo would answer.
3. Scores are calculated automatically. Winner is declared. Debate settled.
    """)

    st.markdown("---")
    st.markdown("**Who are you?**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("I'm Tawo 👩🏾", use_container_width=True):
            st.session_state.role = "tawo"
            st.session_state.phase = "tawo_self"
            st.session_state.current_q = 0
            st.session_state.answers = []
            st.rerun()
    with col2:
        if st.button("I'm Ishe 👨🏾", use_container_width=True):
            st.session_state.role = "ishe"
            st.session_state.phase = "ishe_self"
            st.session_state.current_q = 0
            st.session_state.answers = []
            st.rerun()

    st.markdown("---")
    if st.button("See results 🏆", use_container_width=True):
        st.session_state.phase = "final"
        st.rerun()

# ─── QUIZ PHASE ─────────────────────────────────────────────────────────────
def render_quiz(role_label, mode_text, next_phase, save_role):
    q_idx = st.session_state.current_q
    if q_idx >= TOTAL:
        save_answers(save_role, st.session_state.answers)
        st.session_state.current_q = 0
        st.session_state.answers = []
        st.session_state.phase = next_phase
        st.rerun()
        return

    q = QUESTIONS[q_idx]
    st.markdown(f'<span class="mode-tag">{mode_text}</span>', unsafe_allow_html=True)
    st.markdown(f'<p class="progress-text">Question {q_idx + 1} of {TOTAL}</p>', unsafe_allow_html=True)
    st.progress((q_idx) / TOTAL)
    st.markdown(f'<p class="q-text">{q["q"]}</p>', unsafe_allow_html=True)

    choice = None
    for i, opt in enumerate(q["opts"]):
        label = f"{chr(65+i)} — {opt}"
        if st.button(label, key=f"opt_{q_idx}_{i}", use_container_width=True):
            choice = i

    if choice is not None:
        st.session_state.answers.append(choice)
        st.session_state.current_q += 1
        st.rerun()

if st.session_state.phase == "tawo_self":
    st.markdown('<p class="big-title">Round 1 — Tawo</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Answer each question as yourself, honestly.</p>', unsafe_allow_html=True)
    render_quiz("Tawo", "Answer as yourself", "tawo_transition", "tawo_self")

elif st.session_state.phase == "tawo_transition":
    st.markdown('<p class="big-title">Round 1 done ✓</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Your answers are saved. Now — how well do you know Ishe? Answer the same questions as you think he would.</p>', unsafe_allow_html=True)
    if st.button("Continue to Round 2 →", use_container_width=True):
        st.session_state.phase = "tawo_guess"
        st.session_state.current_q = 0
        st.session_state.answers = []
        st.rerun()

elif st.session_state.phase == "tawo_guess":
    st.markdown('<p class="big-title">Round 2 — Tawo guesses Ishe</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Answer as you think Ishe would answer about himself.</p>', unsafe_allow_html=True)
    render_quiz("Tawo guessing Ishe", "Answer as you think Ishe would", "tawo_done", "tawo_guess")

elif st.session_state.phase == "tawo_done":
    st.markdown('<p class="big-title">Tawo — all done! ✓</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Your answers are saved. Now send the link to Ishe and wait for him to complete his rounds. Come back here to see the results once he\'s done.</p>', unsafe_allow_html=True)
    st.code("Share this link with Ishe on WhatsApp 👇")
    if st.button("Check results 🏆", use_container_width=True):
        st.session_state.phase = "final"
        st.rerun()

elif st.session_state.phase == "ishe_self":
    st.markdown('<p class="big-title">Round 1 — Ishe</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Answer each question as yourself, honestly.</p>', unsafe_allow_html=True)
    render_quiz("Ishe", "Answer as yourself", "ishe_transition", "ishe_self")

elif st.session_state.phase == "ishe_transition":
    st.markdown('<p class="big-title">Round 1 done ✓</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Your answers are saved. Now — how well do you know Tawo? Answer the same questions as you think she would.</p>', unsafe_allow_html=True)
    if st.button("Continue to Round 2 →", use_container_width=True):
        st.session_state.phase = "ishe_guess"
        st.session_state.current_q = 0
        st.session_state.answers = []
        st.rerun()

elif st.session_state.phase == "ishe_guess":
    st.markdown('<p class="big-title">Round 2 — Ishe guesses Tawo</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Answer as you think Tawo would answer about herself.</p>', unsafe_allow_html=True)
    render_quiz("Ishe guessing Tawo", "Answer as you think Tawo would", "ishe_done", "ishe_guess")

elif st.session_state.phase == "ishe_done":
    st.markdown('<p class="big-title">Ishe — all done! ✓</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">All answers are in. Check the final results below.</p>', unsafe_allow_html=True)
    if st.button("See the verdict 🏆", use_container_width=True):
        st.session_state.phase = "final"
        st.rerun()

# ─── FINAL RESULTS ───────────────────────────────────────────────────────────
elif st.session_state.phase == "final":
    st.markdown('<p class="big-title">The verdict 🏆</p>', unsafe_allow_html=True)

    tawo_self = load_answers("tawo_self")
    ishe_self = load_answers("ishe_self")
    tawo_guess = load_answers("tawo_guess")
    ishe_guess = load_answers("ishe_guess")

    if not all([tawo_self, ishe_self, tawo_guess, ishe_guess]):
        st.warning("Not all rounds are complete yet. Both Tawo and Ishe need to finish before results appear.")
        if st.button("← Back"):
            st.session_state.phase = "landing"
            st.rerun()
    else:
        ishe_score = calc_score("ishe_guess", "tawo_self")
        tawo_score = calc_score("tawo_guess", "ishe_self")
        total = TOTAL

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="score-box"><div class="score-big">{ishe_score}/{total}</div><div class="score-sub">Ishe knows Tawo</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="score-box"><div class="score-big">{tawo_score}/{total}</div><div class="score-sub">Tawo knows Ishe</div></div>', unsafe_allow_html=True)

        diff = abs(tawo_score - ishe_score)
        if tawo_score == ishe_score:
            verdict = "It's a tie. You know each other equally well — or equally poorly. Discuss amongst yourselves. 😐"
        elif diff <= 2:
            winner = "Tawo" if tawo_score > ishe_score else "Ishe"
            verdict = f"It's extremely close. {winner} edges it — but neither of you can really claim victory. The debate continues."
        else:
            winner = "Tawo" if tawo_score > ishe_score else "Ishe"
            loser = "Ishe" if winner == "Tawo" else "Tawo"
            verdict = f"{winner} wins. {loser} has some studying to do. The debate is officially settled — for now. 👀"

        st.markdown(f'<div class="winner-box">{verdict}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Question by question — Ishe guessing Tawo:**")
        for i, q in enumerate(QUESTIONS):
            hit = ishe_guess[i] == tawo_self[i]
            css = "result-hit" if hit else "result-miss"
            icon = "✓" if hit else "✗"
            st.markdown(f'<div class="{css}">{icon} {q["q"]}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Question by question — Tawo guessing Ishe:**")
        for i, q in enumerate(QUESTIONS):
            hit = tawo_guess[i] == ishe_self[i]
            css = "result-hit" if hit else "result-miss"
            icon = "✓" if hit else "✗"
            st.markdown(f'<div class="{css}">{icon} {q["q"]}</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("Play again", use_container_width=True):
            st.session_state.phase = "landing"
            st.rerun()
