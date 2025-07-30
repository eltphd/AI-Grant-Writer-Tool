"""Frontend helper utilities for Streamlit.

This module contains helper functions used by the Streamlit UI to
render questions and perform simple checks.  The functions here were
carried over from the original AI‑Grant‑Writer tool so that we can
preserve existing behaviour such as showing chat history and
displaying helpful messages when credentials are missing.

Functions:
    display_message_dialog(text): Show a modal dialog with chat history.
    render_questions(questions, files, selected_project): Render a list
        of questions with controls for generating responses, viewing
        chat history and deleting entries.
    check_credentials(): Verify that the back‑end has valid API
        credentials configured.
"""

import streamlit as st

# Local imports
import utils.utils as utils  # type: ignore
import utils.fast_api_utils as fast_api_utils  # type: ignore


@st.experimental_dialog("Chat history")
def display_message_dialog(text: str) -> None:
    """Display the provided text in a modal dialog.

    Args:
        text: The chat history or other content to display.
    """
    st.write(text)


def render_questions(questions: list, files: list, selected_project: dict) -> None:
    """Render a set of questions and provide controls for each.

    Each question will be displayed in an expander with a text area for
    the answer and buttons to trigger a RAG response, view chat history
    or delete the question.  When the generate button is pressed the
    RAG pipeline will run and update the answer in place.  Deleting a
    question immediately updates the list in session state and
    persists the change to the back‑end.

    Args:
        questions: A list of question records stored in session state.
        files: A list of selected file names used for context in RAG.
        selected_project: The currently selected project object.
    """
    if questions:
        for ix, question in enumerate(questions):
            with st.expander(f"{ix+1}. {question[1]}", expanded=True):
                st.text_area(
                    "Write your answer here",
                    value=question[2],
                    key=f"question_{ix}",
                    height=200,
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Generate response", key=f"gen_button_{ix}"):
                        with st.spinner("Running..."):
                            utils.ask_rag_question_update_questions_v2(questions, ix, files)
                with col2:
                    if st.button("Display chat history", key=f"chat_history_button_{ix}"):
                        display_message_dialog(question[5])
                with col3:
                    if st.button("Delete question", key=f"delete_button_{ix}"):
                        utils.remove_question_from_list(ix, questions, selected_project)


def check_credentials() -> None:
    """Display a message if OpenAI credentials are missing.

    If the API does not indicate that credentials are OK, a message is
    shown and Streamlit execution stops.  This replicates the
    behaviour of the original application.
    """
    if st.session_state.get("credentials") != "OK":
        st.write(
            "Please provide your OPEN API KEY in the config ( ./config/.env ) and restart "
        )
        st.stop()


if __name__ == "__main__":
    pass