from __future__ import annotations
from enum import Enum 
from utils.print_utils import print_error


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
      print_error(
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
