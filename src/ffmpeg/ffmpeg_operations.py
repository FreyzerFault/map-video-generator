import subprocess
import os
from colorama import Fore, Back
from utils.image_utils import read_image_size
from utils.print_utils import print, print_info, print_verbose_info, print_emphasis, colorize
from utils.file_utils import get_first_file


def execute_command(command: str, verbose = False):
  if verbose:
    print_info("Ejecutando Comando: ")
    print_verbose_info(' '.join(command))
    print()
  
  subprocess.run(command)


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
  
  execute_command(command, verbose)


def overlay_image_on_video(video_path: str, image_path: str, output_video_path: str, x = 0, y = 0, scale = 1.0, yes_to_all = True, verbose = False):
  """
  Superpone una imagen en un vídeo en las coordenadas (x, y) especificadas.
  """
  
  print()
  image_file_str = f"{Back.WHITE}{Fore.BLACK} {os.path.basename(image_path)} {Fore.WHITE}{Back.RESET}"
  video_file_str = f"{Back.WHITE}{Fore.BLACK} {os.path.basename(video_path)} {Fore.WHITE}{Back.RESET}"
  pos_str = f" en ({x},{y})" if x != 0 and y != 0 else ""
  print_emphasis(f"📷  Superponiendo Imagen \n\n\t{image_file_str} sobre {video_file_str}{pos_str}\n")
  print()
  
  # Same Video input - output
  if (video_path == output_video_path
    and not yes_to_all
    and input(colorize(f"El vídeo de salida {video_path} ya existe. ¿Deseas sobrescribirlo con el nuevo con la imagen superpuesta? (s/n):", 'yellow'))
    == "n"):
    print("Superposición de imagen cancelada", 'red')
    return output_video_path
  
  # Copy video temporally if same name
  delete_afterwards = False
  if (video_path == output_video_path):
    video_pair = os.path.splitext(os.path.basename(video_path))
    video_name = video_pair[0]
    video_ext = video_pair[1]
    tmp_video = video_name + '_tmp' + video_ext
    tmp_video_path = os.path.join(os.path.dirname(video_path), tmp_video)
    os.rename(video_path, tmp_video_path)
    video_path = tmp_video_path
    delete_afterwards = True
  
  # Do the thing
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
  execute_command(command, verbose)
  
  # Remove the input video if input and output has the same name
  if delete_afterwards:
    os.remove(video_path)
  
  return output_video_path