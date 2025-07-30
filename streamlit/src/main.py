"""Streamlit application for the AI Grant Writer tool.

This file defines the Streamlit UI and orchestrates interactions with the
FastAPI back‑end via utility modules.  It has been extended to include
client intake, project creation with client selection, audio transcription
support and improved error handling.
"""

import streamlit as st
import asyncio  # noqa: F401 - reserved for future async usage

# Local imports
import utils.utils as utils  # type: ignore
import utils.fast_api_utils as fast_api_utils  # type: ignore
import utils.fe_utils as fe_utils  # type: ignore
import utils.client_api_utils as client_api_utils  # type: ignore
import utils.audio_utils as audio_utils  # type: ignore

# Import configuration for Streamlit front‑end
import utils.config as app_config  # type: ignore


def main() -> None:
    st.title("AI Grant Writer")

    # Ensure core data (projects, files, credentials) is loaded into session state
    utils.get_data_from_db(
        st.session_state.get("projects"),
        st.session_state.get("files"),
        st.session_state.get("credentials"),
    )

    # Preload clients into session state if not already present
    if "clients" not in st.session_state:
        st.session_state["clients"] = client_api_utils.get_clients()

    # Check credentials and prompt user if missing
    fe_utils.check_credentials()

    # Define tabs: client intake, upload, generate
    tab_client, tab_upload, tab_generate = st.tabs([
        "Client Intake",
        "Upload Supporting Files/ Text",
        "Generate Text",
    ])

    # -------------------------------------------------------------------------
    # Client intake tab
    # -------------------------------------------------------------------------
    with tab_client:
        st.header("Client Intake", anchor="client-intake")
        with st.form("client_intake_form"):
            name = st.text_input("Client Name")
            organization = st.text_input("Organization")
            contact_info = st.text_input("Contact Info")
            demographics = st.text_input("Demographics")
            goals = st.text_area("Goals / Objectives", height=150)
            if st.form_submit_button("Create Client"):
                status_code = client_api_utils.create_client(
                    name,
                    organization,
                    contact_info,
                    demographics,
                    goals,
                )
                if status_code == 200:
                    st.success(f"Client '{name}' created successfully!")
                    # Refresh client list
                    st.session_state["clients"] = client_api_utils.get_clients()
                else:
                    st.error("Failed to create client. Please check the API logs.")

        # Display existing clients for reference
        if st.session_state.get("clients"):
            st.subheader("Existing Clients")
            for row in st.session_state.clients:
                try:
                    client_id, client_name, org, contact, demo, goal = row[:6]
                    st.markdown(f"**{client_name}** (ID: {client_id}) — {org}")
                except Exception:
                    continue

    # -------------------------------------------------------------------------
    # Upload tab (files/text/audio)
    # -------------------------------------------------------------------------
    with tab_upload:
        st.header("Upload a file", anchor="upload-file")
        with st.form("manual_file_upload"):
            uploaded_file = st.file_uploader(
                "Please upload your files (PDF, TXT, or audio)",
                type=["pdf", "txt", "wav", "mp3", "m4a"],
                key="submit_files",
            )
            if st.form_submit_button("Submit File"):
                if uploaded_file is not None:
                    # Check if the uploaded file is an audio file
                    if uploaded_file.type.startswith("audio"):
                        # Attempt transcription via Whisper
                        transcribed = audio_utils.transcribe_audio(uploaded_file)
                        if transcribed:
                            # Save as manual text snippet
                            status = fast_api_utils.insert_text_snippet(transcribed)
                            if status == 200:
                                st.success("Audio transcribed and stored successfully.")
                                utils.delete_list_from_state_helper(["files", "questions", "projects"])
                            else:
                                st.error("Failed to store transcription.")
                        else:
                            st.error("Transcription failed. Ensure Whisper is installed.")
                    else:
                        status_code = fast_api_utils.insert_file_v2(uploaded_file.name, uploaded_file)
                        if status_code == 200:
                            st.success(f"{uploaded_file.name} uploaded successfully!")
                            utils.delete_list_from_state_helper(["files", "questions", "projects"])
                        else:
                            st.error("File upload failed.")

        st.header("Manual text upload", anchor="manual-text-upload")
        with st.form("manual_text_upload"):
            st.text_area("Please add supporting text", key="manual_text")
            if st.form_submit_button("Submit Text"):
                utils.submit_manual_text()

    # -------------------------------------------------------------------------
    # Generate tab (project and questions)
    # -------------------------------------------------------------------------
    with tab_generate:
        st.header("Create project", anchor="create-project")
        with st.form("create_project_form"):
            st.text_input("Add your project name here", key="project_name")
            st.text_area("Add your project description here", key="project_description")
            # Client selector (hidden in single‑client mode)
            if app_config.SINGLE_CLIENT_MODE:
                # Ensure at least one client exists.  If no clients are found,
                # create a default client automatically.
                clients = st.session_state.get("clients", [])
                if not clients:
                    # Create a generic client record with minimal information.
                    default_name = "Default Client"
                    default_org = ""
                    default_contact = ""
                    default_demo = ""
                    default_goals = ""
                    status_code = client_api_utils.create_client(
                        default_name,
                        default_org,
                        default_contact,
                        default_demo,
                        default_goals,
                    )
                    if status_code == 200:
                        # Refresh client list after insertion
                        st.session_state["clients"] = client_api_utils.get_clients()
                        clients = st.session_state.get("clients", [])
                # Select the first client in the list as the default
                if clients:
                    try:
                        st.session_state["selected_client_id"] = clients[0][0]
                    except Exception:
                        st.session_state["selected_client_id"] = None
                else:
                    st.session_state["selected_client_id"] = None
            else:
                # Standard multi‑client mode: render a drop‑down for selection
                clients = st.session_state.get("clients", [])
                client_options: dict[str, int] = {}
                for row in clients:
                    try:
                        cid, cname = row[0], row[1]
                        client_options[cname] = cid
                    except Exception:
                        continue
                if client_options:
                    selected_client = st.selectbox(
                        "Select client",
                        list(client_options.keys()),
                        key="selected_client",
                    )
                    st.session_state["selected_client_id"] = client_options.get(selected_client)
                else:
                    st.session_state["selected_client_id"] = None
            if st.form_submit_button("Submit"):
                utils.handle_project()

        # File selection
        st.header("Select files", anchor="select-file")
        if st.session_state.get("files"):
            st.multiselect(
                "Select your files",
                [x[1] for x in st.session_state.files],
                key="selected_files",
            )
        else:
            st.write(
                "No files found, please upload a file on the prior tab \"Upload Supporting Files/ Text\"."
            )

        # Project selection
        projects = st.session_state.get("projects")
        if projects:
            st.header("Select project", anchor="select-project")
            project_dict = {
                x[1]: {"id": x[0], "name": x[1], "description": x[2]} for x in projects
            }
            st.selectbox(
                "Select your project",
                project_dict.keys(),
                on_change=utils.handle_project_select_callback,
                key="selected_project",
            )
            if selected_project := st.session_state.get("selected_project"):
                st.write(
                    f"Project Description:\n\n  {project_dict.get(selected_project, {}).get('description', '')}"
                )

        # Load questions when project and files are selected
        if (
            (selected_project := st.session_state.get("selected_project"))
            and project_dict
            and not st.session_state.get("questions")
        ):
            st.session_state["questions"] = fast_api_utils.get_questions(project_dict[selected_project])

        st.header("Input Questions", anchor="input-questions")
        questions_state = st.session_state.get("questions")
        if questions_state:
            if not st.session_state.get("selected_files"):
                st.write("No source files selected, please select a file for reference.")
                st.markdown("[Select a file](#select-file)")
            fe_utils.render_questions(
                st.session_state.get("questions"),
                st.session_state.get("selected_files", []),
                project_dict[st.session_state.selected_project],
            )
        else:
            st.write("No questions found. Please add a question.")

        st.header("Add question", anchor="add-question")
        with st.form("add_question_form"):
            new_question = st.text_area("Add question here", height=200)
            if st.form_submit_button("Submit"):
                utils.add_question_helper(project_dict, new_question)

        # Save questions to database
        if st.session_state.get("questions"):
            st.header("Save to database", anchor="save-questions")
            if st.button("Save questions to DB"):
                with st.spinner(text="In progress..."):
                    parsed_questions = utils.format_questions(st.session_state.questions)
                    response = fast_api_utils.save_questions(parsed_questions, project_dict[st.session_state.selected_project])
                    if response.get("result"):
                        st.toast("Questions saved!")


if __name__ == "__main__":
    main()