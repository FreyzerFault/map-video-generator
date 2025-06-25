import subprocess
import pkg_resources
import sys
from src.utils.print_utils import print, print_emphasis, print_error, print_warning

requirements_file = "requirements.txt"
spec_file = "Map Video Generator.spec"

def check_and_install_requirements():
  print()
  print_emphasis("=============================== Comprobando requisitos ===============================")
  print()
  
  try:
		# Carga los requerimientos desde requirements.txt
    with open(requirements_file) as f:
      required = f.read().splitlines()
		
		# Revisa qué paquetes faltan
    missing = []
    for req in required:
      try:
        pkg_resources.require(req)
      except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
        missing.append(req)

		# Si falta alguno, instala todos
    if missing:
      print_warning("Faltan algunos requisitos, instalando:", ", ".join(missing))
      # pip install -r requirements.txt
      subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    else:
      print_emphasis("✨ Todo joya mi ciela ✨\n")
  except FileNotFoundError:
    print_error(f"ERROR: No se encontró {requirements_file}", )
    sys.exit(1)
  
  print()



def install_bundle():
  print()
  print_emphasis(f"======================= Instalando el bundle con {spec_file} =======================")
  print()

	# pyinstaller "./Map Video Generator.spec" -y
  subprocess.run(['pyinstaller', spec_file, '-y'])

check_and_install_requirements()

install_bundle()
