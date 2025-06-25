from __future__ import annotations
from enum import Enum 
from ffmpeg.text_filter import RelativePosition, TextBox, TextStyle, to_filter_func, to_filter_int_text
from utils.datetime_utils import to_datetime
from utils.print_utils import print_error


class TimeUnit(Enum):
  SECOND = "s"
  MINUTE = "m"
  HOUR = "h"
  DAY = "d"
  MONTH = "M"
  YEAR = "y"
  INVALID = ""


unit_multipliers: dict = {
  TimeUnit.SECOND: 1,
  TimeUnit.MINUTE: 60,
  TimeUnit.HOUR: 60 * 60,
  TimeUnit.DAY: 24 * 60 * 60,
  TimeUnit.MONTH: 30 * 24 * 60 * 60,  # Aproximación de 30 días por mes
  TimeUnit.YEAR: 365 * 24 * 60 * 60,  # Aproximación de 365 días por año
  TimeUnit.INVALID: -1
}

unit_labels: dict = {
  TimeUnit.SECOND: ("segundo", "segundos"),
  TimeUnit.MINUTE: ("minuto", "minutos"),
  TimeUnit.HOUR: ("hora", "horas"),
  TimeUnit.DAY: ("día", "días"),
  TimeUnit.MONTH: ("mes", "meses"),
  TimeUnit.YEAR: ("año", "años"),
  TimeUnit.INVALID: ("", "")
}


class Interval:
  """ Intervalo frame a frame. Posibilidades: (1M = 1 month, 1d = 1 day, 1h = 1 hour, 1m = 1 minute, 1s = 1 second) """
  def __init__(self, num: int = -1, unit: TimeUnit = TimeUnit.INVALID):
    self.num = num
    self.unit = unit
    
    if unit == TimeUnit.INVALID:
      print_error(f"Unidad de tiempo no válida: {unit.value}. Debe ser una de las siguientes: {[u.value for u in TimeUnit]}.")
      self.seconds = -1
      self.unit_label = "[INVALID]"
    
    self.seconds = self.num * unit_multipliers.get(self.unit, -1)
    
    unit_singular, unit_plural = unit_labels.get(self.unit, ("", ""))
    self.unit_label = unit_plural if self.num > 1 else unit_singular
  
  @staticmethod
  def from_text(text: str = '1d') -> Interval:
    num_str = text[:-1]
    num = int(num_str)
    
    try:
      unit: TimeUnit = TimeUnit(text[-1])
      return Interval(num, unit)
    except ValueError:
      print_error(f"Unidad de tiempo no válida: {text[-1]}. Debe ser una de las siguientes: {[unit.value for unit in TimeUnit]}.")
      return Interval(num, TimeUnit.INVALID)


class TimerText(TextBox):
  def __init__(
    self,
    filter_text: str = "",
    sample_text: str = "",
    position: RelativePosition = RelativePosition.TOP_LEFT,
    txt_style: TextStyle = None,
    realtime_date: bool = True,
    show_date: bool = True,
    show_start_and_end_date: bool = False,
    interval: Interval = None,
    initial_datetime: str = "01-01-2023 00:00:00",
    end_datetime: str = "01-02-2023 00:00:00",
  ):
    super(TimerText, self).__init__(filter_text, sample_text, position, txt_style)
    
    self.sample_text = sample_text
    
    # Flags
    self.realtime_date = realtime_date
    self.show_date = show_date
    self.show_start_and_end_date = show_start_and_end_date
    
    self.interval = interval
    
    # Datetime conversion
    self.init_dt = to_datetime(initial_datetime)
    self.end_dt = to_datetime(end_datetime)


  @staticmethod
  def from_config(config: dict, txt_style: TextStyle = TextStyle()):
    position = RelativePosition[config.get("position", "top_left").upper()]
    return TimerText(
      sample_text=config.get("sample_text", ""),
      filter_text=config.get("filter_text", ""),
      position=position,
      txt_style=txt_style,
      realtime_date=config.get("realtime_date", True),
      show_date=config.get("show_date", True),
      show_start_and_end_date=config.get("show_start_and_end_date", False),
      interval=Interval.from_text(config.get("interval", "1d")),
      initial_datetime=config.get("initial_datetime", "01-01-2023 00:00:00"),
      end_datetime=config.get("end_datetime", "01-02-2023 00:00:00"),
    )
  
  
  def build_text(self):
    # SHOW TIMER IF MIN_INTERVAL IS LESS THAN 1440 (1 DAY) or use_secs is True
    show_time = self.interval.seconds < 60 * 60 * 24
    show_seconds = self.interval.seconds < 60    
    
    total_secs = f"floor({self.init_dt.second} + (n*{self.interval.seconds}))"
    total_mins = f"floor({self.init_dt.second} + {total_secs}/60)"
    total_hours = f"floor({self.init_dt.hour} + {total_mins}/60)"
    total_days = f"({total_hours}/24)"

    sec = f"mod({total_secs},60)"
    min = f"mod({total_mins},60)"
    hour = f"mod({total_hours},24)"

    # * NOTA: El cálculo de la fecha es un poco más complicado, ya que día y més son interdependientes.
    # * En caso de pasar por varios meses, se recomienda desactivar la fecha en tiempo real en el config.json.
    # El cálculo del día es dependiente de los días que tiene el mes, y el mes dependiente de los días que han pasado,
    # por lo que dia y mes son interdependientes, no se puede calcular a partir de frame.
    # Se podría acumular los días y reiniciar el contador al llegar al día 31 o 32,
    # pero dado las limitaciones de ffmpeg, no es posible acumular valores, debe estar todo calculado en 1 expresión.

    day = f"(floor({self.init_dt.day} + {total_days}) - 1)"  # Se resta 1 para que el día 1 sea 0 para hacer los cálculos más simples

    # Para meses del 1 al 7, los meses impares tienen 31 días y los pares 30, y para los meses del 8 al 12 es al revés.
    days_of_month = (
        f"(31-mod({self.init_dt.month} + floor({day}/(31 - lt({self.init_dt.month},8))),2))"
    )

    month = f"floor({self.init_dt.month} + floor({day}/{days_of_month}))"

    day = f"1+mod({day},{days_of_month})"
    month = f"1+mod({month}-1,12)"
    year = str(self.init_dt.year)
    
    timer_txt = {
      'year': to_filter_int_text(year, 4),
      'month': to_filter_int_text(month),
      'day': to_filter_int_text(day),
      'hour': to_filter_int_text(hour),
      'min': to_filter_int_text(min),
      'sec': to_filter_int_text(sec),
      'total_days': f" Día {to_filter_func('eif', [total_days, 'd', '2'])}",
    }
    
    timer_date_txt = f"{timer_txt['day']}-{timer_txt['month']}-{timer_txt['year']}"
    timer_time_txt = (
      f"{timer_txt['hour']}\\:{timer_txt['min']}{f'\\:{timer_txt['sec']}' if show_seconds else ''}"
    )

    self.text = (
      f"{timer_date_txt if self.show_date else ''} {timer_time_txt if show_time else ''}"
      if self.realtime_date
      else f"{timer_txt['total_days']} {timer_time_txt if show_time else ''}"
    )

    self.sample_text = (
      f"00-00-0000{f' 00:00{":00" if show_seconds else ""}' if show_time else ''}"
      if self.realtime_date
      else f"00/00/00 - 00/00/00 Día 000{f' 00:00:{":00" if show_seconds else ""}' if show_time else ''}"
    )


  def get_date_interval_txt(self):
    return f"{to_filter_int_text(self.init_dt.day, 1)}/{to_filter_int_text(self.init_dt.month, 1)}/{to_filter_int_text(self.init_dt.year)} - {to_filter_int_text(self.end_dt.day, 1)}/{to_filter_int_text(self.end_dt.month, 1)}/{to_filter_int_text(self.end_dt.year)}"

  def __str__(self):
    return f"Timer(text={self.text}, position={self.position}, realtime_date={self.realtime_date}, show_date={self.show_date}, interval={self.interval}, init_dt={self.init_dt}, end_dt={self.end_dt}, show_start_and_end_date={self.show_start_and_end_date})"

