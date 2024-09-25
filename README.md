PDF Flight Report Analyzer

The "PDF Flight Report Analyzer" application utilizes advanced LLM models and the langchain framework to thoroughly analyze PDF files containing aircraft data and generate comprehensive reports.

## Requirements

- Python 3.7 or later (tested Python 3.12.6)
- pip (Python package manager)

## Installation

1. Clone the repository or download the project files.
  ```
  git clone https://github.com/gianmichelesiano/FlightIncidentAnalyzerDB
  ```

2. Navigate to the project directory:
   ```
   cd FlightIncidentAnalyzerDB
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project's root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the application by running the main file:
   ```
   streamlit run .\app.py  
   ```

2. The user interface will open in your default web browser on port 8501
   ```
   Local URL: http://localhost:8501
   ```
