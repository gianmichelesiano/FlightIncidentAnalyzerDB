import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, create_model
from langchain_openai import ChatOpenAI
import time
import concurrent.futures
import logging
from functools import lru_cache
#from langchain_ollama.llms import OllamaLLM


#OPEN_AI_MODEL = os.getenv('OPEN_AI_MODEL')

# deve prendere il valore definito nel menu a tendina st.sidebar.selectbox("Select LLM Model", ["gpt-4o-2024-08-06", "gpt-3.5-turbo-16k"])
# e usarlo come variabile OPEN_AI_MODEL




logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_aircraft_report_model(prompts):
    fields = {key: (str, Field(description=value)) for key, value in prompts.items()}
    return create_model("AircraftReport", **fields)



def format_and_deduplicate_report(report_text, model):
    # Convert the report dictionary to a structured prompt for the AI

    print(f"Formatted report: {report_text}")
    prompt = (
        "Please process the following content as follows:\n"
        "1. Remove any duplicate entries to ensure all information is unique.\n"
        "2. If the content can be organized chronologically (such as events with dates), "
        "arrange it from the earliest to the latest.\n"
        "3. Format the entire content in Markdown, using appropriate headings, lists, or tables "
        "for clarity and readability.\n\n"
        f"{report_text}\n\n"
        "### Processed Output in Markdown format, not incluede Markdown delimiters, use level 4 for title:"
    )
    # Call the OpenAI API
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    response = llm(prompt)
    return response.content

@lru_cache(maxsize=100)
def extract_chunk(chunk: str, AircraftReport, selected_model) -> BaseModel:
    
    extraction_prompt_template = """
    Extract the following information from the given text:
    Text: {{text}}

    If any information is not available, leave it blank.
    If the information is not in English, translate it to English.
    Provide the output as a structured object with the following fields:
    {fields}
    
    """
    fields_str = "\n".join([f"- {key}: {value}" for key, value in AircraftReport.__fields__.items()])
    extraction_prompt = ChatPromptTemplate.from_template(
        extraction_prompt_template.format(fields=fields_str)
    )

    if selected_model in ["gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-mini"]:
        print("open_ai")
        OPEN_AI_MODEL = selected_model
        llm = ChatOpenAI(temperature=0, model=OPEN_AI_MODEL).with_structured_output(AircraftReport)
    else:
        print("ollama")
        #llm = OllamaLLM(model=selected_model)
        
    extraction_chain = extraction_prompt | llm

    try:
        return extraction_chain.invoke({"text": chunk})
    except Exception as e:
        logging.error(f"Error extracting information from chunk: {e}")
        return AircraftReport()

def process_pdf(uploaded_file, prompts, selected_model):
    start = time.time()
    logging.info(f"Starting extraction from uploaded PDF")
    AircraftReport = create_aircraft_report_model(prompts)


    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader("temp.pdf")
    pages = loader.load_and_split()

    text_splitter = CharacterTextSplitter(chunk_size=15000, chunk_overlap=200)
    texts = text_splitter.split_documents(pages)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_reports = list(executor.map(lambda chunk: extract_chunk(chunk.page_content, AircraftReport, selected_model), texts))
    final_report_dict = {}
    for field in prompts.keys():
        # Use a set to collect unique values
        unique_values = set()
        for report in all_reports:
            value = getattr(report, field, None)
            if isinstance(value, str):
                # Split the value into sentences and add unique sentences to the set
                unique_values.update(sentence.strip() for sentence in value.split('. ') if sentence.strip())
        
        # Join unique sentences back together
        final_report_dict[field] = '. '.join(unique_values)

    final_report = AircraftReport(**final_report_dict)
    end = time.time()
    logging.info(f"Extraction completed in {end - start:.2f} seconds")

    #os.remove("temp.pdf")
    return final_report