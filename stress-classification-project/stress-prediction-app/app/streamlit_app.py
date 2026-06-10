import streamlit as st
import json
from pathlib import Path
import sys
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.predictor import StressPredictor

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stress Level Predictor",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Minimal CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Side margins — constrain content width and center it */
[data-testid="stMainBlockContainer"] {
    max-width: 780px;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    margin: 0 auto;
}

/* Larger base font */
html, body, [data-testid="stAppViewContainer"] {
    font-size: 17px;
}

/* Larger label text on sliders and selectboxes */
[data-testid="stWidgetLabel"] p {
    font-size: 1.05rem !important;
}

/* Bigger primary button */
[data-testid="stBaseButton-primary"] {
    font-size: 1.1rem !important;
    padding: 0.65rem 1.5rem !important;
    height: auto !important;
}

/* Result card base */
.result-card {
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.08);
}
.result-low    { background-color: rgba(39, 174, 96, 0.15);  border-left: 5px solid #27ae60; }
.result-medium { background-color: rgba(243, 156, 18, 0.15); border-left: 5px solid #f39c12; }
.result-high   { background-color: rgba(231, 76, 60, 0.15);  border-left: 5px solid #e74c3c; }

.result-label {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    opacity: 0.6;
    margin-bottom: 0.25rem;
}
.result-value {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.result-description {
    font-size: 0.97rem;
    opacity: 0.8;
    margin-top: 0.4rem;
    line-height: 1.5;
}
.result-low    .result-value { color: #2ecc71; }
.result-medium .result-value { color: #f39c12; }
.result-high   .result-value { color: #e74c3c; }

/* Cluster card */
.cluster-card {
    border-radius: 12px;
    padding: 1.25rem 1.75rem;
    margin-bottom: 1rem;
    background-color: rgba(100, 149, 237, 0.12);
    border: 1px solid rgba(100, 149, 237, 0.3);
    border-left: 5px solid #6495ED;
}
.cluster-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #6495ED;
    margin-bottom: 0.3rem;
}
.cluster-description {
    font-size: 0.97rem;
    opacity: 0.82;
    line-height: 1.6;
}

/* Contributing factors */
.factor-card {
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 1rem;
    line-height: 1.6;
    border: 1px solid rgba(255,255,255,0.07);
}
.factor-negative {
    background: rgba(231, 76, 60, 0.08);
    border-left: 4px solid #e74c3c;
}
.factor-positive {
    background: rgba(39, 174, 96, 0.08);
    border-left: 4px solid #27ae60;
}
.factor-rank {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    opacity: 0.5;
    margin-bottom: 0.2rem;
}

/* Tips */
.tip-card {
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 1rem;
    border: 1px solid rgba(255,255,255,0.07);
    line-height: 1.6;
}
.tip-icon { margin-right: 0.4rem; }

/* Section label */
.section-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    opacity: 0.45;
    margin-bottom: 0.75rem;
    margin-top: 1.5rem;
}

/* Divider spacing */
.block-gap { margin-top: 1.25rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

# Requirement 1: Stress level descriptions
STRESS_DESCRIPTIONS = {
    "Low": (
        "Your predicted stress level is low. Based on the research findings, individuals in this "
        "category generally report feeling in control of their daily demands, maintain stable mood "
        "and energy levels, and experience fewer stress-related physical symptoms. Your lifestyle "
        "factors appear to be working in your favor."
    ),
    "Medium": (
        "Your predicted stress level is moderate. Individuals in this category experience "
        "manageable but noticeable stress — enough to affect focus, sleep quality, or mood on "
        "some days. The research suggests that targeted adjustments to one or two lifestyle "
        "factors can meaningfully shift this outcome."
    ),
    "High": (
        "Your predicted stress level is high. Based on the research findings, individuals in this "
        "category are at greater risk of experiencing persistent fatigue, difficulty concentrating, "
        "disrupted sleep, and physical stress symptoms. Addressing the contributing factors below "
        "is strongly recommended."
    ),
}

# Requirement 2: Cluster labels and profile descriptions
CLUSTER_PROFILES = {
    0: {
        "label": "Balanced Lifestyle",
        "description": (
            "People in this cluster carry a lower overall lifestyle load. They tend to sleep more, "
            "work fewer hours, exercise more regularly, and use social media less. Substance use "
            "(smoking and alcohol) is also lower on average. This profile is associated with "
            "predominantly Low to Medium stress levels, suggesting that moderate, balanced habits "
            "act as a buffer against stress."
        ),
    },
    1: {
        "label": "High-Load Lifestyle",
        "description": (
            "People in this cluster carry a higher overall lifestyle load. They tend to work "
            "significantly longer hours, sleep less, exercise less, and spend more time on social "
            "media. Smoking and alcohol consumption are also higher on average. This profile is "
            "strongly associated with High stress — the majority of individuals in this cluster "
            "report elevated stress levels. Notably, diet quality in this group tends to be higher, "
            "suggesting that busier, higher-pressure lifestyles do not necessarily correspond to "
            "poorer eating habits."
        ),
    },
}


def get_stress_description(level: str) -> str:
    return STRESS_DESCRIPTIONS.get(level, "")


def get_cluster_profile(cluster_id: int) -> dict:
    return CLUSTER_PROFILES.get(cluster_id, {
        "label": f"Cluster {cluster_id}",
        "description": "A lifestyle profile group identified by the clustering model.",
    })


# Requirement 3: Contributing factors analysis
def get_contributing_factors(sleep, work, physical, social_media, diet, smoking, alcohol):
    """
    Score each factor by how far it deviates from the research-supported ideal range.
    Returns (negatives[:3], positives) — negatives sorted by impact descending.
    """
    factors = []

    # Sleep — ideal 7–9 hrs
    if sleep < 6:
        factors.append({
            "factor": "Sleep Duration", "icon": "😴", "is_negative": True,
            "score": (6 - sleep) / 6 * 1.0,
            "explanation": (
                f"You sleep approximately {sleep:.1f} hours per night, below the recommended 7–9 hours. "
                f"Sleep deprivation directly raises cortisol levels, making you more physiologically primed "
                f"for stress (Schwarz et al., 2018). Increasing sleep to 7–9 hours is the highest-leverage "
                f"change you can make."
            ),
        })
    elif sleep > 10:
        factors.append({
            "factor": "Sleep Duration", "icon": "😴", "is_negative": True,
            "score": (sleep - 10) / 10 * 0.5,
            "explanation": (
                f"You sleep approximately {sleep:.1f} hours per night, above the recommended range. "
                f"Consistently oversleeping can disrupt your circadian rhythm and increase fatigue "
                f"(Schwarz et al., 2018)."
            ),
        })
    else:
        factors.append({
            "factor": "Sleep Duration", "icon": "😴", "is_negative": False, "score": 0,
            "explanation": (
                f"You're getting {sleep:.1f} hours of sleep — within the recommended 7–9 hour range. "
                f"Adequate sleep is one of the strongest protective factors against stress "
                f"(Schwarz et al., 2018). Keep it up."
            ),
        })

    # Work hours — ideal ≤ 40 hrs/week
    if work > 50:
        factors.append({
            "factor": "Work Hours", "icon": "💼", "is_negative": True,
            "score": (work - 40) / 40 * 0.95,
            "explanation": (
                f"You work approximately {int(work)} hours per week, significantly above the 40-hour "
                f"threshold. Extended hours are strongly linked to psychological stress, irritability, "
                f"and anxiety (Ochiai et al., 2023). Setting boundaries around your schedule could "
                f"meaningfully reduce your stress load."
            ),
        })
    elif work > 40:
        factors.append({
            "factor": "Work Hours", "icon": "💼", "is_negative": True,
            "score": (work - 40) / 40 * 0.5,
            "explanation": (
                f"You work approximately {int(work)} hours per week, slightly above the standard "
                f"threshold. Consistent overtime accumulates stress over time (Ochiai et al., 2023)."
            ),
        })
    else:
        factors.append({
            "factor": "Work Hours", "icon": "💼", "is_negative": False, "score": 0,
            "explanation": (
                f"Your workload of {int(work)} hours per week is within a healthy range. Sustainable "
                f"work hours are associated with lower psychological stress (Ochiai et al., 2023)."
            ),
        })

    # Physical activity — ideal ≥ 3 hrs/week
    if physical < 2:
        factors.append({
            "factor": "Physical Activity", "icon": "🏃", "is_negative": True,
            "score": (2 - physical) / 2 * 0.85,
            "explanation": (
                f"Your physical activity of {physical:.1f} hours per week is quite low. Even light "
                f"activity significantly buffers daily stress and improves mood (Hachenberger et al., 2023). "
                f"Short walks or light exercise on most days can make a measurable difference."
            ),
        })
    else:
        factors.append({
            "factor": "Physical Activity", "icon": "🏃", "is_negative": False, "score": 0,
            "explanation": (
                f"You engage in {physical:.1f} hours of physical activity per week — a healthy level "
                f"associated with better stress regulation and improved mood "
                f"(Hachenberger et al., 2023). This is a strong protective habit."
            ),
        })

    # Social media — ideal ≤ 2 hrs/day
    if social_media > 4:
        factors.append({
            "factor": "Social Media Usage", "icon": "📱", "is_negative": True,
            "score": (social_media - 2) / 2 * 0.75,
            "explanation": (
                f"You spend {social_media:.1f} hours per day on social media, well above the recommended "
                f"limit. Heavy usage is positively associated with higher stress and anxiety in young adults "
                f"(AlAhbabi et al., 2024). Reducing to under 2 hours daily is recommended."
            ),
        })
    elif social_media > 2:
        factors.append({
            "factor": "Social Media Usage", "icon": "📱", "is_negative": True,
            "score": (social_media - 2) / 2 * 0.4,
            "explanation": (
                f"You spend {social_media:.1f} hours per day on social media — moderately elevated. "
                f"Keeping usage under 2 hours avoids stress amplification (AlAhbabi et al., 2024)."
            ),
        })
    else:
        factors.append({
            "factor": "Social Media Usage", "icon": "📱", "is_negative": False, "score": 0,
            "explanation": (
                f"Your social media usage of {social_media:.1f} hours per day is within a healthy range. "
                f"Moderate screen time is associated with lower stress and anxiety "
                f"(AlAhbabi et al., 2024)."
            ),
        })

    # Diet
    if diet == "Unhealthy":
        factors.append({
            "factor": "Diet Quality", "icon": "🥗", "is_negative": True, "score": 0.8,
            "explanation": (
                "Your diet quality is rated as unhealthy. A diet high in fast food, sweets, and sugary "
                "drinks is directly associated with higher stress levels. Diets rich in fruits, vegetables, "
                "and whole grains are protective (Solomou et al., 2024)."
            ),
        })
    elif diet == "Average":
        factors.append({
            "factor": "Diet Quality", "icon": "🥗", "is_negative": True, "score": 0.4,
            "explanation": (
                "Your diet is average — there is room to improve. Evidence shows that whole-food diets "
                "are protective against stress, while processed foods tend to intensify it "
                "(Solomou et al., 2024)."
            ),
        })
    else:
        factors.append({
            "factor": "Diet Quality", "icon": "🥗", "is_negative": False, "score": 0,
            "explanation": (
                "Your diet quality is healthy — a strong protective factor. Research consistently links "
                "nutritious diets to lower stress levels and better mental health (Solomou et al., 2024)."
            ),
        })

    # Smoking
    smoking_scores = {"Non-Smoker": 0, "Occasional Smoker": 0.5, "Regular Smoker": 0.85, "Heavy Smoker": 1.0}
    s_score = smoking_scores.get(smoking, 0)
    if s_score > 0:
        factors.append({
            "factor": "Smoking Habit", "icon": "🚬", "is_negative": True, "score": s_score * 0.7,
            "explanation": (
                f"You smoke ({smoking.lower()}). Smoking and stress reinforce each other — nicotine "
                f"raises baseline stress over time, creating a feedback loop that deepens with continued "
                f"use (Richards et al., 2011). Cessation or reduction would help break this cycle."
            ),
        })
    else:
        factors.append({
            "factor": "Smoking Habit", "icon": "🚬", "is_negative": False, "score": 0,
            "explanation": (
                "You are a non-smoker — a significant protective factor. Avoiding smoking prevents a "
                "feedback loop between nicotine dependence and elevated baseline stress "
                "(Richards et al., 2011)."
            ),
        })

    # Alcohol
    alcohol_scores = {"Non-Drinker": 0, "Social Drinker": 0.2, "Regular Drinker": 0.65, "Heavy Drinker": 1.0}
    a_score = alcohol_scores.get(alcohol, 0)
    if a_score > 0.2:
        factors.append({
            "factor": "Alcohol Consumption", "icon": "🍺", "is_negative": True, "score": a_score * 0.65,
            "explanation": (
                f"Your alcohol consumption is '{alcohol.lower()}'. Alcohol and stress share a reciprocal "
                f"relationship — each intensifies the other over time (Nigam, 2021). Reducing intake "
                f"can interrupt this cycle and lower your baseline stress response."
            ),
        })
    else:
        factors.append({
            "factor": "Alcohol Consumption", "icon": "🍺", "is_negative": False, "score": 0,
            "explanation": (
                f"Your alcohol consumption is {alcohol.lower()} — a healthy level. Keeping alcohol "
                f"use low prevents it from reinforcing stress over time (Nigam, 2021)."
            ),
        })

    negatives = sorted([f for f in factors if f["is_negative"]], key=lambda x: x["score"], reverse=True)
    positives = [f for f in factors if not f["is_negative"]]

    rank_labels = ["#1 — Highest Impact", "#2 — Significant Impact", "#3 — Contributing Factor"]
    for i, f in enumerate(negatives[:3]):
        f["rank_label"] = rank_labels[i]

    return negatives[:3], positives


# Requirement 4: Prioritized recommendations
def get_dynamic_tips(sleep, work, physical, social_media, diet, smoking, alcohol, stress_level):
    """Tips ordered by impact score descending — highest priority first."""
    candidates = []

    if sleep < 6:
        candidates.append(((6 - sleep) / 6 * 1.0, "😴",
            f"Increase sleep to 7–9 hours nightly. You're currently at {sleep:.1f} hours, which raises "
            f"baseline cortisol and makes daily stressors harder to manage (Schwarz et al., 2018). "
            f"Even adding 30–45 minutes per night is a meaningful first step."))
    elif sleep > 10:
        candidates.append((0.3, "😴",
            "Aim for a consistent 7–9 hour sleep schedule rather than oversleeping. Irregular or excessive "
            "sleep disrupts your circadian rhythm and leaves you more fatigued (Schwarz et al., 2018)."))

    if work > 50:
        candidates.append(((work - 40) / 40 * 0.95, "💼",
            f"Set clearer boundaries around your work schedule. At {int(work)} hours per week you are well "
            f"above the threshold linked to elevated psychological stress and anxiety (Ochiai et al., 2023). "
            f"Reducing by even 5–10 hours weekly can help."))
    elif work > 40:
        candidates.append(((work - 40) / 40 * 0.5, "💼",
            f"Monitor your workload — at {int(work)} hours per week you're slightly above sustainable "
            f"levels. Consistent overtime accumulates stress over time (Ochiai et al., 2023)."))

    if physical < 2:
        candidates.append(((2 - physical) / 2 * 0.85, "🏃",
            f"Incorporate more physical activity — you're currently at {physical:.1f} hours per week. "
            f"Even a 20-minute daily walk has been shown to buffer stress and improve mood significantly "
            f"(Hachenberger et al., 2023)."))

    if social_media > 4:
        candidates.append(((social_media - 2) / 2 * 0.75, "📱",
            f"Reduce social media usage to under 2 hours daily. You're currently at {social_media:.1f} "
            f"hours, a level consistently linked to higher anxiety in young adults (AlAhbabi et al., 2024). "
            f"Consider app timers or scheduled screen-free periods."))
    elif social_media > 2:
        candidates.append(((social_media - 2) / 2 * 0.4, "📱",
            f"Your social media usage of {social_media:.1f} hours daily is slightly elevated. Keeping it "
            f"under 2 hours is associated with lower stress (AlAhbabi et al., 2024)."))

    if diet == "Unhealthy":
        candidates.append((0.8, "🥗",
            "Shift your diet toward whole foods — fruits, vegetables, and whole grains are associated with "
            "lower stress, while fast food and sugary drinks amplify it (Solomou et al., 2024). Small "
            "consistent changes matter more than drastic overhauls."))
    elif diet == "Average":
        candidates.append((0.4, "🥗",
            "There's room to improve your diet. Diets rich in whole foods are protective against stress, "
            "while processed foods tend to intensify it (Solomou et al., 2024). Start with one meal per day."))

    if smoking in ["Regular Smoker", "Heavy Smoker"]:
        candidates.append((0.7, "🚬",
            "Consider speaking to a healthcare professional about smoking cessation. Smoking and stress "
            "reinforce each other — nicotine raises your baseline stress over time, creating a cycle that "
            "is harder to break the longer it continues (Richards et al., 2011)."))
    elif smoking == "Occasional Smoker":
        candidates.append((0.4, "🚬",
            "Even occasional smoking interacts with your stress-response systems over time "
            "(Richards et al., 2011). Reducing use now prevents the feedback loop from deepening."))

    if alcohol in ["Regular Drinker", "Heavy Drinker"]:
        candidates.append((0.65, "🍺",
            "Reducing alcohol consumption would help break the stress–alcohol feedback loop. Stress "
            "encourages drinking, and drinking intensifies stress over time (Nigam, 2021). Gradual "
            "reduction is more sustainable than abrupt stopping."))
    elif alcohol == "Social Drinker":
        candidates.append((0.15, "🍺",
            "Be mindful of whether drinking increases during high-stress periods — alcohol and stress "
            "can reinforce each other even at moderate levels (Nigam, 2021)."))

    candidates.sort(key=lambda x: x[0], reverse=True)
    tips = [(icon, tip) for _, icon, tip in candidates[:3]]

    if not tips:
        if stress_level == "High":
            tips.append(("💡", "Your measured habits appear relatively healthy, yet stress is still high. "
                "Other factors — academic pressure, relationships, or environment — may be contributing. "
                "Consider speaking with a counselor or trusted person."))
        elif stress_level == "Medium":
            tips.append(("💡", "Your habits are fairly balanced. Consistent physical activity and adequate "
                "sleep are the two highest-leverage changes for lowering stress "
                "(Hachenberger et al., 2023; Schwarz et al., 2018)."))
        else:
            tips.append(("✅", "Your lifestyle habits look healthy across the board. Balanced sleep, regular "
                "activity, a nutritious diet, and moderate social media use are all protective factors "
                "against stress. Keep it up."))

    return tips


def get_result_class(level: str) -> str:
    return {"Low": "result-low", "Medium": "result-medium", "High": "result-high"}.get(level, "result-medium")


# ── Model loading ─────────────────────────────────────────────────────────────

local_centers = Path(__file__).parent / "cluster_centers.csv"
if not local_centers.exists():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    src_centers = PROJECT_ROOT / "data" / "processed" / "cluster_centers.csv"
    if src_centers.exists():
        try:
            shutil.copy(src_centers, local_centers)
        except Exception:
            pass


@st.cache_resource
def load_model():
    APP_ROOT = Path(__file__).resolve().parents[1]
    model_path = APP_ROOT / "models" / "multinomial_logreg_lifestyle_cluster.pkl"
    config_path = APP_ROOT / "models" / "model_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    predictor = StressPredictor(model_path=str(model_path), config=config)
    return predictor, config


predictor, config = load_model()


# ── Layout ────────────────────────────────────────────────────────────────────

st.markdown("## 🧠 Stress Level Predictor")
st.caption("Enter your daily lifestyle habits to receive a personalized stress level prediction.")
st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Daily Habits</p>', unsafe_allow_html=True)
sleep_hours = st.slider("Sleep (hours per day)", min_value=0.0, max_value=12.0, value=7.0, step=0.25,
                        help="Average hours of sleep per night")
social_media = st.slider("Social Media Usage (hours per day)", min_value=0.0, max_value=12.0, value=2.0, step=0.25)

st.markdown('<p class="section-label">Work & Activity</p>', unsafe_allow_html=True)
work_hours = st.slider("Work (hours per week)", min_value=0, max_value=100, value=40, step=1)
physical_hours = st.slider("Physical Activity (hours per week)", min_value=0.0, max_value=30.0, value=5.0, step=0.5)

st.markdown('<p class="section-label">Lifestyle Choices</p>', unsafe_allow_html=True)
diet_quality = st.selectbox("Diet Quality", options=["Healthy", "Average", "Unhealthy"])
smoking_habit = st.selectbox("Smoking Habit", options=["Non-Smoker", "Occasional Smoker", "Regular Smoker", "Heavy Smoker"])
alcohol_consumption = st.selectbox("Alcohol Consumption", options=["Non-Drinker", "Social Drinker", "Regular Drinker", "Heavy Drinker"])

st.markdown('<div class="block-gap"></div>', unsafe_allow_html=True)
predict_btn = st.button("Predict My Stress Level", type="primary", use_container_width=True)

st.divider()

# ── Results panel ─────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Your Results</p>', unsafe_allow_html=True)

if predict_btn:
    from src.utils.data_processing import validate_lifestyle_input, encode_and_scale_lifestyle, assign_cluster

    raw = {
        "sleep_hours": sleep_hours,
        "work_hours": work_hours,
        "physical_activity_hours": physical_hours,
        "social_media_hours": social_media,
    }

    errors = validate_lifestyle_input(raw)

    if errors:
        for err in errors:
            st.error(err)
    else:
        with st.spinner("Analyzing your lifestyle..."):
            features = encode_and_scale_lifestyle(
                sleep_hours, work_hours, physical_hours, social_media,
                diet_quality, smoking_habit, alcohol_consumption,
            )

            def find_centers_file(start: Path) -> Path:
                local = Path(__file__).parent / "cluster_centers.csv"
                if local.exists():
                    return local.resolve()
                curr = start
                for _ in range(6):
                    candidate = curr / "data" / "processed" / "cluster_centers.csv"
                    if candidate.exists():
                        return candidate.resolve()
                    curr = curr.parent
                raise FileNotFoundError("Could not locate cluster_centers.csv")

            try:
                cluster_id = assign_cluster(features, str(find_centers_file(Path(__file__).parent)))
            except Exception as e:
                st.error(f"Cluster assignment failed: {e}")
                cluster_id = None

            if cluster_id is not None:
                features["Cluster"] = cluster_id
                try:
                    prediction = predictor.predict(features)

                    # ── Requirement 1: Stress level card + description ────────
                    card_class = get_result_class(prediction)
                    stress_desc = get_stress_description(prediction)
                    st.markdown(f"""
                    <div class="result-card {card_class}">
                        <div class="result-label">Predicted Stress Level</div>
                        <div class="result-value">{prediction}</div>
                        <div class="result-description">{stress_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Requirement 2: Cluster assignment card ────────────────
                    st.markdown('<p class="section-label">Your Lifestyle Profile</p>', unsafe_allow_html=True)
                    profile = get_cluster_profile(cluster_id)
                    st.markdown(f"""
                    <div class="cluster-card">
                        <div class="result-label">Lifestyle Cluster {cluster_id}</div>
                        <div class="cluster-name">{profile['label']}</div>
                        <div class="cluster-description">{profile['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Requirement 3: Contributing factors ───────────────────
                    st.markdown('<p class="section-label">Contributing Factors</p>', unsafe_allow_html=True)
                    negatives, positives = get_contributing_factors(
                        sleep_hours, work_hours, physical_hours, social_media,
                        diet_quality, smoking_habit, alcohol_consumption,
                    )

                    if negatives:
                        for f in negatives:
                            st.markdown(f"""
                            <div class="factor-card factor-negative">
                                <div class="factor-rank">{f['rank_label']} &nbsp;·&nbsp; {f['factor']}</div>
                                <span>{f['icon']}&nbsp; {f['explanation']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="factor-card factor-positive">
                            <span>✅&nbsp; No significant negative lifestyle factors were identified. Your habits are working in your favor.</span>
                        </div>
                        """, unsafe_allow_html=True)

                    if positives:
                        with st.expander("✅ Positive habits you're already maintaining"):
                            for f in positives:
                                st.markdown(f"""
                                <div class="factor-card factor-positive">
                                    <div class="factor-rank">{f['factor']}</div>
                                    <span>{f['icon']}&nbsp; {f['explanation']}</span>
                                </div>
                                """, unsafe_allow_html=True)

                    # ── Requirement 4: Prioritized recommendations ────────────
                    st.markdown('<p class="section-label">Personalized Recommendations</p>', unsafe_allow_html=True)
                    tips = get_dynamic_tips(
                        sleep_hours, work_hours, physical_hours, social_media,
                        diet_quality, smoking_habit, alcohol_consumption, prediction,
                    )
                    for i, (icon, tip) in enumerate(tips, 1):
                        priority_label = ["Priority 1", "Priority 2", "Priority 3"][i - 1]
                        st.markdown(f"""
                        <div class="tip-card">
                            <div class="factor-rank">{priority_label}</div>
                            <span class="tip-icon">{icon}</span>{tip}
                        </div>
                        """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Prediction failed: {e}")
else:
    st.info("Fill in your lifestyle information above and click **Predict My Stress Level** to see your results.")