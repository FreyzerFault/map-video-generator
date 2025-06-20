import os
from colorama import init, Fore, Back, Style
import yaml
import asyncio

init(convert=True)



#region ====================================== PRINT UTILS ======================================

class TextLogWriter:
    def __init__(self, app, log_id="log"):
        self.app = app
        self.log_id = log_id

    def write(self, message):
      try:
        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(asyncio.create_task, self._send_to_log(message))
      except RuntimeError:
        # Si aún no hay loop activo (raro), simplemente ignora o usa fallback
        pass

    def flush(self):
        pass  # requerido por sys.stdout, pero no hace nada

    async def _send_to_log(self, message):
        try:
            log = self.app.query_one(f"#{self.log_id}")
            log.write(message.rstrip())
        except Exception as e:
            pass  # evita errores al cerrar


class ConsoleApp():
  
  def __init__(self, verbose = False, yes_to_all = True, run_callback = None):
    
    self.verbose = verbose
    self.yes_to_all = yes_to_all
    
    self.run_callback = run_callback
  
  
  def print(self, message = "", color: str = Fore.WHITE):
    print(f"{color}{message}{Style.RESET_ALL}")
  
  def print_error(self, message = ""):
    self.print(message, Fore.RED)
  
  def print_warning(self, message = ""):
    self.print(message, Fore.YELLOW)
  
  def print_emphasis(self, message = ""):
    self.print(message, Fore.CYAN)
  
  def print_info(self, message = ""):
    self.print(message, Fore.WHITE)
  
  def print_verbose_info(self, message = ""):
    if self.verbose:
      self.print(message, Fore.LIGHTBLACK_EX)
  
  
  def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 0, length = 100, fill = '█', printEnd = "\r", show_percent: bool = True):
    """
    Call in a loop to create terminal progress bar
    @params:
      iteration   - Required  : current iteration (Int)
      total       - Required  : total iterations (Int)
      prefix      - Optional  : prefix string (Str)
      suffix      - Optional  : suffix string (Str)
      decimals    - Optional  : positive number of decimals in percent complete (Int)
      length      - Optional  : character length of bar (Int)
      fill        - Optional  : bar fill character (Str)
      printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{Fore.YELLOW if iteration < total else Fore.GREEN}{prefix} |{Back.LIGHTBLACK_EX}{bar}{Back.RESET}| {f"{percent}%" if show_percent else f"{iteration}/{total}"} {suffix}{Style.RESET_ALL} {printEnd}')
    # Print New Line on Complete
    if iteration == total: 
      print()
  
  
  def print_file_list(self, files: list[str], title: str = '📂 Files'):
    self.print_emphasis(f"{title} ({len(files)}):")
    self.print()
    self.print_info(f"\t{"\n\t".join(map(lambda file: f"- {file}", files))}")

# SINGLETON: use this over the app
console = ConsoleApp()

#endregion



#region ====================================== FILE UTILS ======================================

def load_config(path) -> dict:
  if path_not_found(path):
    return
  
  # Cargar las variables desde el archivo config.json
  with open(path, 'r') as file:
    return yaml.load(file, Loader=yaml.FullLoader)

def path_not_found(path):
  if not os.path.exists(path):
    console.print_error(f"No se encuentra la ruta {path}.")
    return True
  return False

def get_first_file(folder_path) -> str | None:
  for file in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file)
    if not os.path.isdir(file_path):
      return file_path
  
  return None

#endregion