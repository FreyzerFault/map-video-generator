from enum import Enum
from colorama import init, Fore, Back, Style

init(convert=True)

def colorize(text, color = 'cyan'):
  color_dict = {
    'red': Fore.RED,
    'green': Fore.GREEN,
    'yellow': Fore.YELLOW,
    'blue': Fore.BLUE,
    'magenta': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE,
    'black': Fore.BLACK,
    'gray': Fore.LIGHTBLACK_EX,
    'grey': Fore.LIGHTBLACK_EX,
    'reset': Style.RESET_ALL
  }
  color_code = color_dict.get(color.lower(), Fore.RESET)
  return f"{color_code}{text}{Style.RESET_ALL}"


class LogLevel(Enum):
  INFO = 'info'
  VERBOSE = 'verbose'
  EMPHASIS = 'emphasis'
  WARNING = 'warning'
  ERROR = 'error'

class ConsoleApp():
  
  style_color = {
    LogLevel.INFO: 'white',
    LogLevel.VERBOSE: 'grey',
    LogLevel.EMPHASIS: 'cyan',
    LogLevel.WARNING: 'yellow',
    LogLevel.ERROR: 'red',
  }
  
  def get_color(self, log_level: LogLevel):
    return self.style_color.get(log_level, self.style_color[LogLevel.INFO])
  
  def __init__(self, verbose = False, yes_to_all = True, run_callback = None):
    
    self.verbose = verbose
    self.yes_to_all = yes_to_all
    
    self.run_callback = run_callback
  
  def print(self, message = "", color = 'white', end = '\n'):
    """print() con color. Usa colorama.\n
    Opciones: [red, green, blue, cyan, magenta, yellow, white, black, grey/gray]
    Args:
        end (str, optional): Añade al final sin color. Sustituye '\\n'.\n
          Útil para usar '\\r'.\nDefault: '\\n'
    """
    self.print(colorize(message, color), end=end)
  
  def print_error(self, message = ""):
    self.print(message, self.get_color(LogLevel.ERROR))
  
  def print_warning(self, message = ""):
    self.print(message, self.get_color(LogLevel.WARNING))
  
  def print_emphasis(self, message = ""):
    self.print(message, self.get_color(LogLevel.EMPHASIS))
  
  def print_info(self, message = ""):
    self.print(message, self.get_color(LogLevel.INFO))
  
  def print_verbose_info(self, message = ""):
    if self.verbose:
      self.print(message, self.get_color(LogLevel.VERBOSE))
  
  
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


#region WRAPPER out of console
def print(message = "", color = 'white', end = '\n'):
  """print() con color. Usa colorama.\n
  Opciones: [red, green, blue, cyan, magenta, yellow, white, black, grey/gray]
  Args:
      end (str, optional): Añade al final sin color. Sustituye '\\n'.\n
        Útil para usar '\\r'.\nDefault: '\\n'
  """
  import builtins
  builtins.print(colorize(message, color), end=end)

def print_error(message = ""):
  print(message, console.get_color(LogLevel.ERROR))

def print_warning(message = ""):
  print(message, console.get_color(LogLevel.WARNING))

def print_emphasis(message = ""):
  print(message, console.get_color(LogLevel.EMPHASIS))

def print_info(message = ""):
  print(message, console.get_color(LogLevel.INFO))

def print_verbose_info(message = ""):
  if console.verbose:
    print(message, console.get_color(LogLevel.VERBOSE))


def print_progressBar (iteration, total, prefix = '', suffix = '', decimals = 0, length = 100, fill = '█', printEnd = "\r", show_percent: bool = True):
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


def print_file_list(files: list[str], title: str = '📂 Files'):
  print_emphasis(f"{title} ({len(files)}):")
  print()
  print_info(f"\t{"\n\t".join(map(lambda file: f"- {file}", files))}")

#endregion