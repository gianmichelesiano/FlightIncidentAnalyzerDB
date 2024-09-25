# File: app.py
import streamlit as st
from pdf_processor import process_pdf
from prompt_manager import PromptManager
from database import init_db
from ui_components import render_file_uploader, render_instructions, render_results, render_prompt_manager

def main():
    init_db()
    st.title("PDF Aircraft Report Analyzer")

    prompt_manager = PromptManager()
    uploaded_file = render_file_uploader()
    render_prompt_manager(prompt_manager)
    render_instructions()
    # add on sidevar a select bow LLm model eiht option  gpt-4o-2024-08-06  gpt-3.5-turbo-16k
    
    
    # Select the LLM model from the sidebar dropdown
    selected_model = st.sidebar.selectbox("Select LLM Model", ["gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-mini"])

    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            final_report = process_pdf(uploaded_file, prompt_manager.get_prompts(), selected_model)
            render_results(final_report)

if __name__ == "__main__":
    main()