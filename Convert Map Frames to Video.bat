@echo on

:: Script python map_video_generator.py
:: Install Requirements.txt
pip install -r requirements.txt

set script_path=map_video_generator.py -y

python %script_path%

pause