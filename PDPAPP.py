import streamlit as st
import plotly.graph_objects as go

# setup Page Configuration
st.set_page_config(
    page_title="Dissonance Predictor",
    page_icon="🧠",
    layout="wide"
)

# values from "Estimates of Fixed Effects" table of EA2 model
INTERCEPT = 2.897965
# Main Effects
LMM_ALIGNED_EFFECT = -0.378395
LMM_POSITIVE_EFFECT = 0.186541
LMM_LIBERAL_EFFECT = 2.641192
# Two - way Interactions
LMM_ALIGN_VAL_INTERACTION = -0.525035
LMM_ALIGN_IDEO_INTERACTION = -1.615288
LMM_VAL_IDEO_INTERACTION = -1.056119

# app title and description
st.title("🧠 The Political Dissonance Predictor")
st.write(
    "This tool uses a predictive model from experimental research to estimate the level of cognitive dissonance "
    "(on a 1-10 scale) one might experience when faced with a political policy choice."
)
st.write("---")

# create Columns for Layout
col1, col2 = st.columns([1, 2]) # Make panel wider

# slider UI data 
with col1:
    st.header("Select the Dilemma Conditions:")

    # ideology slider
    st.write("**1. Select the person's ideology on a spectrum:**")
    ideology_slider = st.slider(
        "Ideology Spectrum", min_value=0.0, max_value=1.0, value=0.5,
        label_visibility="collapsed", # Hide the default label
        help="0.0 represents a strong conservative, 1.0 a strong liberal, and 0.5 a perfect moderate."
    )
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.caption("<p style='text-align: left;'>Conservative</p>", unsafe_allow_html=True)
    with c3:
        st.caption("<p style='text-align: right;'>Liberal</p>", unsafe_allow_html=True)

    # alignment slider
    st.write("**2. Select the degree of ideological alignment:**")
    alignment_slider = st.slider(
        "Alignment Spectrum", min_value=0.0, max_value=1.0, value=0.5,
        label_visibility="collapsed",
        help="0.0 represents a choice perfectly aligned with ideology, 1.0 a choice in direct conflict."
    )
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.caption("<p style='text-align: left;'>Aligned</p>", unsafe_allow_html=True)
    with c3:
        st.caption("<p style='text-align: right;'>Conflicting</p>", unsafe_allow_html=True)

    # -valence slider
    st.write("**3. Select the nature of the personal outcome:**")
    valence_slider = st.slider(
        "Valence Spectrum", min_value=0.0, max_value=1.0, value=0.5,
        label_visibility="collapsed",
        help="0.0 represents a clearly positive personal outcome, 1.0 a clearly negative outcome."
    )
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.caption("<p style='text-align: left;'>Positive</p>", unsafe_allow_html=True)
    with c3:
        st.caption("<p style='text-align: right;'>Negative</p>", unsafe_allow_html=True)
#caution!!
    st.warning(
        """**Note on Sliders:** The 'Ideology' slider is a plausible interpolation.
        The 'Alignment' and 'Valence' sliders are **theoretical simulations** assuming a perfectly linear transition between the discrete conditions tested in the experiment.
        """,
        icon="⚠️"
    )

# define logic
is_liberal = ideology_slider
is_conflicting = alignment_slider
is_negative = valence_slider

# convert codes
is_aligned_dummy = 1 - is_conflicting
is_positive_dummy = 1 - is_negative
is_liberal_dummy = is_liberal

# FORMULA!
predicted_score = (INTERCEPT +
                   (LMM_ALIGNED_EFFECT * is_aligned_dummy) +
                   (LMM_POSITIVE_EFFECT * is_positive_dummy) +
                   (LMM_LIBERAL_EFFECT * is_liberal_dummy) +
                   (LMM_ALIGN_VAL_INTERACTION * is_aligned_dummy * is_positive_dummy) +
                   (LMM_ALIGN_IDEO_INTERACTION * is_aligned_dummy * is_liberal_dummy) +
                   (LMM_VAL_IDEO_INTERACTION * is_positive_dummy * is_liberal_dummy))

# Cap the score at 10 and 1 [This really is not needed but just in case in future code]
predicted_score = min(max(predicted_score, 1.0), 10.0)

# Results Dashboard
with col2:
    st.header("Predicted Dissonance Score")
    st.metric(label="Score (out of 10)", value=f"{predicted_score:.2f}")

    # Custom Interpretation values 
    if predicted_score >= 4.0:
        st.error(f"**High Dissonance:** A score of {predicted_score:.2f} is in the highest range of predicted psychological discomfort for this model. This choice likely creates significant internal conflict.")
    elif predicted_score >= 3.0:
        st.warning(f"**Moderate Dissonance:** A score of {predicted_score:.2f} indicates a noticeable level of psychological discomfort. The trade-offs in this choice are significant enough to cause internal conflict.")
    else:
        st.success(f"**Low Dissonance:** A score of {predicted_score:.2f} indicates a low level of psychological discomfort. This choice is likely perceived as relatively easy or straightforward.")
    st.progress(predicted_score / 10)
    
    st.write("---")

    # Show ideological spectrum for the selected Alignment/Valence ---
    st.subheader("Dissonance Across the Ideological Spectrum")

    # Calculate endpoints for the chart based on Alignment/Valence slider settings
    conservative_endpoint = (INTERCEPT +
                             (LMM_ALIGNED_EFFECT * is_aligned_dummy) +
                             (LMM_POSITIVE_EFFECT * is_positive_dummy) +
                             (LMM_ALIGN_VAL_INTERACTION * is_aligned_dummy * is_positive_dummy))
    liberal_endpoint = (INTERCEPT +
                        (LMM_ALIGNED_EFFECT * is_aligned_dummy) +
                        (LMM_POSITIVE_EFFECT * is_positive_dummy) +
                        (LMM_LIBERAL_EFFECT * 1) +
                        (LMM_ALIGN_VAL_INTERACTION * is_aligned_dummy * is_positive_dummy) +
                        (LMM_ALIGN_IDEO_INTERACTION * is_aligned_dummy * 1) +
                        (LMM_VAL_IDEO_INTERACTION * is_positive_dummy * 1))
#visuals for the endpoint chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[conservative_endpoint, liberal_endpoint], y=['', ''], mode='lines', line=dict(color='grey', width=10)))
    fig.add_trace(go.Scatter(x=[conservative_endpoint, liberal_endpoint], y=['', ''], mode='markers', marker=dict(color=['blue', 'red'], size=15), text=[f'Conservative Endpoint: {conservative_endpoint:.2f}', f'Liberal Endpoint: {liberal_endpoint:.2f}'], hoverinfo='text'))
    fig.add_trace(go.Scatter(x=[predicted_score], y=[''], mode='markers', marker=dict(color='yellow', size=25, symbol='star'), text=[f'Your Selection: {predicted_score:.2f}'], hoverinfo='text'))

    fig.update_layout(
        title_text=f'Predicted Score Spectrum (at current Alignment/Valence settings)',
        xaxis_title="Predicted Dissonance Score (PCDI)", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)', showlegend=False, yaxis_showticklabels=False, height=250
    )
    st.plotly_chart(fig, use_container_width=True)

st.write("---")

# expander/more details for user to see
with st.expander("Click here to see the predictive model and its application"):
    st.markdown("This calculator is based on a stable **two-way interaction** Linear Mixed-Effects Model (LMM) derived from the study's data:")
    st.code(f"""
    Score = {INTERCEPT:.2f} 
            + ({LMM_ALIGNED_EFFECT:.2f} * IsAligned) 
            + ({LMM_POSITIVE_EFFECT:.2f} * IsPositive) 
            + ({LMM_LIBERAL_EFFECT:.2f} * IsLiberal) 
            + ({LMM_ALIGN_VAL_INTERACTION:.2f} * IsAligned * IsPositive) 
            + ({LMM_ALIGN_IDEO_INTERACTION:.2f} * IsAligned * IsLiberal) 
            + ({LMM_VAL_IDEO_INTERACTION:.2f} * IsPositive * IsLiberal)
    """, language='latex')
    st.markdown(f"""
    - **How the Sliders Work:** This tool simulates a continuous spectrum for all three factors.
        - The **Ideology** slider interpolates between the two ideological groups measured in the study, which is a plausible estimation for moderates.
        - The **Alignment** and **Valence** sliders are **theoretical interpolations**. They assume a perfectly linear, straight-line change in dissonance between the discrete experimental conditions that were actually tested (e.g., 'Aligned' vs. 'Conflicting'). This is a powerful illustration but should be considered a simulation, as the original study did not measure these "in-between" states.
    """
    )

# -ethics/privacy note
with st.expander("A Note on Ethics and Data Privacy"):
    st.markdown("""
    *   **Original Research Data:** The data used to build this predictive model was collected from confidential participants in a research study. The study's protocol was reviewed and approved by an Institutional Review Board (IRB) to ensure it met ethical standards for research with human subjects.
    *   **Your Privacy in this App:** Your selections within this calculator are completely private. **They are not recorded, stored, or monitored in any way.** All calculations are performed temporarily in your browser and the information is discarded when you close the page.
    *   **Purpose:** This tool is for educational and illustrative purposes only. It is a demonstration of a statistical model and is not intended for psychological diagnosis or assessment.
    """)

# sample size note
st.info(
    """**Note:**  This model is based on a final sample of 99 participants (85 Liberal, 14 Conservative) from an undergraduate honors thesis.
    The effects involving 'Ideology' should be interpreted with caution given the small number of conservatives in the data.
    """
)