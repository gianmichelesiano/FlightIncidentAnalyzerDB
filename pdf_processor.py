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


#OPEN_AI_MODEL = os.getenv('OPEN_AI_MODEL')

# deve prendere il valore definito nel menu a tendina st.sidebar.selectbox("Select LLM Model", ["gpt-4o-2024-08-06", "gpt-3.5-turbo-16k"])
# e usarlo come variabile OPEN_AI_MODEL




logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_aircraft_report_model(prompts):
    fields = {key: (str, Field(description=value)) for key, value in prompts.items()}
    return create_model("AircraftReport", **fields)

@lru_cache(maxsize=100)
def extract_chunk(chunk: str, AircraftReport, selected_model) -> BaseModel:
    OPEN_AI_MODEL = selected_model
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

    llm = ChatOpenAI(temperature=0, model=OPEN_AI_MODEL).with_structured_output(AircraftReport)
    extraction_chain = extraction_prompt | llm

    try:
        return extraction_chain.invoke({"text": chunk})
    except Exception as e:
        logging.error(f"Error extracting information from chunk: {e}")
        return AircraftReport()

def process_pdf(uploaded_file, prompts, selected_model):
    print(f"Selected model: {selected_model}")
    start = time.time()
    logging.info(f"Starting extraction from uploaded PDF")

    AircraftReport = create_aircraft_report_model(prompts)

    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader("temp.pdf")
    pages = loader.load_and_split()

    text_splitter = CharacterTextSplitter(chunk_size=15000, chunk_overlap=500)
    texts = text_splitter.split_documents(pages)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_reports = list(executor.map(lambda chunk: extract_chunk(chunk.page_content, AircraftReport, selected_model), texts))

    final_report_dict = {}
    for field in prompts.keys():
        # Use a set to collect unique values
        unique_values = set()
        for report in all_reports:
            value = getattr(report, field)
            if value:  # Only add non-empty values
                # Split the value into sentences and add each sentence
                sentences = value.split('. ')
                unique_values.update(sentence.strip() for sentence in sentences if sentence.strip())
        
        # Join unique sentences back together
        final_report_dict[field] = '. '.join(unique_values)

    final_report = AircraftReport(**final_report_dict)

    end = time.time()
    logging.info(f"Extraction completed in {end - start:.2f} seconds")

    os.remove("temp.pdf")
    return final_report