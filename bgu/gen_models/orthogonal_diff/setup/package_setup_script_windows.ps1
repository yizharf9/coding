echo off ; 
echo Creating virtual environment... ;
python -m venv .venv ;
echo Activating environment and installing libraries... ; 
.venv\Scripts\activate ;
pip install -r requirements.txt ;
echo Setup complete! ;
