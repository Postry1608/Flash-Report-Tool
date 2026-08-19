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

    # Conditionally show text box if "Hazard / Other" is selected
    other_type_detail = ""
    if incident_type == "Hazard / Other":
        other_type_detail = st.text_input(
            "Specify 'Other' Incident Type *",
            placeholder="e.g., Environmental Spill, Security Issue, Slip Hazard",
        )

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
