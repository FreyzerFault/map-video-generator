from __future__ import annotations
import argparse
import os
from enum import Enum
from PIL import Image
from colorama import Fore, Back, Style
from datetime import datetime
from image_utils import read_image_size
from utils import ConsoleApp, console, get_first_file
from utils import load_config, path_not_found

from ffmpeg_operations import overlay_image_on_video, frames_to_video

class RelativePosition(Enum):
  TOP_LEFT = "top_left"
  TOP_RIGHT = "top_right"
  BOT_LEFT = "bot_left"
  BOT_RIGHT = "bot_right"
  TOP_MIDDLE = "top_middle"
  BOT_MIDDLE = "bot_middle"
  MIDDLE_LEFT = "middle_left"
  MIDDLE_RIGHT = "middle_right"
  CENTER = "center"

#region ========================================= TEXT FILTER =========================================

# Dentro del filtro de texto se pueden usar expresiones dinámicas
# como %{e:expresion} y %{eif:expresion:formato:precision} para cálculos dinámicos
# usando como variable el frame actual (n).
def to_filter_func(name, args):
    return f"%{'{'}{name}\\:{'\\:'.join(args)}{'}'}"

# Construye una expresión con formato de número entero
def to_filter_int_text(exp, digits=2):
    return to_filter_func("eif", [str(exp), "d", str(digits)])

class TextFilterData:
    def __init__(
        self,
        txt: str,
        position: RelativePosition = RelativePosition.TOP_LEFT,
        font_size: int = 24,
        font_family: str = "MS shell dlg 2",
        color: str = "white",
        shadow: bool = False,
        sample_txt: str = "",
    ):
        """Construye un filtro de texto para ffmpeg.

        Args:
            txt (str): texto del filtro. Puede ser dinámico. Por ejemplo usando n (el nº de frame)
            position (Relative_Position, optional): Posición relativa del texto. Default: Relative_Position.TOP_LEFT.
            font_size (int, optional): tamaño de texto. Default = 24.
            font_family (str, optional): tipo de fuente. Default = "MS shell dlg 2".
            color (str, optional): color de la fuente. Default = 'white'.
            shadow (bool, optional): tiene sombra o no. Default = False.
            sample_txt (str, optional): Para textos dinámicos. Se usará para calcular el tamaño del texto. Default = "".
        """
        self.txt = txt
        self.sample_txt = sample_txt
        self.rel_position = position
        self.font_size = font_size
        self.font_family = font_family
        self.color = color
        self.shadow = shadow

    def get_txt_size(
        self, char_width_by_font: float = 0.5, line_height_by_font: float = 1
    ) -> tuple[float, float]:
      """Tamaño del texto en píxeles proporcional al tamaño de fuente con los ratios adecuados font_size -> px

      Args:
          char_width_by_font (float, optional): Ratio tamaño de char / font_size. Defaults to 0.5.
          line_height_by_font (float, optional): Ratio alto de línea / font_size. Defaults to 1.

      Returns:
          tuple[float, float]: tamaño 2D
      """
      txt_width = (char_width_by_font * self.font_size * len(self.sample_txt if self.sample_txt != "" else self.txt))
      txt_height = line_height_by_font * self.font_size

      return txt_width, txt_height

    # 
    def get_XY_by_pos(
        self,
        video_width: int,
        video_height: int,
        mx: float = 30,
        my: float = 30,
        char_width_by_font: float = 0.5,
        line_height_by_font: float = 1,
    ) -> tuple[float, float]:
      """Obtiene las coordenadas X e Y para colocar el texto en la posición deseada.

      Args:
          video_width (int): Ancho del video
          video_height (int): Alto del video
          mx (float, optional): Margen X. Defaults to 30.
          my (float, optional): Margen Y. Defaults to 30.
          char_width_by_font (float, optional): Ratio tamaño de char / font_size. Defaults to 0.5. Defaults to 0.5.
          line_height_by_font (float, optional): Ratio alto de línea / font_size. Defaults to 1. Defaults to 1.

      Raises:
          ValueError: Relative_Position no válida.

      Returns:
          tuple[float, float]: Posición X,Y del texto en el vídeo en píxeles.
      """
      (width, height) = self.get_txt_size(char_width_by_font, line_height_by_font)

      left_x = mx
      right_x = video_width - mx - width

      top_y = my
      bot_y = video_height - my - height

      if self.rel_position == RelativePosition.TOP_LEFT:
          return (left_x, top_y)
      elif self.rel_position == RelativePosition.TOP_RIGHT:
          return (right_x, top_y)
      elif self.rel_position == RelativePosition.BOT_LEFT:
          return (left_x, bot_y)
      elif self.rel_position == RelativePosition.BOT_RIGHT:
          return (right_x, bot_y)
      elif self.rel_position == RelativePosition.TOP_MIDDLE:
          return ((video_width - width) / 2, top_y)
      elif self.rel_position == RelativePosition.BOT_MIDDLE:
          return (video_width - width) / 2, bot_y
      elif self.rel_position == RelativePosition.MIDDLE_LEFT:
          return (left_x, (video_height - height) / 2)
      elif self.rel_position == RelativePosition.MIDDLE_RIGHT:
          return (right_x, (video_height - height) / 2)
      elif self.rel_position == RelativePosition.CENTER:
          return ((video_width - width) / 2, (video_height - height) / 2)
      else:
          console.print_error(
              f"Posición relativa no válida: {self.rel_position}. Debe ser una de las siguientes: {', '.join([pos.value for pos in RelativePosition])}."
          )
          raise ValueError()

    def build_text_filter_by_relative_pos(
        self,
        video_width: int,
        video_height: int,
        mx: float = 30,
        my: float = 30,
        char_width_by_font: float = 0.5,
        line_height_by_font: float = 1,
    ) -> str:
      """Construye el filtro de texto para ffmpeg según la posición relativa del filtro

      Args:
          video_width (int): Ancho del video
          video_height (int): Alto del video
          mx (float, optional): Margen X. Defaults to 30.
          my (float, optional): Margen Y. Defaults to 30.
          char_width_by_font (float, optional): Ratio tamaño de char / font_size. Defaults to 0.5. Defaults to 0.5.
          line_height_by_font (float, optional): Ratio alto de línea / font_size. Defaults to 1. Defaults to 1.

      Returns:
          str: Text Filter for ffmpeg
      """
      (x, y) = self.get_XY_by_pos(
          video_width, video_height, mx, my, char_width_by_font, line_height_by_font
      )

      return self.build_text_filter(x, y)

    def build_text_filter(self, x: int, y: int) -> str:
      """Construye el filtro de texto para ffmpeg con las coordenadas X e Y que pases

      Args:
          x (int): en píxeles
          y (int): en píxeles

      Returns:
          _type_: Text Filter for ffmpeg
      """
      shadow_args = f":shadowcolor={self.color}:shadowx=1:shadowy=1"
      font_args = f":font={self.font_family}"

      return (
          f"drawtext=text='{self.txt}':x='{x}':y='{y}':fontsize='{self.font_size}':fontcolor='{self.color}'"
          + (shadow_args if self.shadow else "")
          + font_args
      )

    # 
    @staticmethod
    def concatenate_filters(*filters) -> str:
      """Concatenar varias expresiones de filtro drawtext para mostrar varios textos en la misma imagen.
      Filtra los filtros vacíos.

      Returns:
          str: filtro1,filtro2,filtro3,...
      """ 
      return ",".join(f for f in filters if f != "" and f is not None)


class TextStyle:
  def __init__(
    self,
    font_size: int = 24,
    font_family: str = "Sans",
    color: str = "white",
    shadow: bool = False
  ):
    self.font_size = font_size
    self.font_family = font_family
    self.color = color
    self.shadow = shadow
  
  @staticmethod
  def from_config(config: dict) -> TextStyle:
    return TextStyle(config['font_size'], config['font_family'], config['color'], config['shadow'])


class TextBox:
  def __init__(
    self,
    text: str = "",
    sample_text: str = "", # Para textos dinámicos como un timer
    position: RelativePosition = RelativePosition.TOP_LEFT,
    txt_style: TextStyle = None,
  ):
    self.text = text
    self.sample_text = sample_text
    self.position = position
    self.style = txt_style
  
  
  @staticmethod
  def from_config(config: dict, txt_style: TextStyle = TextStyle()):
    return TextBox(
      text=config.get("text", ""),
      position=RelativePosition[config.get("position", "TOP_LEFT").upper()],
      txt_style=txt_style
    )
  
  
  def to_FilterData(self) -> TextFilterData:
    return TextFilterData(self.text, self.position, self.style.font_size, self.style.font_family, self.style.color, self.style.shadow, self.sample_text)


  def __str__(self):
    return f"Title(text={self.text}, position={self.position})"

#endregion


#region ======================================== TIMER ========================================

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
      console.print_error(f"Unidad de tiempo no válida: {unit.value}. Debe ser una de las siguientes: {[u.value for u in TimeUnit]}.")
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
      console.print_error(f"Unidad de tiempo no válida: {text[-1]}. Debe ser una de las siguientes: {[unit.value for unit in TimeUnit]}.")
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


#region ======================================== MAP ========================================

class Map:
  def __init__(
    self,
    frames_folder_path: str = "",
    video_folder_path: str = "",
    name: str = "",
    frame_name: str = "",
    framerate: int = 24,
    timer: TimerText = None,
    title: TextBox = None,
    overlay_legend_path: str = "",
  ):
    self.frames_path = os.path.join(frames_folder_path, name)
    self.video_path = os.path.join(video_folder_path, f"{name}.mp4")
    self.name = name
    self.frame_name = frame_name
    self.framerate = framerate
    self.timer = timer if timer else TimerText()
    self.title = title if title else TextBox.EMPTY_TITLE
    self.overlay_legend_path = overlay_legend_path
    
    if path_not_found(self.frames_path):
      console.print_error(f"⚠ No se ha encontrado la carpeta del mapa {self.name} o está vacía.")
    
    # Map Size
    first_frame = get_first_file(self.frames_path)
    
    if not first_frame:
      console.print_error(f"⚠ No se ha encontrado ningún frame en la carpeta de frames {self.frames_path}")
      return
    
    self.size = read_image_size(first_frame)  # Placeholder for video size, to be set later
    self.video_width = self.size[0]
    self.video_height = self.size[1]


  @staticmethod
  def from_config(config: dict, frames_folder_path: str = "", video_folder_path: str = "", legend_images_folder_path: str = "", title_style: TextStyle = TextStyle(), timer_style: TextStyle = TextStyle()) -> 'Map':
    legend_image = config.get('overlay_legend_path', '')
    return Map(
      frames_folder_path=frames_folder_path,
      video_folder_path=video_folder_path,
      name=config.get('name', ''),
      frame_name=config.get('frame_name', ''),
      framerate=config.get('framerate', 24),
      timer=TimerText.from_config(config.get('timer', {}), timer_style),
      title=TextBox.from_config(config.get('title', {}), title_style),
      overlay_legend_path=os.path.join(legend_images_folder_path, legend_image) if legend_image else ''
    )


  def frames_to_video(self, yes_to_all: bool = True, debug_mode: bool = False, verbose: bool = False, margin: tuple[int] = (30,30), char_width_by_font: float = 0.4, line_height_by_font: float = 1) -> str:
      """Procesa el Mapa de frames a video.
      Le añade un timer y una leyenda.

      Returns:
        str: Ruta del video de salida. En caso de error devuelve un str vacío.
      """
      #region Check Input Frames Path
      
      frames_path = os.path.join(self.frames_path, self.frame_name)
      
      # Check if the map exists in the input frames folder
      if path_not_found(self.frames_path):
        console.print_error(
          f"Los frames del mapa {self.name} no se encuentran en la ruta {self.frames_path}."
        )
        return ""

      # Ask to overwrite if the vídeo already exists
      if (os.path.exists(self.video_path)
        and not yes_to_all
        and input(f"{Fore.YELLOW}El vídeo de salida {self.video_path} ya existe. ¿Deseas sobrescribirlo? (s/n): {Style.RESET_ALL}")
        == "n"
      ):
        return ""
      
      #endregion

      # =================== TIMER =====================

      interval = self.timer.interval
      
      print()
      console.print_info(f"\t- ⏱️  {Fore.RED}{interval.num} {interval.unit_label} / frame{Fore.RESET} x {Fore.RED}{self.framerate} fps{Fore.RESET} = {self.framerate * interval.num} {interval.unit_label} {'reales' if interval.num > 1 else 'real'} / seg. de vídeo")
      console.print_info(f"\t- 📅 {self.timer.init_dt} - {self.timer.end_dt}")
      console.print_info(f"\t- 📏 {self.video_width} x {self.video_height} px")
      print()

      #region ============================ DYNAMIC TEXT FILTER EXPRESSIONS ============================
      
      # ======================== TITLE ========================

      if self.title and self.title.text:
        title_filter_data = self.title.to_FilterData()
        title_filter = title_filter_data.build_text_filter_by_relative_pos(
          self.video_width, self.video_height, margin[0], margin[1], char_width_by_font, line_height_by_font
        )
      else:
        title_filter = None

      # ======================== TIMER ========================

      self.timer.build_text() # This builds the Timer filter expression
      
      timer_filter_data = self.timer.to_FilterData()
      (x, y) = timer_filter_data.get_XY_by_pos(
        self.video_width, self.video_height, margin[0], margin[1], char_width_by_font, line_height_by_font
      )

      # INIT and END Date FILTER
      init_datetime_filter = ""
      if self.timer.show_start_and_end_date:
        sample_date_interval_txt = f"{self.timer.init_dt.day}/{self.timer.init_dt.month}/{self.timer.init_dt.year} - {self.timer.end_dt.day}/{self.timer.end_dt.month}/{self.timer.end_dt.year}"
        start_end_date_txtBox = TextBox(self.timer.get_date_interval_txt(), sample_date_interval_txt, self.timer.position, self.timer.style)
        start_end_date_filter_data = start_end_date_txtBox.to_FilterData()

        init_datetime_filter = (
          start_end_date_filter_data.build_text_filter_by_relative_pos(
            self.video_width, self.video_height, margin[0], margin[1], char_width_by_font, line_height_by_font
          )
        )
        
        y_offset = (start_end_date_filter_data.font_size * line_height_by_font * 1.5)
        y += (
          -y_offset
          if self.timer.position in [RelativePosition.BOT_LEFT, RelativePosition.BOT_RIGHT, RelativePosition.BOT_MIDDLE]
          else
          +y_offset
        )

      # TIMER Filter
      timer_filter = timer_filter_data.build_text_filter(x, y)

      # Overlap ALL filters in one
      text_filter = TextFilterData.concatenate_filters(
        title_filter, timer_filter, init_datetime_filter
      )

      #endregion

      #region DEBUGGING
      
      if debug_mode:
        # FRAMES
        debug_frames_txtBox = TextBox(
          "Frame: %{eif:n:d:4}",
          "Frame: 0000",
          RelativePosition.MIDDLE_LEFT,
          TextStyle(16, color="red", shadow=True)
        )
        debug_frames_filter_data = debug_frames_txtBox.to_FilterData()
        debug_frames_filter = (
          debug_frames_filter_data.build_text_filter_by_relative_pos(
            self.video_width, self.video_height, margin['x'], margin['y'], char_width_by_font, line_height_by_font
          )
        )

        # Overlap with the other text filters
        text_filter = TextFilterData.concatenate_filters(
          text_filter, debug_frames_filter
        )
      
      #endregion

      #region ======================== PROCESS VIDEO ========================
      
      frames_to_video(frames_path, self.video_path, self.framerate, text_filter, verbose)
      
      #endregion

      #region ================================ LEGEND ================================

      legend_path = self.overlay_legend_path

      if not legend_path:
        return self.video_path

      if path_not_found(legend_path):
        console.print_error(f"No se puede cargar la imagen de leyenda {legend_path} para el mapa {self.name}.")
        return self.video_path

      video_with_legend_path = os.path.join(os.path.dirname(self.video_path), f"{self.name}_with_legend.mp4")

      if (
        os.path.exists(video_with_legend_path)
        and not yes_to_all
        and input(
          f"{Fore.YELLOW}El vídeo con leyenda {video_with_legend_path} ya existe. ¿Deseas sobrescribirlo? (s/n): {Style.RESET_ALL}"
        ) == 'n'
      ):
        return self.video_path

      # Adjust size of image to size of video
      image_size = read_image_size(legend_path)

      if image_size[0] != self.video_width or image_size[1] != self.video_height:
        console.print_verbose_info(f"Ajustando tamaño de la imagen de leyenda {legend_path}: {image_size[0]}x{image_size[1]} => {os.path.basename(self.video_path)} {self.video_width}x{self.video_height}")
        with Image.open(legend_path) as img:
          img = img.resize((self.video_width, self.video_height), Image.Resampling.BILINEAR)  # Use BILINEAR for better quality

          # Save to a temporal folder
          resized_tmp_folder = os.path.join(os.path.dirname(legend_path), "tmp_resized")
          os.makedirs(resized_tmp_folder, exist_ok=True)

          resized_img_path = os.path.join(resized_tmp_folder, f"{os.path.basename(legend_path)}")
          img.save(resized_img_path)  # Overwrite the image with the resized one
          legend_path = (resized_img_path) # Update legend_path to the resized image path

      overlay_image_on_video(self.video_path, legend_path, video_with_legend_path, verbose=verbose)
      
      #endregion
      
      return video_with_legend_path


  def __str__(self):
    return f"Map(name={self.name}, frame_name={self.frame_name}, framerate={self.framerate}, timer={self.timer}, title={self.title}, overlay_legend_path={self.overlay_legend_path})"

#endregion


#region ====================================== MAIN ======================================

def main():
  
  #region PARSE ARGUMENTS
  args = parse_args()
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
  legend_images_folder_path = config["legend_images_folder_path"]

  if path_not_found(input_frames_folder_path) or path_not_found(output_videos_folder_path):
    return

  # TEXT STYLE
  title_text_style = TextStyle.from_config(config["title_text_style"])
  timer_text_style = TextStyle.from_config(config["timer_text_style"])

  margin = (config["margin"]["x"], config["margin"]["y"])

  char_width_by_font = config["char_width_by_font"]
  line_height_by_font = config["line_height_by_font"]


  # Inicialización de los Mapas a partir del archivo de configuración
  maps = [Map.from_config(map_config, input_frames_folder_path, output_videos_folder_path, legend_images_folder_path, title_text_style, timer_text_style) for map_config in config["maps"]]
  
  #endregion
  
  
  videos = []

  # Initial call to print 0% progress
  progress_bar = {
    "total": len(maps),
    "prefix": "🎥 Video Generation:",
    "suffix": "Videos 🎬",
    "length": len(maps) * 5,
    "print_end": "\n",
    "show_percentage": False
  }

  # Iterate each MAP
  for i, map in enumerate(maps):
    print()
    console.print_emphasis(f"{'=' * 40} 🧭 {map.name} 🕒 {'=' * 40}")
    print()
    console.printProgressBar(
      i,
      progress_bar["total"],
      prefix=progress_bar["prefix"],
      suffix=progress_bar["suffix"],
      length=progress_bar["length"],
      printEnd=progress_bar["print_end"],
      show_percent=progress_bar["show_percentage"],
    )
    print()
    
    
    videos.append(map.frames_to_video(yes_to_all, debug_mode, verbose, margin, char_width_by_font, line_height_by_font))


  print()
  console.printProgressBar(
    progress_bar["total"],
    progress_bar["total"],
    prefix="✨ COMPLETED ✨",
    suffix=progress_bar["suffix"],
    length=progress_bar["length"],
    show_percent=progress_bar["show_percentage"],
  )
  print()
  console.print_file_list(videos, '🎬 Videos')
  print()


#endregion



#region ============================================= DATETIME UTILS =========================================

def to_datetime(date_str: str) -> datetime | None:
  """
  Convierte una cadena de fecha en formato 'dd-mm-YYYY HH:MM:SS' a un objeto datetime.
  """
  if not date_str:
    return None
  
  try:
    return datetime.strptime(date_str, '%d-%m-%Y %H:%M:%S')
  except ValueError:
    console.print_error(f"Fecha no válida: {date_str}. Debe tener el formato 'dd-mm-YYYY HH:MM:SS'.")
    return None

#endregion


#region ============================================= UTILS =========================================

def parse_args():
    parser = argparse.ArgumentParser(
    description="Convertidor de Mapas en Frames a Video con Timer y Leyenda incluido. Configura todo en el config.json"
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
    return parser.parse_args()

#endregion


if __name__ == "__main__":
  main()