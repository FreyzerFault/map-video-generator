import os, subprocess, json
from PIL import Image
from colorama import Fore, Style
from datetime import datetime

def main():
  # LOAD CONFIG
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
  debug = config['debug']
  
  # Realtime date:
  # Si es True, se calculará la fecha y hora de cada frame extrapolando de la fecha inicial.
  # Si es False, se mostrará la fecha inicial y un contador de días desde el inicio.
  # (Recomendado no mostrar la fecha a tiempo real si el intervalo de tiempo pasa por más de un mes.)
  realtime_date = config['realtime_date']
  
  # CHECK PATHS
  if not exists_path(os.path.dirname(input_path)): return
  if not exists_path(os.path.dirname(output_path)): return
  
  # INITIAL DATE
  initial_time = datetime(init_year, init_month, init_day, init_hour, init_min)
  
  print(f"{Fore.CYAN}Fecha y hora inicial: {initial_time}{Style.RESET_ALL}")
  print(f"{Fore.CYAN}Generando frames cada {min_interval} minutos a {framerate} fps{Style.RESET_ALL}")

  # SHOW TIMER IF MIN_INTERVAL IS LESS THAN 1440 (1 DAY)
  show_timer = min_interval < 1440

  # DATE & TIME
  
  total_mins = f"floor({init_min} + (n*{min_interval}))"
  total_hours = f"floor({init_hour} + {total_mins}/60)"
  total_days = f"({total_hours}/24)"
  
  min =   f"mod({total_mins},60)"
  hour =  f"mod({total_hours},24)"
  
  # * NOTA: El cálculo de la fecha es un poco más complicado, ya que día y més son interdependientes.
  # * En caso de pasar por varios meses, se recomienda desactivar la fecha en tiempo real en el config.json.
  # El cálculo del día es dependiente de los dias que tiene el mes, y el mes dependiente de los dias que han pasado,
  # por lo que dia y mes son interdependientes, no se puede calcular a partir de frame.
  # Se podría acumular los días y reiniciar el contador al llegar al día 31 o 32,
  # pero dado las limitaciones de ffmpeg, no es posible acumular valores, debe estar todo calculado en 1 expresión.
  
  
  day = f"(floor({init_day} + {total_days}) - 1)" # Se resta 1 para que el día 1 sea 0 para hacer los cálculos más simples
  
  # Para meses del 1 al 7, los meses impares tienen 31 días y los pares 30, y para los meses del 8 al 12 es al revés.
  days_of_month = f"(31-mod({init_month} + floor({day}/(31 - lt({init_month},8))),2))"
  
  month = f"floor({init_month} + floor({day}/{days_of_month}))"

  day =   f"1+mod({day},{days_of_month})"
  month = f"1+mod({month}-1,12)"
  year = str(init_year)


  # TEXT FILTER EXPRESSIONS
  # Dentro del filtro de texto se pueden usar expresiones dinámicas
  # como %{e:expresion} y %{eif:expresion:formato:precision} para cálculos dinámicos
  # usando como variable el frame actual (n).
  def func(name, args):
    return f"%{'{'}{name}\\:{"\\:".join(args)}{'}'}"
  
  # Construye una expresión con formato de número entero
  def int_text(exp, digits = 2):
    return func("eif", [str(exp), 'd', str(digits)])
  
  init_date_text = f"{int_text(init_day)}-{int_text(init_month)}-{int_text(init_year)}"
  realtime_date_text = f"{int_text(day)}-{int_text(month)}-{int_text(year)}"
  timer_text = f"{int_text(hour)}\\:{int_text(min)}"
  total_days_text = f" Día {func('eif', [total_days, 'd', '2'])}"
  
  
  # TEXT MEASURES
  margin = 10
  line_height = 40
  date_width = 160
  timer_width = 60
  total_days_width = 100
  
  image_size = read_image_size(os.path.dirname(input_path))
  width = image_size[0] # Image size
  height = image_size[1] # Image size
  
  
  # TEXT FILTER
  text_filter = (
          # TITLE
          (f"drawtext=text='{subtitle}':x={margin}:y={margin}:fontsize=24:fontcolor=white")
      )

  # Se pueden concatenar varias expresiones de drawtext para mostrar varios textos en la misma imagen.
  if realtime_date: # Fecha de cada frame
    text_filter += (
      # DATE
      (f",drawtext=text='{realtime_date_text} {timer_text if show_timer else ""}'")
      + (f":x={width - margin - date_width - (timer_width if show_timer else 0)}:y={margin}:fontsize=24:fontcolor=white")
    )
  else: # Muestra la fecha inicial y un timer con un contador de días que pasaron
    text_filter += (
      # INIT DATE
      (f",drawtext=text='Desde el {init_date_text}':x={margin}:y={margin + line_height}:fontsize=24:fontcolor=white")
      # TIMER
      + (f",drawtext=text='")
        + (f"{total_days_text} {timer_text if show_timer else ''}")
      + ("'")
      + (f":x={width - margin - total_days_width - timer_width if show_timer else 0}:y={margin}:fontsize=24:fontcolor=white")
    )
    
  # DEBUGGING
  if debug:
    text_filter += (
      # FRAMES
      (f",drawtext=text='Frame\\: %{'{'}n{'}'}':x={margin}:y={height / 2 - line_height / 2}")
      + (f":fontsize=16:fontcolor=red:shadowcolor=black:shadowx=1:shadowy=1")
    )

  # FFMPEG COMMAND
  command = [
      'ffmpeg',
      '-framerate', str(framerate),
      '-i', input_path,
      '-vf',
      text_filter,
      output_path
  ]
  
  print (f"{Fore.CYAN}Comando: {' '.join(command)}{Style.RESET_ALL}")
  
  # return
  
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