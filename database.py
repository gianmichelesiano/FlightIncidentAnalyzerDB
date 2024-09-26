import sqlite3
import os
import csv

DB_NAME = 'prompts.db'
CSV_FILE_PATH = './safety_data_final_report.csv'

def check_csv_file_exists(file_path):
    if not os.path.isfile(file_path):
        #print(f"Error:  file CSV '{file_path}' not exist.")
        return False

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create prompts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL
    )
    ''')
    
    # Insert default prompts if the table is empty
    cursor.execute('SELECT COUNT(*) FROM prompts')
    if cursor.fetchone()[0] == 0:
        default_prompts = [
            ("type_of_flight", 'Describe the type and nature of the flight involved in the incident'),
            ("position_of_pilot_copilot", 'Identify the position of the pilot and co-pilot during the flight'),
            ("phases_of_flight", 'Detail the phases of flight covered in the report, noting any events'),
            ("events_during_phases", 'Describe events occurring during each phase of flight and who observed them'),
            ("actions_taken_by_crew", 'Outline the actions taken by the crew for each flight phase in response to events'),
            ("event_causing_accident", 'Identify the event that occurred during flight causing the accident'),
            ('aircraft_handling_post_event', 'Describe how the aircraft was handled following the event causing the accident'),
            ('pilot_experience', 'Provide details of the pilot''s experience'),
            ('pilot_medical_license', 'State the medical license details of the pilot'),
            ('mass_and_balance_info', 'Include information on aircraft mass and balance'),
            ('performance_info', 'Summarize performance details of the aircraft'),
            ('operational_info', 'Provide other operational information relevant to the event'),
            ('meteo_info', 'Discuss meteorological conditions related to the incident, including METAR, TAF, weather charts'),
            ('lighting_info', 'Detail the lighting conditions at the time of the incident, such as day, night, dawn, dusk'),
            ('navigation_aids_info', 'Provide information on navigation aids and their status'),
            ('communication_info', 'Describe the communication with air traffic control and other relevant parties'),
            ('aerodrome_info', 'Detail information about the aerodrome/operating site, including location and runway details'),
            ('cvr_data', 'Summarize data collected from the Cockpit Voice Recorder (CVR)'),
            ('fdr_data', 'Include details from the Flight Data Recorder (FDR)'),
            ('other_recording_device_info', 'Provide information from any other recording devices'),
            ('final_position_aircraft', 'Describe the final position and condition of the aircraft, noting any damages'),
            ('causes', 'List the causes of the accident, including failures in aircraft and effects from damages'),
            ('human_aspects', 'Discuss human factors, including medical, pathological, and psychological aspects'),
            ('fire_occurrence', 'State whether a fire occurred and provide details, including causes and damages'),
            ('survivability', 'Describe survivability aspects, including injuries or exits post-accident'),
            ('organization_info', 'Provide insights into the organization and operations involved'),
            ('additional_investigations', 'Outline any further investigations on technical aspects, guidelines, or maintenance info'),
            ('analysis', 'Discuss analysis done, including remarks on events, compliance, technical issues, and weather conditions'),
            ('probable_cause_and_findings', 'Identify the main cause and findings of the investigation, including additional factors'),
            ('safety_recommendations', 'List any safety recommendations suggested by the investigation')
        ]
        cursor.executemany('INSERT INTO prompts (key, value) VALUES (?, ?)', default_prompts)
    
    # Create report table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS report (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        json_id INTEGER,
        country TEXT NOT NULL,
        report_type TEXT NOT NULL,
        url TEXT NOT NULL
    )
    ''')
    
    if  check_csv_file_exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, 'r') as file:
            reader = csv.reader(file)
            report_data = [(int(row[0]), row[1], row[2], row[3]) for row in reader]
            cursor.executemany('INSERT OR IGNORE  INTO report (json_id, country, report_type, url) VALUES (?, ?, ?, ?)', report_data)
        
    conn.commit()
    conn.close()