#!/bin/bash
# Total Battle Chest Tracker Launcher

echo "Starting Total Battle Chest Tracker..."
echo ""

# Check if virtual environment exists
if [ -d "chest_tracker_env" ]; then
    echo "Activating virtual environment..."
    source chest_tracker_env/bin/activate
fi

# Check if dependencies are installed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "Error: PyQt6 not found!"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Run the application
python3 chest_tracker.py

echo ""
echo "Application closed."
