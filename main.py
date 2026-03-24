# imports
from scoring import mood_scoring
from model import mood_model
from ui import ui_style
import streamlit as st
import random

# config
st.set_page_config(page_title="Office Mood Tracker", page_icon="😀", layout="centered")

# mood scoring system — cached as singletons, constructed once per server process
@st.cache_resource
def get_scoring():
    return mood_scoring()

@st.cache_resource
def get_model():
    return mood_model()

mscoring = get_scoring()
mquotes  = get_model()

# aux functions

@st.cache_data(show_spinner=False)
def cached_compute_wbi(history_key: tuple) -> dict:
    """
    Wraps mscoring.compute_wbi with Streamlit caching.
    history_key is a hashable tuple of (mood, raw_score) pairs — used as cache key.
    """
    history = [{"mood": m, "raw_score": s} for m, s in history_key]
    return mscoring.compute_wbi(history)

def get_wbi_data(history: list) -> dict:
    """Convert history to a hashable key and return cached WBI computation."""
    key = tuple((e["mood"], e["raw_score"]) for e in history)
    return cached_compute_wbi(key)

def get_random_suggestion(mood_key: str) -> str:
    return random.choice(mscoring.moods[mood_key]["suggestions"])

# AI Section starts here...
@st.dialog(" ")
def modal_view():
    wbi_data = get_wbi_data(st.session_state.mood_history)

    upt = mquotes.user_prompt(
            name,
            age,
            mood,
            wbi_data["wbi"],
            mscoring.wbi_label(wbi_data["wbi"]),
            mscoring.compute_raw_mood_score(mood),
            mscoring.moods[mood]["quadrant"],
            mscoring.moods[mood]["pa_load"],
            mscoring.moods[mood]["na_load"],
            wbi_data['instability'],
            wbi_data['decay_valence']
        )

    with st.spinner("Finding the right words for you..."):
        res = mquotes.generate(mquotes.sys_prompt, upt)
    st.markdown(f"""
        <div class="quote-card">
            <div class="quote-section">
                <div class="quote-mark">&ldquo;</div>
                <div class="quote-text">{res['quote']}</div>
                <div class="quote-mark quote-mark-close">&rdquo;</div>
            </div>
            <div class="author-section">
                <div class="author-name">{res['author']}</div>
                <div class="author-meta">{res['years']} &nbsp;&middot;&nbsp; {res['who']}</div>
            </div>
            <div class="context-section">
                <div class="context-label">&#10022; Why this quote</div>
                <div class="context-text">{res['context']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Ends here...

def log_mood(name: str, age: int, mood_key: str) -> None:
    entry = {
        "name":      name,
        "age":       age,
        "mood":      mood_key,
        "emoji":     mscoring.moods[mood_key]["emoji"],
        "raw_score": mscoring.compute_raw_mood_score(mood_key),
        "valence":   mscoring.moods[mood_key]["valence"],
        "arousal":   mscoring.moods[mood_key]["arousal"],
        "pa_load":   mscoring.moods[mood_key]["pa_load"],
        "na_load":   mscoring.moods[mood_key]["na_load"],
        "quadrant":  mscoring.moods[mood_key]["quadrant"],
    }
    st.session_state.mood_history.append(entry)
    st.session_state.last_suggestion  = get_random_suggestion(mood_key)
    st.session_state.last_mood_logged = mood_key


def weekly_summary(history: list) -> dict:
    frequency: dict = {}
    for entry in history:
        frequency[entry["mood"]] = frequency.get(entry["mood"], 0) + 1

    wbi_data = get_wbi_data(history)
    wbi      = wbi_data["wbi"]

    if wbi >= 65:
        verdict, css = "🌟 Very Positive Week", "verdict-positive"
    elif wbi < 35:
        verdict, css = "💙 Needs Emotional Attention", "verdict-negative"
    else:
        verdict, css = "⚖️ Balanced Week", "verdict-balanced"

    return {**wbi_data, "frequency": frequency, "verdict": verdict, "css_class": css}


# App UI
ui_style()

# mood options
MOOD_OPTIONS: list = list(mscoring.moods.keys())

# app states
def _init_state() -> None:
    defaults = {
        "mood_history":       [],
        "last_suggestion":    None,
        "last_mood_logged":   None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

st.markdown("""
<div class="hero-banner">
    <h1>😀 Office Mood Booster</h1>
    <p>The Boost you need to be Productive 👊</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    name = st.text_input("Your name", placeholder="e.g. Forrest Frank")
with col2:
    age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)

mood = st.selectbox("How are you feeling right now?", MOOD_OPTIONS)

# Live circumplex preview
m = mscoring.moods[mood]
v_sign = "+" if m["valence"] >= 0 else ""
a_sign = "+" if m["arousal"] >= 0 else ""
st.markdown(f"""
<div class="dim-row">
  <span class="dim-badge {'dim-valence-pos' if m['valence']>=0 else 'dim-valence-neg'}">
      Valence: {v_sign}{m['valence']}
  </span>
  <span class="dim-badge {'dim-arousal-high' if m['arousal']>=0 else 'dim-arousal-low'}">
      Arousal: {a_sign}{m['arousal']}
  </span>
  <span class="dim-badge dim-pa">PA load: {m['pa_load']}</span>
  <span class="dim-badge dim-na">NA load: {m['na_load']}</span>
  <span class="dim-badge dim-quad">{m['quadrant']}</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Action buttons
col_a, col_b, col_c = st.columns([1, 1.2, 1])
with col_a:
    log_clicked = st.button("✅ Log My Mood", use_container_width=True)
with col_b:
    summary_clicked = st.button("📊 Show Weekly Summary", use_container_width=True)
with col_c:
    motivation_clicked = st.button("💡 Motivational Quote")

if log_clicked:
    if not name.strip():
        st.warning("Please enter your name before logging your mood.")
    else:
        log_mood(name.strip(), age, mood)

# Post-log suggestion + per-entry score
if st.session_state.last_suggestion and st.session_state.last_mood_logged:
    lm   = st.session_state.last_mood_logged
    rs   = mscoring.compute_raw_mood_score(lm)
    sign = "+" if rs >= 0 else ""

    st.markdown(f"""
    <div class="card">
        <div class="card-title">💡 Personalised Suggestion</div>
        <p style="font-size:0.9rem;color:#888;margin:0 0 0.3rem;">
            Logged: <strong>{lm}</strong> &nbsp;|&nbsp;
            Entry score: <strong style="color:#ff7e5f">{sign}{rs}</strong> / 10 &nbsp;|&nbsp;
            Quadrant: <em>{mscoring.moods[lm]['quadrant']}</em>
        </p>
        <div class="suggestion-box">{mscoring.moods[lm]['emoji']} {st.session_state.last_suggestion}</div>
    </div>
    """, unsafe_allow_html=True)

# Live WBI dashboard
with st.sidebar:
    if st.session_state.mood_history:
        wbi_data = get_wbi_data(st.session_state.mood_history)
        wbi      = wbi_data["wbi"]
        colour   = mscoring.wbi_colour(wbi)
        label    = mscoring.wbi_label(wbi)

        st.title("📈 Live Wellbeing Index", text_alignment="center")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:0.5rem;">
            <div class="wbi-ring" style="background:{colour};">{wbi}</div>
            <div style="font-size:1.1rem;font-weight:800;color:#333;">{label}</div>
            <div style="font-size:0.75rem;color:#aaa;margin-top:4px;">
                Wellbeing Index (0-100) &nbsp;·&nbsp; {wbi_data['entry_count']} log{'s' if wbi_data['entry_count']!=1 else ''}
            </div>
        </div>
        <div class="score-grid">
            <div class="score-tile">
                <div class="score-tile-val">{wbi_data['decay_valence']:+.1f}</div>
                <div class="score-tile-lbl">Valence Score</div>
            </div>
            <div class="score-tile">
                <div class="score-tile-val">{wbi_data['pa_na_balance']:+.1f}</div>
                <div class="score-tile-lbl">PA − NA Balance</div>
            </div>
            <div class="score-tile">
                <div class="score-tile-val">{wbi_data['instability']:.1f}</div>
                <div class="score-tile-lbl">Instability σ</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PA / NA progress bars
        pa_pct = int(min(100, wbi_data["pa"] * 10))
        na_pct = int(min(100, wbi_data["na"] * 10))
        st.markdown(f"""
        <div style="margin-top:0.6rem;">
            <div style="font-size:0.72rem;font-weight:800;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">
                Positive Affect &nbsp;·&nbsp; {wbi_data['pa']:.1f}/10
            </div>
            <div style="background:#eee;border-radius:50px;height:10px;overflow:hidden;margin-bottom:8px;">
                <div style="height:100%;width:{pa_pct}%;background:linear-gradient(90deg,#27ae60,#2ecc71);border-radius:50px;"></div>
            </div>
            <div style="font-size:0.72rem;font-weight:800;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">
                Negative Affect &nbsp;·&nbsp; {wbi_data['na']:.1f}/10
            </div>
            <div style="background:#eee;border-radius:50px;height:10px;overflow:hidden;">
                <div style="height:100%;width:{na_pct}%;background:linear-gradient(90deg,#e74c3c,#ff7675);border-radius:50px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box" style="margin-top:0.8rem;">
            <strong>How is this score calculated?</strong><br>
            The Wellbeing Index (WBI) blends three research-backed components:
            (1) <em>Decay-weighted valence</em> — recent moods carry more weight, older moods fade
            (temporal decay model, Nature Communications 2018);
            (2) <em>PA-NA balance</em> — Positive and Negative Affect tracked as independent dimensions
            (PANAS, Watson et al. 1988);
            (3) <em>Mood instability penalty</em> — high volatility between entries reduces the score
            (MSSD metric, PMC 2024). Each mood is mapped on Russell's (1980) Circumplex axes:
            Valence (pleasant-unpleasant) and Arousal (activated-deactivated).
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Mood history pills
st.header("📋 Mood History")
pills = "".join(
    f'<span class="mood-pill">{e["emoji"]} {e["name"]} ({e["raw_score"]:+.0f})</span>'
        for e in reversed(st.session_state.mood_history[-24:])
    )
st.markdown(pills, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)       

# Weekly Summary 
if summary_clicked:
    if not st.session_state.mood_history:
        st.info("No moods logged yet. Log at least one mood first!")
    else:
        s = weekly_summary(st.session_state.mood_history)

        st.header("📊 Weekly Summary")

        rows = ""
        for mk, cnt in s["frequency"].items():
            rs   = mscoring.compute_raw_mood_score(mk)
            quad = mscoring.moods[mk]["quadrant"]
            rows += (
                f"<tr style='border-bottom:1px solid #eee;'>"
                f"<td style='padding:0.4rem 0.7rem;'>{mk}</td>"
                f"<td style='text-align:center;padding:0.4rem 0.7rem;font-weight:700;'>{cnt}</td>"
                f"<td style='text-align:center;padding:0.4rem 0.7rem;color:#ff7e5f;font-weight:700;'>{rs:+.1f}</td>"
                f"<td style='text-align:center;padding:0.4rem 0.7rem;'>{mscoring.moods[mk]['valence']:+.2f}</td>"
                f"<td style='text-align:center;padding:0.4rem 0.7rem;'>{mscoring.moods[mk]['arousal']:+.2f}</td>"
                f"<td style='padding:0.4rem 0.7rem;font-size:0.8rem;color:#666;'>{quad}</td>"
                f"</tr>"
            )

        st.markdown(f"""
        <table style='width:100%;border-collapse:collapse;font-family:Nunito,sans-serif;font-size:0.88rem;'>
          <tr style='background:#f5f0ff;'>
            <th style='text-align:left;padding:0.4rem 0.7rem;'>Mood</th>
            <th style='padding:0.4rem 0.7rem;'>Count</th>
            <th style='padding:0.4rem 0.7rem;'>Entry Score</th>
            <th style='padding:0.4rem 0.7rem;'>Valence</th>
            <th style='padding:0.4rem 0.7rem;'>Arousal</th>
            <th style='text-align:left;padding:0.4rem 0.7rem;'>Quadrant</th>
          </tr>
          {rows}
        </table>
        """, unsafe_allow_html=True)
        
        colour = mscoring.wbi_colour(s["wbi"])
        st.markdown(f"""
        <div style="margin-top:1rem;display:flex;gap:1rem;flex-wrap:wrap;align-items:center;">
            <div class="wbi-ring" style="background:{colour};width:90px;height:90px;font-size:1.6rem;">
                {s['wbi']}
            </div>
            <div>
                <div style="font-size:0.75rem;font-weight:800;color:#888;text-transform:uppercase;letter-spacing:1px;">
                    Wellbeing Index Components
                </div>
                <div style="font-size:0.9rem;font-weight:700;color:#333;line-height:1.9;">
                    Decay-weighted Valence: <strong>{s['decay_valence']:+.2f}</strong><br>
                    Positive Affect (PA): <strong>{s['pa']:.2f}/10</strong>
                    &nbsp;|&nbsp; Negative Affect (NA): <strong>{s['na']:.2f}/10</strong><br>
                    PA-NA Balance: <strong>{s['pa_na_balance']:+.2f}</strong><br>
                    Mood Instability (MSSD): <strong>{s['instability']:.2f}</strong>
                </div>
            </div>
        </div>
        <div class="verdict {s['css_class']}" style="margin-top:0.9rem;">{s['verdict']}</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if motivation_clicked:
    modal_view()

st.markdown("---")
with st.expander("⚙️ Reset all data"):
    if st.button("🗑️ Clear mood history & reset"):
        st.session_state.mood_history     = []
        st.session_state.last_suggestion  = None
        st.session_state.last_mood_logged = None
        st.success("All data cleared. Fresh start! 🌱")
        st.rerun()

st.markdown("""
<p style='text-align:center;color:#ccc;font-size:0.75rem;margin-top:1.5rem;'>
    Scoring based on: Russell (1980) Circumplex Model · PANAS (Watson et al. 1988) ·
    Temporal Decay (Nature Comms 2018) · MSSD Instability (PMC 2024) · HAAS Four-Factor Model (2023)
    <br>Built with 💛 by the Meta People Experience Engineering team · No data stored externally
</p>
""", unsafe_allow_html=True)
