# File: ui_components.py
import streamlit as st
from pdf_processor import format_and_deduplicate_report

def render_file_uploader():
    return st.file_uploader("Choose a PDF file", type="pdf")

def render_instructions():
    st.sidebar.header("Instructions")
    st.sidebar.write("""
    1. Upload a PDF file using the file uploader.
    2. (Optional) Add new prompts using the 'Manage Prompts' section.
    3. Click 'Process PDF' to analyze the document.
    4. View the extracted information in the 'Extraction Results' section.
    """)

def render_results(final_report, selected_model):
    st.header("Extraction Results")
    for field, value in final_report:
        if value:
            print(field, value)
            if len(value) > 200:
                value_formatted = format_and_deduplicate_report(value, selected_model)
            else:
                value_formatted = value
            
            st.subheader(field.replace('_', ' ').title())
            st.markdown(value_formatted)
            

def render_prompt_manager(prompt_manager):
    prompt_manager.render_prompt_management()