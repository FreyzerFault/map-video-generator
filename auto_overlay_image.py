import os
import yaml
import ffmpeg
from colorama import Fore, Style

#region ====================================== MAIN ======================================

def main():
  # LOAD CONFIG
  config = load_config('./overlay_images_config.yaml')

  video_path = config['video_path']
  out_video_path = config['out_video_path']
  
  images_data = config['images']
    
  # CHECK PATHS
  if not exists_path(video_path):
    print(f"{Fore.RED}No se encuentra la ruta {video_path}.")
    return
  
  video = ffmpeg.input(video_path)
  images = [ffmpeg.input(image['path']) for image in images_data]
  
  video_width = get_video_width(video_path)
  
  for i in range(1, len(images)):
    image_data = images_data[i]
    
    if not exists_path(image_data['path']):
      print(f"{Fore.RED}No se encuentra la ruta {image_data['path']}.")
      return
    
    print(f"{Fore.CYAN}Colocando imagen {image_data['path']} en el video {video_path} en {image_data['pos']}{Style.RESET_ALL}")  
    
    
    # Escalar overlay a un porcentaje del ancho del video manteniendo aspecto
    images[i] = images[i].filter('scale', f'{video_width}*{image_data['width_scale']}', '-1')
    
    # Calculate X and Y positions for the image
    mX = image_data['margin']['x']
    mY = image_data['margin']['y']
    
    if image_data['pos'] == 'top_left':
      x = mX
      y = mY
    elif image_data['pos'] == 'top_right':
      x = f'W-w-{mX}'
      y = mY
    elif image_data['pos'] == 'bottom_left':
      x = mX
      y = f'H-h-{mY}'
    elif image_data['pos'] == 'bottom_right':
      x = f'W-w-{mX}'
      y = f'H-h-{mY}'
    else:
      print(f"{Fore.RED}Posición de imagen no válida. Debe ser 'top_left', 'top_right', 'bottom_left' o 'bottom_right'.{Style.RESET_ALL}")
      return
    
    video = ffmpeg.overlay(video, images[i], x=x, y=y)
  
  
  video = video.filter('scale', 'trunc(iw/2)*2', 'trunc(ih/2)*2')  # Escala el video a un tamaño par
  
  video.output(out_video_path).run()
  
  # Open in VLC
  # import subprocess
  # subprocess.run(['vlc', out_video_path])


#region ====================================== UTILS ======================================

def load_config(yaml_path) -> dict:
  if not exists_path(yaml_path):
    return
  
  # Cargar las variables desde el archivo config.json
  with open(yaml_path, 'r') as file:
    return yaml.safe_load(file)

def exists_path(path):
  if not os.path.exists(path):
    print(f"No se encuentra la ruta {path}.")
    return False
  return True

def get_video_width(filename):
    probe = ffmpeg.probe(filename)
    video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    return int(video_stream['width'])

#endregion

if __name__ == "__main__":
  main()