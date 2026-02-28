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
.result-low    .result-value { color: #2ecc71; }
.result-medium .result-value { color: #f39c12; }
.result-high   .result-value { color: #e74c3c; }

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

def get_dynamic_tips(sleep, work, physical, social_media, diet, smoking, alcohol, stress_level):
    """
    Generate tips grounded in the research literature reviewed in the thesis:
    - Sleep deprivation → elevated cortisol/stress (Schwarz et al., 2018)
    - Long working hours → psychological stress, irritability, anxiety (Ochiai et al., 2023)
    - Physical activity (even light) → buffers stress, improves mood (Hachenberger et al., 2023)
    - Heavy social media use → higher stress and anxiety in young adults (AlAhbabi et al., 2024)
    - Unhealthy diet → associated with higher stress; healthy foods protective (Solomou et al., 2024)
    - Smoking ↔ stress reinforce each other (Richards et al., 2011)
    - Alcohol ↔ stress are reciprocal — each intensifies the other (Nigam, 2021)
    """
    tips = []

    # Sleep — Schwarz et al. (2018)
    if sleep < 6:
        tips.append((
            "😴",
            "You're averaging less than 6 hours of sleep. Research shows that sleep deprivation raises baseline cortisol levels, making you more physiologically primed for stress even before your day begins (Schwarz et al., 2018). Prioritizing 7–9 hours can reduce this baseline load."
        ))
    elif sleep > 10:
        tips.append((
            "😴",
            "Sleeping more than 10 hours regularly can disrupt your sleep cycle and leave you feeling more fatigued. A consistent 7–9 hour schedule supports healthier stress regulation (Schwarz et al., 2018)."
        ))

    # Work — Ochiai et al. (2023)
    if work > 50:
        tips.append((
            "💼",
            f"You're working around {int(work)} hours per week. A large-scale study of over 15,000 workers found that employees with extended working hours showed significantly higher psychological stress, irritability, and anxiety — particularly when long hours occurred frequently (Ochiai et al., 2023). Where possible, try to set boundaries around your work schedule."
        ))

    # Physical activity — Hachenberger et al. (2023)
    if physical < 2:
        tips.append((
            "🏃",
            "Your physical activity level is quite low. Studies on university students found that even light physical activity — not just intense exercise — helped buffer daily stress and improved mood on difficult days (Hachenberger et al., 2023). A short walk can make a real difference."
        ))

    # Social media — AlAhbabi et al. (2024)
    if social_media > 4:
        tips.append((
            "📱",
            f"You're spending around {social_media:.1f} hours a day on social media. Research on young adults aged 18–25 found that heavy social media use was positively associated with higher stress and anxiety (AlAhbabi et al., 2024). Reducing your usage — even by an hour — may help lower that load."
        ))

    # Diet — Solomou et al. (2024)
    if diet == "Unhealthy":
        tips.append((
            "🥗",
            "An unhealthy diet is linked to higher stress levels. A systematic review of university students found that stress was associated with greater intake of fast food, sweets, and sugary drinks, while lower stress was linked to fruits, vegetables, and whole grains (Solomou et al., 2024). Small dietary shifts can have a protective effect."
        ))
    elif diet == "Average":
        tips.append((
            "🥗",
            "Your diet is average — there's room to improve. Evidence suggests that diets rich in fruits, vegetables, and whole grains are associated with lower stress levels, while processed and sugary foods tend to amplify it (Solomou et al., 2024)."
        ))

    # Smoking — Richards et al. (2011)
    if smoking in ["Regular Smoker", "Heavy Smoker"]:
        tips.append((
            "🚬",
            "Smoking and stress reinforce each other in a feedback loop — stress drives cravings, while smoking alters your body's stress-response systems over time, raising your baseline stress level (Richards et al., 2011). Speaking to a healthcare professional about cessation strategies may help break this cycle."
        ))
    elif smoking == "Occasional Smoker":
        tips.append((
            "🚬",
            "Even occasional smoking can interact with your stress-response systems. Research shows that stress and smoking reinforce each other, and that nicotine use can gradually increase baseline stress over time (Richards et al., 2011)."
        ))

    # Alcohol — Nigam (2021)
    if alcohol in ["Regular Drinker", "Heavy Drinker"]:
        tips.append((
            "🍺",
            "Alcohol and stress share a reciprocal relationship — stress encourages drinking, while alcohol use intensifies stress over time (Nigam, 2021). Regular or heavy drinking can make it harder for your body to recover from stressors. Reducing intake may help break this cycle."
        ))
    elif alcohol == "Social Drinker":
        tips.append((
            "🍺",
            "Social drinking is generally moderate, but it's worth being mindful that alcohol and stress can reinforce each other over time (Nigam, 2021). Monitor whether drinking increases during high-stress periods."
        ))

    # Fallback if no weak areas detected
    if not tips:
        if stress_level == "High":
            tips.append(("💡", "Your measured habits appear relatively healthy, yet stress is still high. This suggests other factors — such as academic pressure, relationships, or environment — may be contributing. Consider speaking with a counselor or trusted person."))
        elif stress_level == "Medium":
            tips.append(("💡", "Your habits are fairly balanced. The research suggests that consistent physical activity and adequate sleep are the two highest-leverage changes you can make to move stress levels lower (Hachenberger et al., 2023; Schwarz et al., 2018)."))
        else:
            tips.append(("✅", "Your lifestyle habits look healthy across the board. The research consistently shows that balanced sleep, regular activity, a nutritious diet, and moderate social media use act as protective factors against stress. Keep it up."))

    return tips[:3]  # cap at 3 tips


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

            # Cluster assignment
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

                    # Result card
                    card_class = get_result_class(prediction)
                    st.markdown(f"""
                    <div class="result-card {card_class}">
                        <div class="result-label">Predicted Stress Level</div>
                        <div class="result-value">{prediction}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Dynamic tips
                    st.markdown('<p class="section-label">Personalized Insights</p>', unsafe_allow_html=True)
                    tips = get_dynamic_tips(
                        sleep_hours, work_hours, physical_hours, social_media,
                        diet_quality, smoking_habit, alcohol_consumption, prediction
                    )
                    for icon, tip in tips:
                        st.markdown(f"""
                        <div class="tip-card">
                            <span class="tip-icon">{icon}</span>{tip}
                        </div>
                        """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Prediction failed: {e}")
else:
    st.info("Fill in your lifestyle information on the left and click **Predict My Stress Level** to see your results.")