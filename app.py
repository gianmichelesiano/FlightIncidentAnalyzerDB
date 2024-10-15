import streamlit as st
from pdf_processor import process_pdf
from prompt_manager import PromptManager
from database import init_db
from ui_components import render_file_uploader, render_instructions, render_results, render_prompt_manager
import time 
import json
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

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
    if not uploaded_file:
        render_prompt_manager(prompt_manager)
    render_instructions()

    # Select the LLM model from the sidebar dropdown
    #selected_model = st.sidebar.selectbox("Select LLM Model", ["gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-mini", "llama3.2"])
    selected_model = selected_model = st.sidebar.selectbox(
        "Select LLM Model",
        ["gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-mini"],
        key="model_select"  # Add a unique key
    )

    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            final_report = process_pdf(uploaded_file, prompt_manager.get_prompts(), selected_model)
            render_results(final_report, selected_model)

def select_report_page():
    st.title("Reports list")
    
    countries = ["", "CA", "US", "DE", "AU", "FR", "AT", "CH", "GB"]
    country_labels = {
        "": "Select a country",  # Add a label for the empty option
        "CA": "Canada",
        "US": "United States",
        "DE": "Germany",
        "AU": "Australia",
        "FR": "France",
        "AT": "Austria",
        "CH": "Switzerland",
        "GB": "United Kingdom"
    }

    selected_country = st.selectbox(
        "Select a Country",
        countries,
        format_func=lambda x: country_labels[x],
        key="country_select",
        index=0  # Set default selection to the first item (empty string)
    )

    if selected_country != "":
        reports = PromptManager().get_report(selected_country)

        report_options = {f"Report ID: {report[0]} - {report[1]} ": report[3] for report in reports}

        # Create a select box with the report options
        selected_report = st.selectbox("Select a Report", ["Select a report"] + list(report_options.keys()), key="report_select")

        if selected_report != "Select a report":
            # Write the selected report ID and URL
            st.write(f"Selected Report ID: {selected_report.split(' - ')[0]}")
            st.write(f"Selected Report URL: {report_options[selected_report]}")
            
            # Open and write to the file in the specified directory
            report_id = selected_report.split(' - ')[0].split(": ")[1]
            file_path = f"safety-scan-export-20240823-102233/{report_id}.json"
            
            # Replace the report ID with the full link
            report_url = f"https://www.aeroinside.com/safetyscan/view/{report_id}"
            st.write(f"Selected Report website: {report_url}")
    else:
        st.info("Please select a country to view reports.")


def create_prompt_template():
    prompt_template = """
Compare the following texts:
Target Text: {target_text}
Test Text: {test_text}
Analyze these texts and provide a detailed report following these steps:

List all important concepts and their values in the Target Text.
Identify which Target Text concepts are present in the Test Text.
For each shared concept, check if the Test Text value exactly matches the Target Text value.
Calculate:
Completeness Score = (Concepts in Test / Concepts in Target) * 100
Accuracy Score = (Exact value matches / Exact value matches in Target) * 100


Generate a report with this structure:

Completeness Score
[Percentage with brief explanation, put the value find]
Accuracy Score
[Percentage with brief explanation, put the value find]


    """
    return PromptTemplate(
        input_variables=["target_text", "test_text"],
        template=prompt_template
    )

def compare_texts(target_text, test_text):
    llm = OpenAI(temperature=0)
    prompt = create_prompt_template()
    print(prompt)
    chain = RunnableSequence(prompt | llm)
    result = chain.invoke({"target_text": target_text, "test_text": test_text})
    return result

def parse_result(result):
    if "Completeness Score" in result:
        completeness_score = result.split("Completeness Score")[1].split("%")[0].strip() + "%"
    else:
        completeness_score = 'N/A' 
          
    if "Accuracy Score" in result:
        accuracy_score = result.split("Accuracy Score")[1].split("%")[0].strip() + "%"
    else:
        accuracy_score = 'N/A'   

    return completeness_score, accuracy_score

def benchmark_analysis_page():
    st.title("Benchmark Analysis")

    target_text = st.text_area("Enter Target Text", height=200)
    test_text = st.text_area("Enter Test Text", height=200)

    if st.button("Analyze"):
        if target_text and test_text:
            result = compare_texts(target_text, test_text)
            
            
            completeness_score, accuracy_score = parse_result(result)

            st.subheader("Completeness Score")
            st.write(completeness_score)
            st.subheader("Accuracy Score")
            st.write(accuracy_score)
            st.subheader("Analysis Result")
            st.write(result)
      
            st.success("Report analyzed successfully!")
        else:
            st.error("Please enter both target and test texts.")

def main():
    init_db()

    # Create a dictionary of pages
    pages = {
        "Analyze Report": main_page,
        "Reports list": select_report_page,
        #"Banchmark analysis": benchmark_analysis_page
    }

    # Add sidebar navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()), key="navigation_radio")

    # Display the selected page
    pages[selection]()



if __name__ == "__main__":
    main()