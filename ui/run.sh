#!/bin/bash
# Run script for Streamlit UI

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run Streamlit
streamlit run main.py

