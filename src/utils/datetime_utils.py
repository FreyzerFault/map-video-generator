from datetime import datetime
from utils.print_utils import print_error

def to_datetime(date_str: str) -> datetime | None:
  """
  Convierte una cadena de fecha en formato 'dd-mm-YYYY HH:MM:SS' a un objeto datetime.
  """
  if not date_str:
    return None
  
  try:
    return datetime.strptime(date_str, '%d-%m-%Y %H:%M:%S')
  except ValueError:
    print_error(f"Fecha no válida: {date_str}. Debe tener el formato 'dd-mm-YYYY HH:MM:SS'.")
    return None
