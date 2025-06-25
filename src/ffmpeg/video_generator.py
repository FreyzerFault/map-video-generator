from __future__ import annotations
import os 
from PIL import Image
from ffmpeg.text_filter import RelativePosition, TextBox, TextFilterData, TextStyle
from ffmpeg.timer_text_filter import TimerText
from ffmpeg.ffmpeg_operations import overlay_image_on_video, frames_to_video
from utils.image_utils import read_image_size
from utils.print_utils import colorize, print, print_error, print_info, print_verbose_info
from utils.file_utils import path_not_found, get_first_file


class VideoGenerator:
  def __init__(
    self,
    frames_folder_path: str = "",
    video_folder_path: str = "",
    name: str = "",
    frame_name: str = "",
    framerate: int = 24,
    timer: TimerText = None,
    title: TextBox = None,
    overlay_image_path: str = "",
  ):
    self.frames_path = os.path.join(frames_folder_path, name)
    self.video_path = os.path.join(video_folder_path, f"{name}.mp4")
    self.name = name
    self.frame_name = frame_name
    self.framerate = framerate
    self.timer = timer if timer else TimerText()
    self.title = title if title else TextBox.EMPTY_TITLE
    self.overlay_image_path = overlay_image_path
    
    if path_not_found(self.frames_path):
      print_error(f"⚠  No se ha encontrado la carpeta con los frames: {self.name}. O está vacía.")
    
    # Get a frame
    first_frame = get_first_file(self.frames_path)
    
    if not first_frame:
      print_error(f"⚠  No se ha encontrado ningún frame en la carpeta de frames {self.frames_path}")
      return
    
    self.size = read_image_size(first_frame)  # Placeholder for video size, to be set later
    self.video_width = self.size[0]
    self.video_height = self.size[1]


  @staticmethod
  def from_config(config: dict, frames_folder_path: str = "", video_folder_path: str = "", overlay_images_folder_path: str = "", title_style: TextStyle = TextStyle(), timer_style: TextStyle = TextStyle()) -> 'VideoGenerator':
    overlay_image_path = config.get('overlay_image', '')
    return VideoGenerator(
      frames_folder_path=frames_folder_path,
      video_folder_path=video_folder_path,
      name=config.get('name', ''),
      frame_name=config.get('frame_name', ''),
      framerate=config.get('framerate', 24),
      timer=TimerText.from_config(config.get('timer', {}), timer_style),
      title=TextBox.from_config(config.get('title', {}), title_style),
      overlay_image_path=os.path.join(overlay_images_folder_path, overlay_image_path) if overlay_image_path else ''
    )


  def frames_to_video(self, yes_to_all: bool = True, debug_mode: bool = False, verbose: bool = False, margin: tuple[int] = (30,30), char_width_by_font: float = 0.4, line_height_by_font: float = 1) -> str:
      """Procesa el pack de frames a video.
      Le añade un timer y una leyenda.

      Returns:
        str: Ruta del video de salida. En caso de error devuelve un str vacío.
      """
      #region Check Input Frames Path
      
      frames_path = os.path.join(self.frames_path, self.frame_name)
      
      # Check if the frames exists in the input frames folder
      if path_not_found(self.frames_path):
        print_error(
          f"Los frames de {self.name} no se encuentran en la ruta {self.frames_path}."
        )
        return ""

      # Ask to overwrite if the vídeo already exists
      if (os.path.exists(self.video_path)
        and not yes_to_all
        and input(colorize(f"El vídeo de salida {self.video_path} ya existe. ¿Deseas sobrescribirlo? (s/n):", 'yellow'))
        == "n"
      ):
        return ""
      
      #endregion

      # =================== TIMER =====================

      interval = self.timer.interval
      
      print()
      print_info(f"\t- ⏱️  {colorize(f"{interval.num} {interval.unit_label} / frame", 'red')} x {colorize(f"{self.framerate} fps", 'red')} = {self.framerate * interval.num} {interval.unit_label} {'reales' if interval.num > 1 else 'real'} / seg. de vídeo")
      print_info(f"\t- 📅 {self.timer.init_dt} - {self.timer.end_dt}")
      print_info(f"\t- 📏 {self.video_width} x {self.video_height} px")
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

      #region ================================ OVERLAY IMAGE ================================

      image_path = self.overlay_image_path

      if not image_path:
        return self.video_path

      if path_not_found(image_path):
        print_error(f"No se puede cargar la imagen {image_path} para superponer sobre el video {self.name}.")
        return self.video_path

      # Adjust size of image to size of video
      image_size = read_image_size(image_path)

      if image_size[0] != self.video_width or image_size[1] != self.video_height:
        print_verbose_info(f"Ajustando tamaño de la imagen {image_path}: {image_size[0]}x{image_size[1]} => {os.path.basename(self.video_path)} {self.video_width}x{self.video_height}")
        with Image.open(image_path) as img:
          img = img.resize((self.video_width, self.video_height), Image.Resampling.BILINEAR)  # Use BILINEAR for better quality

          # Save to a temporal folder
          resized_tmp_folder = os.path.join(os.path.dirname(image_path), "tmp_resized")
          os.makedirs(resized_tmp_folder, exist_ok=True)

          resized_img_path = os.path.join(resized_tmp_folder, f"{os.path.basename(image_path)}")
          img.save(resized_img_path)  # Overwrite the image with the resized one
          image_path = (resized_img_path) # Update legend_path to the resized image path

      video_path = overlay_image_on_video(self.video_path, image_path, self.video_path, verbose=verbose)
      
      #endregion
      
      return video_path


  def __str__(self):
    return f"Video(name={self.name}, frame_name={self.frame_name}, framerate={self.framerate}, timer={self.timer}, title={self.title}, overlay_image_path={self.overlay_image_path})"
