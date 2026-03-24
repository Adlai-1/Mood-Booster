# imports
import math

class mood_scoring:
    def __init__(self) -> None:
        self.moods: dict = {
            "😊 Happy": {
                "emoji": "😊",
                "valence":  0.85,
                "arousal":  0.55,
                "pa_load":  0.90,
                "na_load":  0.05,
                "quadrant": "High Arousal / Positive Valence",
                "suggestions": [
                    "Share your positive energy — send a quick appreciation note to a teammate right now.",
                    "This is peak performance state. Schedule your hardest task for the next 90 minutes.",
                    "Celebrate the small wins: step out for a nice coffee and savour the moment fully.",
                    "Channel your energy into mentoring a junior colleague — happiness compounds when shared.",
                    "Host an impromptu team stand-up and spread the good mood intentionally.",
                ],
            },
            "😌 Calm": {
                "emoji": "😌",
                "valence":  0.70,
                "arousal": -0.40,
                "pa_load":  0.75,
                "na_load":  0.05,
                "quadrant": "Low Arousal / Positive Valence",
                "suggestions": [
                    "You're in deep-focus territory. Tackle complex, analytical work right now.",
                    "Use this calm clarity for important decision-making — your judgment is at its sharpest.",
                    "A great time to document or write; calm states produce clear, structured thinking.",
                    "Practise a 5-minute mindfulness session to anchor this positive calm state.",
                    "Reach out for a meaningful 1:1 conversation — calm energy makes you a great listener.",
                ],
            },
            "😔 Sad": {
                "emoji": "😔",
                "valence": -0.65,
                "arousal": -0.50,
                "pa_load":  0.10,
                "na_load":  0.75,
                "quadrant": "Low Arousal / Negative Valence",
                "suggestions": [
                    "Take a 5-minute walk outside — even brief movement shifts low-arousal negative states.",
                    "Reach out to a trusted colleague for a warm, non-work chat.",
                    "Write down 3 things — however small — that went okay today.",
                    "Put on an uplifting playlist; research shows music can increase both valence and arousal.",
                    "Give yourself permission to take a screen break and gently reset.",
                ],
            },
            "😡 Angry": {
                "emoji": "😡",
                "valence": -0.80,
                "arousal":  0.80,
                "pa_load":  0.05,
                "na_load":  0.95,
                "quadrant": "High Arousal / Negative Valence",
                "suggestions": [
                    "Step away from the desk immediately — 5 minutes breaks the high-arousal anger loop.",
                    "Write frustrations in a private note, then close it. Externalising defuses intensity.",
                    "Do box breathing: 4 counts in, hold 4, out 6, hold 2. Repeat 4 times.",
                    "Identify the root cause calmly once arousal drops — problem-solving beats venting.",
                    "Drink a full glass of cold water; hydration physically helps regulate arousal states.",
                ],
            },
            "😩 Stressed": {
                "emoji": "😩",
                "valence": -0.70,
                "arousal":  0.65,
                "pa_load":  0.10,
                "na_load":  0.85,
                "quadrant": "High Arousal / Negative Valence",
                "suggestions": [
                    "Write a quick 3-item priority list — seeing tasks on paper reduces cognitive load.",
                    "Try Pomodoro: 25 min focused work, 5 min break. Reduces perceived overwhelm.",
                    "Do a desk stretch: neck rolls, shoulder shrugs, wrist circles — reduces cortisol.",
                    "Communicate workload concerns with your manager early — don't absorb it silently.",
                    "Close unnecessary tabs and apps to declutter your cognitive workspace.",
                ],
            },
            "😴 Tired": {
                "emoji": "😴",
                "valence": -0.30,
                "arousal": -0.80,
                "pa_load":  0.20,
                "na_load":  0.40,
                "quadrant": "Low Arousal / Negative Valence",
                "suggestions": [
                    "A 10-20 min power nap (if possible) restores alertness more than caffeine.",
                    "Swap the next coffee for water — dehydration is a leading cause of fatigue.",
                    "Walk to refill your bottle — gentle movement raises low arousal states.",
                    "Try a 2-minute energising desk stretch sequence to shift arousal upward.",
                    "Reschedule non-critical tasks to tomorrow's peak-energy window.",
                ],
            },
            "😰 Anxious": {
                "emoji": "😰",
                "valence": -0.65,
                "arousal":  0.75,
                "pa_load":  0.05,
                "na_load":  0.90,
                "quadrant": "High Arousal / Negative Valence",
                "suggestions": [
                    "Name what you are anxious about specifically — vagueness amplifies anxiety.",
                    "5-4-3-2-1 grounding: name 5 things you see, 4 you hear, 3 you feel, 2 you smell, 1 taste.",
                    "Slow exhale breathing: breathe out longer than you breathe in to activate the vagus nerve.",
                    "Break the next hour into one concrete 10-minute task — small action reduces anxiety.",
                    "Talk to someone you trust — anxiety loses power when shared out loud.",
                ],
            },
            "😐 Neutral": {
                "emoji": "😐",
                "valence":  0.05,
                "arousal": -0.10,
                "pa_load":  0.40,
                "na_load":  0.20,
                "quadrant": "Low Arousal / Near-Neutral",
                "suggestions": [
                    "Neutral is a clean slate — try starting one small task you have been postponing.",
                    "A short walk or change of scenery can nudge valence upward from neutral.",
                    "Check in with a colleague — social interaction tends to shift neutral states positively.",
                    "Put on a curated focus playlist; ambient sound nudges arousal just enough to engage.",
                    "Review your priorities for the rest of the day — neutral is a great planning state.",
                ],
            },
        }
        self.DECAY_RATE = 0.85 # lambda — exponential decay per entry (older entries lose weight)
        self.STABILITY_W = 0.20 # weight of stability bonus/penalty in final WBI
        pass

    def compute_raw_mood_score(self, mood_key: str) -> float:
        """
        Per-entry score using the Russell Circumplex Model (valence x arousal).

        Quadrant-specific arousal modifier (HAAS four-factor logic):
        Q1  High Arousal Positive  -> boosts score (excitement/happiness)
        Q2  Low Arousal Positive   -> mild boost (calm is healthy, not penalised)
        Q3  High Arousal Negative  -> amplifies penalty (angry/anxious = worst)
        Q4  Low Arousal Negative   -> softened penalty (sad is less acute than angry)

        Result mapped to -10 ... +10 scale.
        """
        m = self.moods[mood_key]
        v = m["valence"]
        a = m["arousal"]

        if v >= 0 and a >= 0:
            arousal_modifier = 0.30 * a
        elif v >= 0 and a < 0:
            arousal_modifier = 0.10 * abs(a)
        elif v < 0 and a >= 0:
            arousal_modifier = -0.50 * a
        else:
            arousal_modifier = 0.15 * abs(a)

        raw = v * 10 + arousal_modifier * 10
        return round(raw, 2)

    def compute_pa_na_scores(self, history: list) -> dict:
        """
        Independent Positive Affect (PA) and Negative Affect (NA) scores,
        decay-weighted to honour PANAS independence principle (Watson et al. 1988).
        Returns: pa (0-10), na (0-10), pa_na_balance (-10...+10).
        """
        if not history:
            return {"pa": 0.0, "na": 0.0, "pa_na_balance": 0.0}

        n = len(history)
        total_w = pa_sum = na_sum = 0.0

        for i, entry in enumerate(history):
            age = n - 1 - i
            weight = self.DECAY_RATE ** age
            total_w += weight
            pa_sum  += weight * self.moods[entry["mood"]]["pa_load"]
            na_sum  += weight * self.moods[entry["mood"]]["na_load"]

        pa      = (pa_sum / total_w) * 10
        na      = (na_sum / total_w) * 10
        balance = pa - na
        return {"pa": round(pa, 2), "na": round(na, 2), "pa_na_balance": round(balance, 2)}

    def compute_decay_weighted_valence(self, history: list) -> float:
        """
        Exponential-decay weighted mean of raw entry scores.
        Implements the temporal decay model: recent moods carry more weight.
        (Eldar et al. / Nature Communications 2018)
        Returns value on -10 ... +10 scale.
        """
        if not history:
            return 0.0
        n = len(history)
        total_w = val_sum = 0.0
        for i, entry in enumerate(history):
            age = n - 1 - i
            w = self.DECAY_RATE ** age
            total_w += w
            val_sum += w * entry["raw_score"]
        return round(val_sum / total_w, 2)

    def compute_mood_instability(self, history: list) -> float:
        """
        Mood Instability = Mean Square of Successive Differences (MSSD) of raw scores.
        Higher MSSD = more volatile mood = wellbeing penalty.
        Based on: PMC 11545575 — MSSD as the gold-standard instability metric.
        Returns normalised instability score 0-10 (0 = perfectly stable).
        """
        if len(history) < 2:
            return 0.0
        scores = [e["raw_score"] for e in history]
        mssd = sum((scores[i+1] - scores[i])**2 for i in range(len(scores)-1)) / (len(scores)-1)
        normalised = min(10.0, math.sqrt(mssd) / 2.0)
        return round(normalised, 2)


    def compute_wbi(self, history: list) -> dict:
        """
        Wellbeing Index (WBI) — composite score 0-100.

        WBI = clip(
                valence_component * 0.65
            + pa_na_component   * 0.20
            - instability       * 0.20,
            0, 100
            ) * 10

        Components:
        valence_component  : decay-weighted valence mapped 0-10
        pa_na_component    : PA-NA balance mapped 0-10
        instability        : MSSD volatility 0-10 (subtracted as penalty)
        """
        if not history:
            return {
                "wbi": 50, "valence_component": 0, "instability": 0,
                "pa": 0, "na": 0, "pa_na_balance": 0,
                "decay_valence": 0, "entry_count": 0,
            }

        decay_v  = self.compute_decay_weighted_valence(history)
        pa_na    = self.compute_pa_na_scores(history)
        instab   = self.compute_mood_instability(history)

        v_comp       = (decay_v + 10) / 2.0
        balance_comp = (pa_na["pa_na_balance"] + 10) / 2.0

        composite = (
            v_comp       * 0.65
        + balance_comp * 0.20
        - instab       * self.STABILITY_W
        )

        wbi = max(0, min(100, composite * 10))

        return {
            "wbi":               round(wbi, 1),
            "valence_component": round(v_comp, 2),
            "pa":                pa_na["pa"],
            "na":                pa_na["na"],
            "pa_na_balance":     pa_na["pa_na_balance"],
            "instability":       instab,
            "decay_valence":     decay_v,
            "entry_count":       len(history),
        }
    
    def wbi_colour(self, wbi: float) -> str:
        if wbi >= 65:
            return "linear-gradient(135deg,#27ae60,#2ecc71)"
        if wbi >= 40:
            return "linear-gradient(135deg,#f39c12,#f1c40f)"
        return "linear-gradient(135deg,#e74c3c,#c0392b)"

    def wbi_label(self, wbi: float) -> str:
        if wbi >= 80: return "🌟 Thriving"
        if wbi >= 65: return "😊 Doing Well"
        if wbi >= 50: return "⚖️ Balanced"
        if wbi >= 35: return "⚠️ Needs Care"
        return "💙 Seek Support"