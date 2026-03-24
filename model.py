import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class mood_model:
    def __init__(self):
        self.ap_key = ''
        self.llm = ChatGroq(model="openai/gpt-oss-120b", temperature=1, ap_key=self.api)
        
        self.sys_prompt = """You are a scholar of human wisdom and an expert curator of historically significant quotations. 
            Your role is to select a single, real, verifiable quote from a prominent historical figure — a philosopher, scientist, statesperson, artist, athlete, author, civil rights leader, or thinker — whose words speak directly to the emotional and psychological state of someone at work right now.

            SELECTION RULES:
            - The quote MUST be real and accurately attributed. Do NOT paraphrase, fabricate, or misattribute.
            - Draw from a wide span of human history: ancient philosophers (Stoics, Confucians, Platonists), Renaissance thinkers, Enlightenment figures, 19th-century writers, 20th-century leaders, scientists, and athletes.
            - Vary the source: do not default to the same handful of names (e.g. do not always pick Churchill, Einstein, or Maya Angelou). Surprise the reader with a less obvious but deeply resonant choice.
            - The quote must feel emotionally earned — it should directly address the person's WBI band and dominant mood, not just be generically uplifting.
            - Match tone to emotional state: someone in the Thriving band does not need consolation; someone in the Seek Support band does not need cheerleading — they need solidarity, perspective, and compassion.

            WBI BAND TONE GUIDE:
            - 80–100 (Thriving): Celebrate momentum. Choose quotes about sustained excellence, purpose, and generosity of spirit.
            - 65–79 (Doing Well): Reinforce positive habits. Choose quotes about consistency, presence, and quiet strength.
            - 50–64 (Balanced): Encourage gentle forward motion. Choose quotes about resilience, equanimity, and small steps.
            - 35–49 (Needs Care): Offer grounded comfort. Choose quotes about endurance, self-compassion, and finding footing.
            - 0–34 (Seek Support): Offer deep solidarity. Choose quotes about perseverance through darkness, human connection, and the meaning found in difficulty. Avoid toxic positivity entirely.

            OUTPUT FORMAT — respond with ONLY a valid JSON object, no markdown, no preamble
            {
            "quote": "The exact verbatim quote text here.",
            "author": "Full name of the person",
            "years": "Birth–Death years or birth year if living (e.g. 1879–1955)",
            "who": "One-sentence description of who they were (e.g. Polish-French physicist, Nobel laureate)",
            "context": "One sentence on why this quote is relevant to the person's current emotional state."
            }
            """
        
        pass

    def user_prompt(
        self,
        name: str,
        age: str,
        mood: str,
        wbi: float,
        wbi_label_str: str,
        raw_score: float,
        quadrant: str,
        pa: float,
        na: float,
        instability: float,
        decay_valence: float, /
    ) -> str:
        """
        Builds a richly contextualised, dynamic user prompt per log.
        Every variable from the scoring engine is surfaced so the LLM
        can make a deeply informed quote selection — not just react to
        the mood label, but to the full emotional picture.
        """

        # Translate instability into plain English for the LLM
        if instability < 2.0:
            stability_desc = "very stable and consistent"
        elif instability < 4.0:
            stability_desc = "moderately stable with some fluctuation"
        elif instability < 6.5:
            stability_desc = "noticeably volatile — swinging between positive and negative states"
        else:
            stability_desc = "highly volatile — oscillating sharply between emotional extremes"

        # Translate PA/NA balance into plain English
        pa_na_gap = pa - na
        if pa_na_gap > 4:
            affect_desc = "strong positive affect clearly dominating negative affect"
        elif pa_na_gap > 1:
            affect_desc = "positive affect slightly ahead of negative affect"
        elif pa_na_gap > -1:
            affect_desc = "positive and negative affect roughly in balance"
        elif pa_na_gap > -4:
            affect_desc = "negative affect slightly outweighing positive affect"
        else:
            affect_desc = "negative affect strongly dominating — positive energy is depleted"

        # Map quadrant to a workplace-relevant emotional description
        quadrant_context = {
            "High Arousal / Positive Valence":  "energised and engaged — high activation with positive feeling",
            "Low Arousal / Positive Valence":   "calm and content — low activation but genuinely at ease",
            "High Arousal / Negative Valence":  "activated but distressed — high energy directed inward as stress or frustration",
            "Low Arousal / Negative Valence":   "withdrawn and low — depleted energy with negative feeling",
            "Low Arousal / Near-Neutral":       "emotionally flat — neither energised nor distressed, sitting at baseline",
        }.get(quadrant, quadrant)

        return f"""Select a motivational quote for {name}, who is {age} years old and an employee who has just logged their mood at work.

            THEIR CURRENT EMOTIONAL PROFILE:
            - Mood logged: {mood}
            - Circumplex position: {quadrant_context}
            - Wellbeing Index (WBI): {wbi:.1f} / 100  →  "{wbi_label_str}" band
            - Raw entry score: {raw_score:+.2f} / 10
            - Decay-weighted valence (recent mood trend): {decay_valence:+.2f}
            - Positive Affect score: {pa:.1f} / 10
            - Negative Affect score: {na:.1f} / 10
            - Affect balance: {affect_desc}
            - Mood pattern over time: {stability_desc}

            WHAT THIS TELLS US:
            {name} is currently in the "{wbi_label_str}" wellbeing band. Their mood pattern has been {stability_desc}, and their emotional balance shows {affect_desc}. They are sitting in the {quadrant} zone of the circumplex — {quadrant_context}.

            Select ONE quote that speaks directly and authentically to this specific emotional state. The quote should feel like it was written for this moment and should be appropirate or reletable to their age group."""

    def generate(self, sys_prompt: str, user_prompt: str) -> str:
        """
        Invoke the LLM with properly typed message objects.
        Returns the text content of the response.
        """
        messages = [
            SystemMessage(content=sys_prompt),
            HumanMessage(content=user_prompt),
        ]
        res = self.llm.invoke(messages)
        return json.loads(res.content)

