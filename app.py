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

st.set_page_config(page_title="PathFinder AI", page_icon="🧭", layout="centered")

def render_visual_roadmap(steps: list[str]):
    if not steps:
        return
    st.subheader("Roadmap")
    for i, step in enumerate(steps, 1):
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            st.markdown(
                f"""
                <div style="
                    background: #4F46E5;
                    color: white;
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    margin-top: 4px;
                ">{i}</div>
                """,
                unsafe_allow_html=True
            )
            if i < len(steps):
                st.markdown(
                    """<div style="width: 2px; height: 40px; background: #CBD5E1; margin-left: 17px;"></div>""",
                    unsafe_allow_html=True
                )
        with col2:
            st.markdown(f"**{step}**")

def create_concise_pdf(data: dict) -> bytes:
    def clean(text):
        if not text:
            return ""
        text = str(text).replace("–", "-").replace("—", "-").replace("•", "-")
        return " ".join(text.split())

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    usable = 180

    def reset_x():
        pdf.set_x(15)

    # Header
    pdf.set_fill_color(67, 56, 202)
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

    # Title
    title = clean(data.get("title")) or "Personalized Pathway"
    pdf.set_font("Helvetica", "B", 16)
    reset_x()
    pdf.multi_cell(usable, 8, title)
    pdf.ln(2)

    # Timeline
    timeline = clean(data.get("timeline")) or "Flexible"
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(71, 85, 105)
    reset_x()
    pdf.cell(65, 7, f"  Timeline: {timeline}", fill=True, ln=True)
    pdf.ln(6)

    # Why
    why = clean(data.get("why"))
    if why:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(67, 56, 202)
        reset_x()
        pdf.cell(usable, 8, "Why This Fits You", ln=True)
        pdf.set_draw_color(67, 56, 202)
        pdf.set_line_width(0.4)
        pdf.line(15, pdf.get_y(), 70, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        reset_x()
        pdf.multi_cell(usable, 5.2, why)
        pdf.ln(4)

    # Roadmap
    steps = [clean(s) for s in data.get("steps", []) if clean(s)]
    if steps:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(67, 56, 202)
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

    # MDC
    mdc = [clean(p) for p in data.get("mdc", []) if clean(p)]
    if mdc:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(67, 56, 202)
        reset_x()
        pdf.cell(usable, 8, "Best MDC Starting Points", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 41, 59)
        for prog in mdc[:5]:
            reset_x()
            pdf.multi_cell(usable, 5, f"- {prog}")
        pdf.ln(2)

    # Skills
    skills = [clean(s) for s in data.get("skills", []) if clean(s)]
    if skills:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(67, 56, 202)
        reset_x()
        pdf.cell(usable, 8, "Skills to Build Now", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 41, 59)
        for skill in skills[:5]:
            reset_x()
            pdf.multi_cell(usable, 5, f"- {skill}")

    # Footer
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

st.title("🧭 PathFinder AI")
st.caption("Personalized Career Pathways · Starting at Miami Dade College")
st.divider()

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

st.divider()

if st.button("Generate Pathway", type="primary", use_container_width=True):
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

                st.markdown("---")
                st.subheader(data.get("title") or "Personalized Pathway")
                if data.get("why"):
                    st.info(data["why"])

                render_visual_roadmap(data.get("steps", []))

                col_a, col_b = st.columns(2)
                with col_a:
                    if data.get("mdc"):
                        st.subheader("Best MDC Starting Points")
                        for prog in data["mdc"]:
                            st.markdown(f"- **{prog}**")
                with col_b:
                    if data.get("skills"):
                        st.subheader("Skills to Build Now")
                        for skill in data["skills"]:
                            st.markdown(f"- {skill}")

                if data.get("jobs"):
                    st.subheader("Possible Job Titles")
                    for job in data["jobs"]:
                        st.markdown(f"- {job}")

                if data.get("next_actions"):
                    st.subheader("Next Actions (This Month)")
                    for i, action in enumerate(data["next_actions"], 1):
                        st.markdown(f"{i}. {action}")

                # PDF
                try:
                    pdf_bytes = create_concise_pdf(data)
                    st.download_button(
                        label="Download Concise PDF",
                        data=pdf_bytes,
                        file_name="PathFinder_Pathway.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as pdf_err:
                    st.warning("Pathway generated, but PDF export failed.")
                    st.code(str(pdf_err))

            except Exception as e:
                st.error("Something went wrong:")
                st.code(str(e))

st.divider()
st.caption("PathFinder AI · MDC Challenge")