import streamlit as st
from datetime import datetime, date
from database import *
def personal_details():
    st.header("Personal Details")
    st.markdown("Your personal details will be stored in the dependents table as 'Self'.")

    # Fetch existing details if present
    username = st.session_state.get("username")  # Assuming user_id is stored in session
    existing_details = get_self_details(username)

    # Prefill data if exists
    if existing_details:
        name = st.text_input("Name", value=existing_details["Name"])
        dob = st.date_input("Date of Birth", value=existing_details["Date_of_Birth"], min_value=date(1925, 1, 1), max_value=date.today())
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                              index=["Male", "Female", "Other"].index(existing_details["Gender"]))
    else:
        name = st.text_input("Name")
        dob = st.date_input("Date of Birth", min_value=date(1925, 1, 1), max_value=date.today())
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    # Disable adding again, only allow updates
    submit_label = "Update Personal Details" if existing_details else "Save Personal Details"
    submit_personal = st.button(submit_label)

    if submit_personal:
        if name and dob and gender:
            if upsert_self_details(username, name, dob, gender):
                st.success("Personal details saved successfully!")
                st.session_state["updated"] = True  # Trigger UI refresh if needed
                st.rerun()

            else:
                st.error("Failed to update personal details.")
        else:
            st.error("Please fill all fields.")

    ### --- Dependent Details Form ---
    with st.form(key="dependent_form"):
        dep_name = st.text_input("Dependent Name")
        dep_dob = st.date_input("Dependent Date of Birth", min_value=date(1925, 1, 1), max_value=date.today())
        dep_gender = st.selectbox("Dependent Gender", ["Male", "Female", "Other"])
        dep_relationship = st.selectbox("Relationship", ["Spouse", "Children", "Mother", "Father", "Other"])
        submit_dependent = st.form_submit_button(label="Add Dependent")

        if submit_dependent:
            if dep_name and dep_dob and dep_gender and dep_relationship:
                add_dependent(username, dep_name, dep_dob, dep_gender, dep_relationship)
                st.success("Dependent added successfully!")
                st.session_state["updated"] = True
            else:
                st.error("Please fill all fields.")

    ### --- Retrieve and Display Dependents ---
    dependents = get_dependents(username)

    st.subheader("Dependents List")
    if not dependents:
        st.write("No dependents found.")
    else:
        for dep in dependents:
            col1, col2 = st.columns([1, 10])
            with col1:
                if st.button("❌", key=f"delete_Personal_{dep['Dependent_ID']}"):
                    delete_dependent(username,dep["Dependent_ID"])
                    st.session_state["updated"] = True
                    st.rerun()  # Refresh page to reflect changes

            with col2:
                with col2:
                    st.write(f"**{dep['Name']}** - {dep['Relationship']}")