from __future__ import annotations
import argparse
import sys
from utils.print_utils import print, print_emphasis, print_error, print_file_list, print_progressBar
from utils.file_utils import load_config, path_not_found

from ffmpeg.video_generator import VideoGenerator
from ffmpeg.text_filter import TextStyle


#region ============================================= ARGUMENTS =========================================

def parse_args(args):
    parser = argparse.ArgumentParser(
    description="Convertidor de Frames a Video con Timer y Leyenda incluido. Configura todo en el config.json"
    )
    parser.add_argument(
      "-t",
      "--test",
      action="store_true",
      help="Ejecuta el script en modo test, usando unos frames de prueba.",
    )
    parser.add_argument(
      "-d",
      "--debug",
      action="store_true",
      help="Ejecuta el script en modo debug, para mostrar más información en un panel en el vídeo renderizado.",
    )
    parser.add_argument(
      "-y",
      "--yes_to_all",
      action="store_true",
      help='Responde "s" a todas las preguntas de confirmación, como sobrescribir archivos existentes.',
    )
    parser.add_argument(
      "-v",
      "--verbose",
      action="store_true",
      help="Muestra más detalles en la salida de los comandos ejecutados.",
    )
    return parser.parse_args(args)

#endregion


#region ====================================== MAIN ======================================

def main(args=None):
  
  if args is None:
    args = sys.argv[1:]
  
  #region PARSE ARGUMENTS
  args = parse_args(args)
  test_mode = args.test
  debug_mode = args.debug
  yes_to_all = args.yes_to_all
  verbose = args.verbose
  #endregion


  #region LOAD CONFIG
  config = load_config("./config.yaml" if not test_mode else "./test/config.yaml")

  if not config:
    return

  # PATHS
  input_frames_folder_path = config["input_frames_folder_path"]
  output_videos_folder_path = config["output_videos_folder_path"]
  overlay_images_folder_path = config["overlay_images_folder_path"]

  if path_not_found(input_frames_folder_path) or path_not_found(output_videos_folder_path):
    return

  # TEXT STYLE
  title_text_style = TextStyle.from_config(config["title_text_style"])
  timer_text_style = TextStyle.from_config(config["timer_text_style"])

  margin = (config["margin"]["x"], config["margin"]["y"])

  char_width_by_font = config["char_width_by_font"]
  line_height_by_font = config["line_height_by_font"]


  # Inicialización de los Videos a partir del archivo de configuración
  video_gens = [
    VideoGenerator.from_config(
      video_config,
      input_frames_folder_path,
      output_videos_folder_path,
      overlay_images_folder_path,
      title_text_style,
      timer_text_style
    )
    for video_config in config["videos"]]
  
  #endregion
  
  
  videos = []

  # Initial call to print 0% progress
  progress_bar = {
    "total": len(video_gens),
    "prefix": "🎥 Video Generation:",
    "suffix": "Videos 🎬",
    "length": len(video_gens) * 5,
    "print_end": "\n",
    "show_percentage": False
  }

  # Iterate each VIDEO
  for i, video_gen in enumerate(video_gens):
    print()
    print_emphasis(f"{'=' * 40} 🎞️  {video_gen.name} 🕒 {'=' * 40}")
    print()
    print_progressBar(
      i,
      progress_bar["total"],
      prefix=progress_bar["prefix"],
      suffix=progress_bar["suffix"],
      length=progress_bar["length"],
      printEnd=progress_bar["print_end"],
      show_percent=progress_bar["show_percentage"],
    )
    print()
    
    
    videos.append(video_gen.frames_to_video(yes_to_all, debug_mode, verbose, margin, char_width_by_font, line_height_by_font))


  print()
  print_progressBar(
    progress_bar["total"],
    progress_bar["total"],
    prefix="✨ COMPLETED ✨",
    suffix=progress_bar["suffix"],
    length=progress_bar["length"],
    show_percent=progress_bar["show_percentage"],
  )
  print()
  print_file_list(videos, '🎬 Videos')
  print()
  
  input("Pulsa cualquier tecla para cerrar...")

#endregion


if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print()
    print_error(f"ERROR: {e}")
    print()
    input("Pulsa cualquier tecla para cerrar...")