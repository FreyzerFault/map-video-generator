import os, subprocess, json
from PIL import Image
from colorama import Fore, Style
from datetime import datetime

def main():
  config = load_config('./config.json')

  input_path = config['input_path']
  output_path = config['output_path']
  framerate = config['framerate']
  init_year = config['init_year']
  init_month = config['init_month']
  init_day = config['init_day']
  init_hour = config['init_hour']
  init_min = config['init_min']
  min_interval = config['min_interval']
  subtitle = config['video_subtitle']
  
  # Verifica si existen las rutas
  if not exists_path(os.path.dirname(input_path)): return
  if not exists_path(os.path.dirname(output_path)): return
  
  # Image size
  width = read_image_size('./Belen Agosto - 246064')[0]
  
  # Calcula la fecha y hora inicial
  initial_time = datetime(init_year, init_month, init_day, init_hour, init_min)
  print(f"{Fore.CYAN}Fecha y hora inicial: {initial_time}{Style.RESET_ALL}")
  print(f"{Fore.CYAN}Generando frames cada {min_interval} minutos a {framerate} fps{Style.RESET_ALL}")

  # Genera el comando ffmpeg con drawtext para calcular la fecha y hora dinámicamente
  min = f"%{'{'}eif\\:{init_min} + mod(n*{min_interval},60)\\:d\\:2{'}'}"
  hour = f"%{'{'}eif\\:{init_hour} + mod((n*{min_interval})/60,24)\\:d\\:2{'}'}"
  day = f"%{'{'}eif\\:{init_day} + mod((n*{min_interval})/60/24,31)\\:d\\:2{'}'}"
  month = f"%{'{'}eif\\:{init_month} + (n*{min_interval})/60/24/31\\:d\\:2{'}'}"
  year = init_year

  command = [
      'ffmpeg',
      '-framerate', str(framerate),
      '-i', input_path,
      '-vf', (
          f"drawtext=text='{day}-{month}-{year} {hour}\\:{min}'"
          f":x={width - 220}:y=10:fontsize=24:fontcolor=white"
          f",drawtext=text='{subtitle}':x=10:y=10:fontsize=24:fontcolor=white"
      ),
      output_path
  ]
  
  subprocess.run(command)

def load_config(json_path) -> dict:
  if not exists_path(json_path): return
  
  # Cargar las variables desde el archivo config.json
  with open(json_path, 'r') as file:
    return json.load(file)

def exists_path(path):
  if not os.path.exists(path):
    print(f"No se encuentra la ruta {path}.")
    return False
  return True

def read_image_size(folder_path):
  # Obtiene el tamaño de la 1º imagen en la carpeta
  image = os.listdir(folder_path)[0]
  print(f"Imagen: {image}")
  image_path = os.path.join(folder_path, image)
  with Image.open(image_path) as img:
    width, height = img.size
    
  return (width, height)

if __name__ == "__main__":
  main()