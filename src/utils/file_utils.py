import os
import yaml
from utils.print_utils import print_error

def load_config(path) -> dict:
  if path_not_found(path):
    return
  
  # Cargar las variables desde el archivo config.json
  with open(path, 'r') as file:
    return yaml.load(file, Loader=yaml.FullLoader)

def path_not_found(path):
  if not os.path.exists(path):
    print_error(f"No se encuentra la ruta {path}.")
    return True
  return False

def get_first_file(folder_path) -> str | None:
  for file in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file)
    if not os.path.isdir(file_path):
      return file_path
  
  return None
