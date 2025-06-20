import subprocess
import os
from colorama import Fore, Back
from image_utils import read_image_size
from utils import console, get_first_file


def frames_to_video(input_frames_path: str, output_video_path: str, framerate: int, text_filter: str = "", verbose: bool = False):
  
  video_size = read_image_size(get_first_file(os.path.dirname(input_frames_path)))
  video_width = video_size[0]
  video_height = video_size[1]
  
  if video_width % 2 != 0 or video_height % 2 != 0:
    # print_warning(f"El tamaño del vídeo {video_width}x{video_height} debe ser par.")
    
    if video_width % 2 != 0:
      video_width = video_width - 1
    if video_height % 2 != 0:
      video_height = video_height - 1
      
    # print_info(f"Ajustando vídeo a {video_width}x{video_height}.")
  
  text_filter = f"scale={video_width}:{video_height},{text_filter}"
  
  # FFMPEG COMMAND
  command = [
      'ffmpeg',
      '-framerate', str(framerate),
      '-i', input_frames_path,
      '-vf', text_filter,
      '-y',
      '-loglevel', 'info' if verbose else 'warning', # Output verbosity
      output_video_path
  ]
  
  if verbose:
    console.print()
    console.print_info("Ejecutando Comando: ")
    console.print_verbose_info(' '.join(command))
    console.print()
  
  subprocess.run(command)


def overlay_image_on_video(video_path: str, image_path: str, output_video_path: str, x: int = 0, y: int = 0, scale: float = 1.0, verbose: bool = False):
  """
  Superpone una imagen en un vídeo en las coordenadas (x, y) especificadas.
  """
  command = [
      'ffmpeg',
      '-i', video_path,
      '-i', image_path,
      '-filter_complex', f'overlay={x}:{y}',
      '-c:a', 'copy',
      '-y',
      '-loglevel', 'info' if verbose else 'warning', # Reduce output verbosity
      output_video_path
  ]
  console.print()
  image_file_str = f"{Back.WHITE}{Fore.BLACK} {os.path.basename(image_path)} {Fore.WHITE}{Back.RESET}"
  video_file_str = f"{Back.WHITE}{Fore.BLACK} {os.path.basename(video_path)} {Fore.WHITE}{Back.RESET}"
  pos_str = f" en ({x},{y})" if x != 0 and y != 0 else ""
  console.print_emphasis(f"🗺️  Colocando Leyenda 🧭\n\n\t{image_file_str} sobre {video_file_str}{pos_str}\n\n\tResultado: {output_video_path}")
  console.print()
  if verbose:
    console.print_info("Ejecutando Comando: ")
    console.print_verbose_info(' '.join(command))
    console.print()
  
  subprocess.run(command)
