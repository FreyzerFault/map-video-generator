# Map Video Generator for QGIS

QGIS permite renderizar animaciones con su herramienta de línea de tiempo si los datos tienen atributos temporales.

Lo que hace QGIS es generar frames por cada intervalo de tiempo y guardarlos como imágenes en una carpeta.

Para convertir estos frames a un video he creado este script que usa el comando _ffmpeg_.

## USO

Mete los frames generados del mapa en la carpeta **_frames_**.

Las imágenes de leyendas en la carpeta **_legend_images_**.

Configura todo en el **_config.yaml_**.

Y ejecuta **_convert_to_video.bat_**.

## CONFIGURACIÓN

Configura su funcionamiento con el archivo **_config.json_**.

### RUTAS

- **input_frames_folder_path**: Carpeta contenedora de las carpetas de frames de cada mapa.
- **output_videos_folder_path**: Carpeta contenedora de los videos que se generan
- **legend_images_folder_path**: Carpeta contenedora de las imágenes con la leyenda que quieras superponer al video

### Configuración de disposición global del texto

- **margin**: Margen del video para el texto (el timer y más)
- **char_width_by_font**: Ratio anchura de un caracter / el tamaño de letra
- **line_height_by_font**: Ratio altura de una línea de texto / el tamaño de let
- **line_height_by_font**: Ratio altura de una línea de texto / el tamaño de letra

### Estilo de cada texto

- **timer_text_style**: Estilo del texto del Timer
- **title_text_style**: Estilo del texto del Título
  - _font_size_: tamaño de letra.
  - _font_family_: Fuente de letra. Usa fuentes Mono para textos dinámicos como el Timer (el tamaño de caracter uniforme evita errores de posicionamiento del texto)
  - _color_: color del texto
  - _shadow_: true para que lleve una sombra

### MAPAS

_**maps**_ Contiene la lista de mapas para automatizar la ejecución del script con varios mapas, cada uno con su configuración propia:

- **name**: Nombre del mapa. Debe coincidir con la carpeta que contiene sus frames y el nombre del video generado.
- **frame_name**: Nombre dinámico de cada frame (configurado en QGIS en su generación). Ejemplo: f%04d.png
- **framerate**: frames por segundo. Ejemplo: 2fps para un video de 5 minutos por frame => 10 minutos reales por segundo de video.

- **overlay_legend**: nombre de la imagen de leyenda que quieras superponer.

- **title**:
  - **text**: Texto del título. Dejar vacío para no añadir ningún título
  - **position**: Posición relativa del Título (top_left, top_right, bot_left, bot_right, middle_left, middle_right, center)

- **timer**:
  - **realtime_date**: true => Timer normal en tiempo real || false => Contador de días en vez de mostrar la fecha real
  - **show_date**: true => Muestra la fecha || false => solo muestra la hora
  - **show_start_and_end_date**: true => Añade las fechas de inicio y fin del video
  - **interval**: Intervalo frame - frame (1y = 1 year, 1M = 1 month, 1d = 1 day, 1h = 1 hour, 1m = 1 minute, 1s = 1 second).
  - **initial_datetime**: Fecha de comienzo del video. (dd-MM-YYYY hh:mm:ss)
  - **end_datetime**: Fecha final del video. (dd-MM-YYYY hh:mm:ss)
  - **position**: Posición relativa del Título (top_left, top_right, bot_left, bot_right, middle_left, middle_right, center)

## Requisitos

- [Python 3](https://www.python.org/downloads/)

(Las dependencias adicionales se instalan automáticamente al ejecutar el script convert_to_video.bat por primera vez)

## GIFS

Como recomendación propia, uso [ezgif.com](https://ezgif.com/video-to-gif) para sacar gifs de los videos generados.

Son mucho más ligeros y fáciles de usar para colgarlos en una web o almacenarlos.

![gif](./docs/gif_demo.gif)
