# File: prompt_manager.py
import streamlit as st
from database import get_db_connection, init_db

class PromptManager:
    def __init__(self):
        init_db()

    def add_prompt(self, key, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO prompts (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()

    def remove_prompt(self, key):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prompts WHERE key = ?', (key,))
        conn.commit()
        conn.close()
        
    def update_prompt(self, key, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE prompts SET value = ? WHERE key = ?', (value, key))
        conn.commit()
        conn.close()

    def get_prompts(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM prompts')
        prompts = {row['key']: row['value'] for row in cursor.fetchall() if row['key']}
        conn.close()
        return prompts
    
    def get_report(self, selected_country):
        print(f"Getting report for country: {selected_country}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT json_id, country, report_type, url FROM report WHERE country = ?', (selected_country,))
        reports = cursor.fetchall()
        conn.close()
        return reports

    def render_prompt_management(self):
        st.header("Manage Prompts")
        
        # Add new prompt
        with st.expander("Add New Prompt"):
            new_prompt_key = st.text_input("New Prompt Key")
            new_prompt_value = st.text_area("New Prompt Value")
            if st.button("Add Prompt"):
                if new_prompt_key and new_prompt_value:
                    self.add_prompt(new_prompt_key, new_prompt_value)
                    st.success(f"Added new prompt: {new_prompt_key}")
                else:
                    st.warning("Please enter both a key and a value for the new prompt.")
        
        # Display and manage existing prompts
        st.subheader("Current Prompts")
        prompts = self.get_prompts()
        for key, value in prompts.items():
            col1, col2, col3, col4 = st.columns([2, 5, 1, 1])
            with col1:
                st.write(key)
            with col2:
                new_value = st.text_area(
                    label=f"Edit prompt for {key}",  # Provide a non-empty label
                    value=value,
                    key=f"prompt_{key}",
                    height=100,
                    label_visibility="collapsed"  # Hide the label visually
                )
            with col3:
                if st.button("💾", key=f"save_{key}"):
                    self.update_prompt(key, new_value)
            with col4:
                if st.button("🗑️", key=f"delete_{key}"):
                    self.remove_prompt(key)
                    st.experimental_rerun()
    