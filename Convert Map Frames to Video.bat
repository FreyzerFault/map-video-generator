@echo on

:: Script python map_video_generator.py
:: Install Requirements.txt
pip install -r requirements.txt

set script_path=./src/main.py -y

python %script_path%

pause