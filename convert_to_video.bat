@echo off

:: Script python convert_to_video.py
:: Install Requirements.txt
pip install -r requirements.txt

set script_path=convert_to_video.py

python %script_path%

pause