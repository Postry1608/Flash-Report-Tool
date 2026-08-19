import io
import os
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
import streamlit as st

# --- DEFINE PAGE CONFIG AT THE VERY TOP ---
st.set_page_config(
    page_title="Flash Reporting Tool",
    page_icon="⚡",
    layout="centered",
)

# --- HIDE "PRESS ENTER TO SUBMIT" & STEPPER (+/-) BUTTONS VIA CSS ---
st.markdown(
    """
    <style>
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- APP HEADER & LOGO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=240)

st.title("⚡ Flash Report Tool")
st.warning(
    "⚠️ All text boxes require descriptive sentences. Vague one or two-word"
    " entries will block submission."
)


# --- DIALOG POP-UP FOR DOWNLOAD & REMINDER ---
@st.dialog("✅ Flash Report Generated Successfully")
def show_download_dialog(pdf_bytes, file_name):
    st.success("The Flash Report has been compiled and validated.")
    st.warning(
        "📧 **Action Required:**\n\n"
        "Please ensure a copy of this generated report is emailed to:\n\n"
        "👉 **Safety@fantasyislandresort.co.uk**"
    )
    st.download_button(
        label="📲 Download Validated Flash Report PDF",
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf",
        use_container_width=True,
    )


# --- INPUT FORM ---
with st.form("flash_report_form", clear_on_submit=False):
    st.subheader("1. General Information")
    col1, col2 = st.columns(2)
    with col1:
        inc_date = st.date_input("Date", format="DD/MM/YYYY")
        incident_type = st.radio(
            "Did an injury occur? *",
            ["Accident", "Near Miss", "Property Damage", "Hazard / Other"],
            horizontal=True,
        )
    with col2:
        inc_time = st.time_input("Time")
        staff_name = st.text_input("Staff Completing Form *")

    area_occured = st.text_input(
        "Area Where Accident / Incident Occured *",
        placeholder="e.g., H&S Office, Millennium Coaster, Ingoldmells Market",
    )

    st.subheader("2. Event Narrative & Actions")
    description = st.text_area(
        "Description of Occurrence *",
        placeholder="Detail what happened, root causes, and any injuries involved...",
    )
    immediate_action = st.text_area(
        "Immediate Action Taken *",
        placeholder="Detail initial steps taken to resolve or isolate the hazard/incident...",
    )
    follow_up_action = st.text_area(
        "Follow Up Actions Required (if applicable)",
        placeholder="Detail ongoing investigations, repairs, or future preventive controls needed...",
    )

    submit_button = st.form_submit_button(
        "Verify and Generate Flash Report", type="primary"
    )

# --- FORM VALIDATION & PDF GENERATION ---
if submit_button:
    required_fields = {
        "Staff Completing Form": staff_name,
        "Area Where Occured": area_occured,
        "Description of Occurrence": description,
        "Immediate Action Taken": immediate_action,
    }

    missing_fields = []
    lazy_fields = []

    for label, val in required_fields.items():
        stripped_val = str(val).strip() if val is not None else ""
        if not stripped_val:
            missing_fields.append(label)
        elif label in [
            "Description of Occurrence",
            "Immediate Action Taken",
        ] and len(stripped_val.split()) < 3:
            lazy_fields.append(label)

    if missing_fields:
        st.error(
            "❌ Cannot generate PDF. The following mandatory fields are empty:"
            f" {', '.join(missing_fields)}"
        )
    elif lazy_fields:
        st.error(
            "❌ Quality Check Failed: The text boxes for"
            f" **{', '.join(lazy_fields)}** require a full descriptive sentence,"
            " not just one or two words."
        )
    else:

        def generate_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30,
            )
            story = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "TitleStyle",
                parent=styles["Heading1"],
                fontSize=16,
                spaceAfter=0,
                textColor=colors.HexColor("#1A365D"),
            )
            h2_style = ParagraphStyle(
                "H2Style",
                parent=styles["Heading2"],
                fontSize=11,
                spaceBefore=8,
                spaceAfter=4,
                textColor=colors.HexColor("#2B6CB0"),
            )
            body_style = ParagraphStyle(
                "BodyStyle", parent=styles["BodyText"], fontSize=9, leading=13
            )
            bold_body = ParagraphStyle(
                "BoldBody", parent=body_style, fontName="Helvetica-Bold"
            )

            # --- HEADER WITH LOGO ---
            if os.path.exists("logo.png"):
                logo_img = RLImage("logo.png", width=120, height=45)
                header_data = [[
                    Paragraph("<b>INCIDENT FLASH REPORT</b>", title_style),
                    logo_img,
                ]]
            else:
                header_data = [[
                    Paragraph("<b>INCIDENT FLASH REPORT</b>", title_style),
                    Paragraph("", body_style),
                ]]

            header_table = Table(header_data, colWidths=[360, 170])
            header_table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ])
            )
            story.append(header_table)
            story.append(Spacer(1, 10))

            formatted_date = inc_date.strftime("%d/%m/%Y") if inc_date else "N/A"

            # --- GENERAL INFORMATION BLOCK ---
            meta_data = [
                [
                    Paragraph("<b>Date:</b>", body_style),
                    Paragraph(formatted_date, body_style),
                    Paragraph("<b>Time:</b>", body_style),
                    Paragraph(str(inc_time), body_style),
                ],
                [
                    Paragraph("<b>Incident Type:</b>", body_style),
                    Paragraph(incident_type, body_style),
                    Paragraph("<b>Completed By:</b>", body_style),
                    Paragraph(staff_name, body_style),
                ],
            ]
            t_meta = Table(meta_data, colWidths=[90, 175, 90, 175])
            t_meta.setStyle(
                TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                    ("BACKGROUND", (2, 0), (2, -1), colors.whitesmoke),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ])
            )
            story.append(Paragraph("1. Incident Overview", h2_style))
            story.append(t_meta)

            # --- LOCATION BLOCK ---
            story.append(Paragraph("2. Location Details", h2_style))
            t_loc = Table(
                [
                    [
                        Paragraph("<b>Area Occured:</b>", body_style),
                        Paragraph(area_occured, body_style),
                    ]
                ],
                colWidths=[100, 430],
            )
            t_loc.setStyle(
                TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ])
            )
            story.append(t_loc)

            # --- NARRATIVE & ACTIONS BLOCK ---
            story.append(Paragraph("3. Event Narrative & Action Plan", h2_style))
            narrative_data = [
                [Paragraph("<b>Description of Occurrence:</b>", bold_body)],
                [Paragraph(description, body_style)],
                [Paragraph("<b>Immediate Action Taken:</b>", bold_body)],
                [Paragraph(immediate_action, body_style)],
                [Paragraph("<b>Follow Up Actions Required:</b>", bold_body)],
                [
                    Paragraph(
                        follow_up_action if follow_up_action.strip() else "None recorded.",
                        body_style,
                    )
                ],
            ]
            t_narrative = Table(narrative_data, colWidths=[530])
            t_narrative.setStyle(
                TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, 0), colors.whitesmoke),
                    ("BACKGROUND", (0, 2), (0, 2), colors.whitesmoke),
                    ("BACKGROUND", (0, 4), (0, 4), colors.whitesmoke),
                ])
            )
            story.append(t_narrative)

            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        pdf_bytes = generate_pdf()
        clean_staff = staff_name.replace(" ", "_")
        clean_date = inc_date.strftime("%d-%m-%Y")
        file_name = f"Flash_Report_{clean_staff}_{clean_date}.pdf"

        show_download_dialog(pdf_bytes, file_name)
