import os
import sys
import shutil
# import subprocess
import win32com.client

main_shortcut_name = "Generar Videos"
test_shortcut_name = "TEST - Generar Videos de prueba"

def main():
  # Crear los accesos directos
  exe_abs_path = ''
  for file in os.listdir():
    file_name, ext = os.path.splitext(file)
    if ext == '.exe':
      exe_abs_path = os.path.abspath(file)

  # En vez de esconder archivos, mueve todo a la carpeta _internal para que el antivirus no se queje
  internal_folder = "./_internal"
  # No funca:
  # shutil.move(exe_abs_path, internal_folder)
  # exe_abs_path = os.path.abspath(os.path.join(internal_folder, os.path.basename(exe_abs_path)))
  
  
	# Acceso Directo
  shortcut_file = f"{main_shortcut_name}.lnk"
  arguments = "-y"

  shell = win32com.client.Dispatch("WScript.Shell")
  shortcut = shell.CreateShortcut(shortcut_file)
  shortcut.TargetPath = exe_abs_path
  shortcut.Arguments = arguments
  shortcut.WorkingDirectory = os.path.dirname(__file__)
  shortcut.IconLocation = exe_abs_path
  shortcut.Save()

  # TEST
  test_shortcut_file = f"{test_shortcut_name}.lnk"
  test_arguments = "-ty"

  shell = win32com.client.Dispatch("WScript.Shell")
  test_shortcut = shell.CreateShortcut(test_shortcut_file)
  test_shortcut.TargetPath = exe_abs_path
  test_shortcut.Arguments = test_arguments
  test_shortcut.WorkingDirectory = os.path.dirname(__file__)
  test_shortcut.IconLocation = exe_abs_path
  test_shortcut.Save()
  
  from colorama import Fore
  print(f"{Fore.GREEN}Creados Accesos Directos:{Fore.RESET}")
  print(f"\t{shortcut_file} => {os.path.basename(exe_abs_path)} {arguments}")
  print(f"\t{test_shortcut_file} => {os.path.basename(exe_abs_path)} {test_arguments}")
  
  
  # Escondo este script
  if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Inside a pyInstaller bundle
    shutil.move(sys.executable, internal_folder)
  else:
    # Inside a normal python script
    shutil.move(__file__, internal_folder)
  
  # Esconde el .exe
  # subprocess.call(['attrib', '+H', exe_abs_path])
  
  # # Y me escondo yo también jiji
  # subprocess.call(['attrib', '+H', __file__])
  
  # # Y esconde la carpeta _internal de paso
  # subprocess.call(['attrib', '+H', internal_folder])
  
  
  print()
  input("Pulsa cualquier tecla para cerrar...")


if __name__ == "__main__":
  main()