from genericpath import isfile
import os
from colorama import init, Fore, Back, Style
import yaml
from tabnanny import verbose

init(convert=True)

#region ====================================== FILE UTILS ======================================

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

#endregion


#region ====================================== DEBUG UTILS ======================================

def print_error(message: str):
  print(f"{Fore.RED}{message}{Style.RESET_ALL}")

def print_warning(message: str):
  print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

def print_emphasis(message: str):
  print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
  
def print_info(message: str):
  print(f"{Fore.WHITE}{message}{Style.RESET_ALL}")

def print_verbose_info(message: str):
  if verbose:
    print(f"{Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}")


# PROGRESS BAR
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 0, length = 100, fill = '█', printEnd = "\r"):
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
    print(f'\r{Fore.YELLOW if iteration < total else Fore.GREEN}{prefix} |{Back.LIGHTBLACK_EX}{bar}{Back.RESET}| {percent}% {suffix}{Style.RESET_ALL}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def print_file_list(files: list[str], title: str = '📂 Files'):
    print_emphasis(f"{title} ({len(files)}):")
    print()
    print_info(f"\t{"\n\t".join(map(lambda file: f"- {file}", files))}")

#endregion