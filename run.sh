#!/bin/bash

# Run Streamlit app in the background
streamlit run Hotel_Analyst.py &

# Get the PID of the Streamlit process
STREAMLIT_PID=$!

echo "Streamlit app is running with PID: $STREAMLIT_PID"

# Run the FastAPI app by executing crawler.py directly
python crawler.py

# Optionally, wait for FastAPI to complete before killing Streamlit (uncomment if needed)
# wait $!
# kill $STREAMLIT_PID
