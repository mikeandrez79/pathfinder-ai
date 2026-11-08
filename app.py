import streamlit as st
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

st.set_page_config(page_title="PathFinder AI", page_icon="🦈", layout="centered")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%);
        padding: 2rem 2rem 1.6rem 2rem;
        border-radius: 18px;
        margin-bottom: 1.6rem;
        color: white;
        box-shadow: 0 4px 14px rgba(15, 118, 110, 0.25);
    }
    .main-header h1 {
        color: white !important;
        margin-bottom: 0.25rem;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .main-header p {
        color: #CCFBF1 !important;
        font-size: 1.05rem;
        margin: 0;
    }
    .stTextArea textarea, .stTextInput input, .stSelectbox div {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0F766E 0%, #0D9488 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        color: white !important;
        padding: 0.7rem 1rem !important;
        font-size: 1.05rem !important;
    }
    .stButton > button {
        border-radius: 14px !important;
        padding: 0.85rem 1rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border: 1.5px solid #0F766E !important;
        color: #0F766E !important;
        background: white !important;
    }
    .stButton > button:hover {
        background: #F0FDFA !important;
    }
    .stDownloadButton > button {
        background: #0F766E !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def render_visual_roadmap(steps: list[str]):
    if not steps:
        return
    for i, step in enumerate(steps, 1):
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            st.markdown(
                f"""
                <div style="
                    background: #0F766E;
                    color: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 1.1rem;
                    margin-top: 4px;
                ">{i}</div>
                """,
                unsafe_allow_html=True
            )
            if i < len(steps):
                st.markdown(
                    """<div style="width: 2px; height: 44px; background: #CBD5E1; margin-left: 19px;"></div>""",
                    unsafe_allow_html=True
                )
        with col2:
            st.markdown(f"<div style='padding-top: 8px; font-size: 1.05rem;'><strong>{step}</strong></div>", unsafe_allow_html=True)

def create_concise_pdf(data: dict) -> bytes:
    def clean(text):
        if not text:
            return ""
        text = str(text)
        replacements = {
            "–": "-", "—": "-", "•": "-", "’": "'", "‘": "'",
            "“": '"', "”": '"', "…": "...", "\u00a0": " "
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return " ".join(text.split()).strip()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    usable = 180

    def reset_x():
        pdf.set_x(15)

    pdf.set_fill_color(15, 118, 110)
    pdf.rect(0, 0, 210, 32, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(15, 8)
    pdf.cell(usable, 10, "PathFinder AI")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 18)
    pdf.cell(usable, 8, "Personalized Career Pathway  |  Miami Dade College")

    pdf.set_text_color(30, 41, 59)
    pdf.set_xy(15, 42)

    title = clean(data.get("title")) or "Personalized Pathway"
    pdf.set_font("Helvetica", "B", 16)
    reset_x()
    pdf.multi_cell(usable, 8, title)
    pdf.ln(2)

    timeline = clean(data.get("timeline")) or "Flexible"
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(240, 253, 250)
    pdf.set_text_color(19, 78, 74)
    reset_x()
    pdf.cell(70, 7, f"  Timeline: {timeline}", fill=True, ln=True)
    pdf.ln(6)

    why = clean(data.get("why"))
    if why:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(15, 118, 110)
        reset_x()
        pdf.cell(usable, 8, "Why This Fits You", ln=True)
        pdf.set_draw_color(15, 118, 110)
        pdf.set_line_width(0.4)
        pdf.line(15, pdf.get_y(), 70, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        reset_x()
        pdf.multi_cell(usable, 5.2, why)
        pdf.ln(4)

    steps = [clean(s) for s in data.get("steps", []) if clean(s)]
    if steps:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(15, 118, 110)
        reset_x()
        pdf.cell(usable, 8, "Roadmap", ln=True)
        pdf.line(15, pdf.get_y(), 45, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        for i, step in enumerate(steps, 1):
            reset_x()
            pdf.multi_cell(usable, 5.5, f"{i}. {step}")
            pdf.ln(1)

    pdf.ln(3)

    mdc = [clean(p) for p in data.get("mdc", []) if clean(p)]
    if mdc:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 118, 110)
        reset_x()
        pdf.cell(usable, 8, "Best MDC Starting Points", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 41, 59)
        for prog in mdc[:5]:
            reset_x()
            pdf.multi_cell(usable, 5, f"- {prog}")
        pdf.ln(2)

    skills = [clean(s) for s in data.get("skills", []) if clean(s)]
    if skills:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 118, 110)
        reset_x()
        pdf.cell(usable, 8, "Skills to Build Now", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 41, 59)
        for skill in skills[:5]:
            reset_x()
            pdf.multi_cell(usable, 5, f"- {skill}")

    pdf.set_y(-18)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    reset_x()
    pdf.cell(usable, 6, "Generated by PathFinder AI  |  Personalized for your background", align="C")

    return bytes(pdf.output())

def parse_pathway(text: str) -> dict:
    data = {
        "title": "",
        "why": "",
        "steps": [],
        "mdc": [],
        "skills": [],
        "jobs": [],
        "next_actions": []
    }
    if not text:
        return data

    sections = re.split(r"###\s+", text)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        if not lines:
            continue
        header = lines[0].lower()
        content = lines[1:]

        if "pathway title" in header:
            data["title"] = content[0] if content else ""
        elif "why this fits" in header:
            data["why"] = " ".join(content)
        elif "roadmap" in header:
            data["steps"] = [re.sub(r"^\d+[\.\)]\s*", "", line) for line in content if re.match(r"^\d+[\.\)]", line)]
        elif "mdc starting" in header or "starting points" in header:
            data["mdc"] = [line.lstrip("-•* ").strip() for line in content if line.startswith(("-", "•", "*"))]
        elif "skills to build" in header or "skills" in header:
            data["skills"] = [line.lstrip("-•* ").strip() for line in content if line.startswith(("-", "•", "*"))]
        elif "possible job" in header or "job titles" in header:
            data["jobs"] = [line.lstrip("-•* ").strip() for line in content if line.startswith(("-", "•", "*"))]
        elif "next actions" in header:
            data["next_actions"] = [re.sub(r"^\d+[\.\)]\s*", "", line) for line in content if re.match(r"^\d+[\.\)]", line)]

    return data

# Header
st.markdown("""
<div class="main-header">
    <h1>🦈 PathFinder AI</h1>
    <p>Personalized Career Pathways · Starting at Miami Dade College</p>
</div>
""", unsafe_allow_html=True)

# Session state
if "page" not in st.session_state:
    st.session_state.page = "form"
if "pathway_data" not in st.session_state:
    st.session_state.pathway_data = None
if "results_view" not in st.session_state:
    st.session_state.results_view = "why"

# ===================== FORM PAGE =====================
if st.session_state.page == "form":
    st.markdown("Tell us about your background and goal. We’ll build a realistic pathway that starts from where you are.")

    st.subheader("Your Information")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name (optional)")
    with col2:
        timeline = st.selectbox("Timeline", ["1–2 years", "2–3 years", "3–4 years", "Flexible"])

    background = st.text_area(
        "Background & Experience",
        height=100,
        placeholder="Example: 5 years in professional kitchens + some IT experience"
    )
    goal = st.text_area(
        "Career Goal",
        height=80,
        placeholder="Example: Combine kitchen experience with technology"
    )
    extra = st.text_input("Any constraints? (optional)", placeholder="Need to work full-time, limited budget, etc.")

    st.write("")

    if st.button("Generate My Pathway", type="primary", use_container_width=True):
        if not background.strip() or not goal.strip():
            st.warning("Please fill in both Background and Career Goal.")
        else:
            with st.spinner("Building your personalized pathway..."):
                prompt = f"""
You are PathFinder AI, a concise career advisor for Miami Dade College students.
Student info:
- Background: {background}
- Goal: {goal}
- Timeline: {timeline}
- Constraints: {extra if extra else "None"}
Create a short, precise, practical pathway. Keep it tight and useful. No fluff.
Use exactly this structure and formatting:
### Pathway Title
(Short and clear name)
### Why This Fits You
(2 short sentences maximum)
### Roadmap
1. 
2. 
3. 
4. 
(Maximum 5 steps. Be specific and actionable.)
### Best MDC Starting Points
- Program 1
- Program 2
- Program 3
### Skills to Build Now
- Skill 1
- Skill 2
- Skill 3
### Possible Job Titles
- Title 1
- Title 2
- Title 3
### Next Actions (This Month)
1. 
2. 
3. 
Rules:
- Be concise.
- Focus on real MDC program types (certificates, AS degrees, bachelor’s).
- Respect the student’s existing experience.
- Prefer hybrid/unique combinations when the background allows it.
"""
                try:
                    response = client.chat.completions.create(
                        model="grok-4.3",
                        messages=[
                            {"role": "system", "content": "You are a concise and practical career pathway advisor."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.6
                    )
                    result = response.choices[0].message.content
                    data = parse_pathway(result)
                    data["timeline"] = timeline
                    st.session_state.pathway_data = data
                    st.session_state.page = "results"
                    st.session_state.results_view = "why"
                    st.rerun()
                except Exception as e:
                    st.error("Something went wrong:")
                    st.code(str(e))

# ===================== RESULTS PAGE =====================
elif st.session_state.page == "results" and st.session_state.pathway_data:
    data = st.session_state.pathway_data

    if st.button("← Back to form"):
        st.session_state.page = "form"
        st.session_state.results_view = "why"
        st.rerun()

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0F766E 0%, #0D9488 100%);
        color: white;
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        margin-bottom: 1.6rem;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.2);
    ">
        <h2 style="margin:0; color:white; font-size:1.75rem;">🎯 {data.get("title") or "Personalized Pathway"}</h2>
    </div>
    """, unsafe_allow_html=True)

    # ---------- WHY VIEW ----------
    if st.session_state.results_view == "why":
        if data.get("why"):
            st.markdown(f"""
            <div style="
                background:#F0FDFA;
                border-left: 5px solid #0F766E;
                padding: 1.3rem 1.5rem;
                border-radius: 14px;
                margin-bottom: 2rem;
                color:#134E4A;
                font-size:1.05rem;
            ">
                <strong>💡 Why this fits you</strong><br><br>
                {data["why"]}
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("### Explore your pathway")
        st.write("")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🗺️  Roadmap", use_container_width=True):
                st.session_state.results_view = "roadmap"
                st.rerun()
        with col2:
            if st.button("🏫  Skills & Programs", use_container_width=True):
                st.session_state.results_view = "skills"
                st.rerun()
        with col3:
            if st.button("💼  Jobs & Actions", use_container_width=True):
                st.session_state.results_view = "jobs"
                st.rerun()

    # ---------- ROADMAP ----------
    elif st.session_state.results_view == "roadmap":
        if st.button("← Back"):
            st.session_state.results_view = "why"
            st.rerun()
        st.markdown("### Your Step-by-Step Roadmap")
        st.write("")
        if data.get("steps"):
            render_visual_roadmap(data["steps"])
        else:
            st.info("No roadmap steps generated.")

    # ---------- SKILLS ----------
    elif st.session_state.results_view == "skills":
        if st.button("← Back"):
            st.session_state.results_view = "why"
            st.rerun()
        col_a, col_b = st.columns(2)
        with col_a:
            if data.get("mdc"):
                st.markdown("**🏫 Best MDC Starting Points**")
                for prog in data["mdc"]:
                    st.markdown(f"""
                    <div style="
                        background:#F8FAFC;
                        border:1px solid #E2E8F0;
                        border-radius:14px;
                        padding:0.9rem 1.1rem;
                        margin-bottom:0.65rem;
                        font-size:1rem;
                    ">📘 {prog}</div>
                    """, unsafe_allow_html=True)
        with col_b:
            if data.get("skills"):
                st.markdown("**⚡ Skills to Build Now**")
                for skill in data["skills"]:
                    st.markdown(f"""
                    <div style="
                        background:#F8FAFC;
                        border:1px solid #E2E8F0;
                        border-radius:14px;
                        padding:0.9rem 1.1rem;
                        margin-bottom:0.65rem;
                        font-size:1rem;
                    ">🛠️ {skill}</div>
                    """, unsafe_allow_html=True)

    # ---------- JOBS ----------
    elif st.session_state.results_view == "jobs":
        if st.button("← Back"):
            st.session_state.results_view = "why"
            st.rerun()

        if data.get("jobs"):
            st.markdown("**💼 Possible Job Titles**")
            job_cols = st.columns(min(3, len(data["jobs"])))
            for i, job in enumerate(data["jobs"][:3]):
                with job_cols[i]:
                    st.markdown(f"""
                    <div style="
                        background:#F0FDFA;
                        border-radius:14px;
                        padding:1rem 0.7rem;
                        text-align:center;
                        border:1px solid #CCFBF1;
                        font-size:1rem;
                    ">{job}</div>
                    """, unsafe_allow_html=True)
            st.write("")

        if data.get("next_actions"):
            st.markdown("**✅ Next Actions This Month**")
            for i, action in enumerate(data["next_actions"], 1):
                st.markdown(f"""
                <div style="
                    background:#F8FAFC;
                    border-radius:12px;
                    padding:0.75rem 1.1rem;
                    margin-bottom:0.55rem;
                    border-left:4px solid #0F766E;
                    font-size:1rem;
                "><strong>{i}.</strong> {action}</div>
                """, unsafe_allow_html=True)

        st.write("")
        st.write("")
        try:
            pdf_bytes = create_concise_pdf(data)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name="PathFinder_Pathway.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as pdf_err:
            st.warning("PDF export failed.")
            st.code(str(pdf_err))

st.divider()
st.caption("PathFinder AI · MDC Challenge")
