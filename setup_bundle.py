import yaml
import os
import shutil

from src.utils.print_utils import print_emphasis, print_file_list

config_file_path = "./config.yaml"
readme_file_path = "./README.md"

setup_script_file = "RUN ME.exe"
setup_script_path = os.path.join(f"./dist/{setup_script_file}")

def insert_assets(build_folder_path: str):
  """
  Inserta todos los assets necesarios junto al .exe.
  Crea además las carpetas donde deberán ir los datos
  """
  empty_dirs = []
  copy_dir_paths = []
  
  with open(config_file_path, 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    
    # Carpetas vacías para los datos
    empty_dirs = [
			config["input_frames_folder_path"],
			config["output_videos_folder_path"],
    ]
    
    # Carpetas con assets a incluir
    copy_dir_paths = [
			config["legend_images_folder_path"],
			"./test",
		]
  
  for empty_dir in empty_dirs:
    empty_dir = os.path.join(build_folder_path, empty_dir)
    os.mkdir(empty_dir)
  
  for path in copy_dir_paths:
    dest_path = os.path.join(build_folder_path, path)
    shutil.copytree(path, dest_path)
  
  # Archivos sueltos en la raíz
  shutil.copy(config_file_path, os.path.join(build_folder_path, config_file_path))
  shutil.copy(readme_file_path, os.path.join(build_folder_path, readme_file_path))
  
  # Mover el script para crear los shortcuts.
  # Lo he convertido a .exe para mejor usabilidad.
  # Está en ./dist/RUN ME.exe
  shutil.copy(setup_script_path, os.path.join(build_folder_path, setup_script_file))
  print()
  print_emphasis()
  print_file_list([*empty_dirs, *copy_dir_paths, setup_script_file], f"Assets iniciales cargados en el bundle {build_folder_path}:")
  print()


def compress_bundle(bundle_path, zip_name):
  """ Comprime todo en un zip """
  print()
  print_emphasis(f"Comprimiendo carpeta {os.path.basename(bundle_path)} en un zip: {zip_name}")
  print()
  shutil.make_archive(os.path.join(os.path.dirname(bundle_path), zip_name), 'zip', os.path.dirname(bundle_path), os.path.basename(bundle_path))


def setup_bundle_folder(program_name: str, version = '1.0'):
  """
  Prepara la carpeta del bundle para su uso, insertando los assets necesarios.
  Y la comprime para su publicación.
  """
  build_folder_path = os.path.join("./dist/", program_name)
  
  insert_assets(build_folder_path)
  compress_bundle(build_folder_path, f"{program_name} {version}")