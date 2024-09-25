import streamlit as st
from pdf_processor import process_pdf
from prompt_manager import PromptManager
from database import init_db
from ui_components import render_file_uploader, render_instructions, render_results, render_prompt_manager
import time 
import json

def display_formatted_json(file_path):
    try:
        with open(file_path, 'r') as file:
            # Load the JSON content
            json_content = json.load(file)
            
            # Format the JSON with indentation
            formatted_json = json.dumps(json_content, indent=2)
            
            st.write("File Content:")
            
            # Display the formatted JSON in a text area
            st.text_area("JSON Content", value=formatted_json, height=300)
    except json.JSONDecodeError:
        st.error("The file is not a valid JSON.")
    except FileNotFoundError:
        st.error("The specified file was not found.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def main_page():
    st.title("PDF Aircraft Report Analyzer")

    prompt_manager = PromptManager()
    uploaded_file = render_file_uploader()
    render_prompt_manager(prompt_manager)
    render_instructions()

    # Select the LLM model from the sidebar dropdown
    selected_model = st.sidebar.selectbox("Select LLM Model", ["gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-mini"])

    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            final_report = process_pdf(uploaded_file, prompt_manager.get_prompts(), selected_model)
            render_results(final_report)

def select_report_page():
    st.title("Select Report")

    reports = PromptManager().get_report()


    report_options = {f"{report[0]} - {report[1]}": report[3] for report in reports}

    # Create a select box with the report options
    selected_report = st.selectbox("Select a Report", list(report_options.keys()))
    
    # Display the selected report URL
    if selected_report:
        # Write the selected report ID and URL
        st.write(f"Selected Report ID: {selected_report.split(' - ')[0]}")
        st.write(f"Selected Report URL: {report_options[selected_report]}")
        
        # Open and write to the file in the specified directory
        report_id = selected_report.split(' - ')[0]
        file_path = f"safety-scan-export-20240823-102233/{report_id}.json"
       
        # try:
        #     with open(file_path, 'r') as file:
        #         file_content = file.read()
        #     st.text(display_formatted_json(file_path))
        # except Exception as e:
        #     st.error(f"An error occurred while writing or reading the file: {e}")
            


def main():
    init_db()

    # Create a dictionary of pages
    pages = {
        "Analyze Report": main_page,
        "Select Report": select_report_page
    }

    # Add sidebar navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Display the selected page
    pages[selection]()



if __name__ == "__main__":
    main()