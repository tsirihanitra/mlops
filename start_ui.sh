#!/bin/bash
# Check if streamlit is already running
if pgrep -f "streamlit run src/ui.py" > /dev/null; then
    echo "Streamlit is already running."
    exit 0
fi

echo "Starting Streamlit in the background..."
nohup streamlit run src/ui.py --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &
sleep 2
echo "Streamlit started! You can now access it at http://localhost:8501"
