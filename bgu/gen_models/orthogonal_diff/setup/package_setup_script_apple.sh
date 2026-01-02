pip freeze > requirements.txt;
#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv .venv
echo "Activating environment and installing libraries..."
source .venv/bin/activate
pip install -r requirements.txt
echo "Setup complete!"