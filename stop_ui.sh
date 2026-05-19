#!/bin/bash
if pgrep -f "streamlit run src/ui.py" > /dev/null; then
    echo "Stopping Streamlit..."
    pkill -f "streamlit run src/ui.py"
    echo "Streamlit stopped."
else
    echo "Streamlit is not running."
fi
