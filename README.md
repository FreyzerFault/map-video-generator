# Frames to Video Converter for QGIS

QGIS permite renderizar animaciones con su herramienta de línea de tiempo si los datos tienen atributos temporales.

Lo que hace QGIS es generar frames por cada intervalo de tiempo y guardarlos como imágenes en una carpeta.

Para convertir estos frames a un video he creado este script que usa ffmpeg.

## Uso

Al generar los frames con QGIS, selecciona como carpeta de extracción una nueva carpeta dentro de **_./frames_**, y configura como nombre de cada imagen "_f%04.png_". (puedes configurar el nombre que quieras si lo cambias en el "_config.json_").

Configura la carpeta de entrada y de salida en el **_config.json_** junto con el nombre dinámico de los frames y el nombre del video.

Configura los demás parámetros acorde a la configuración usada en QGIS:

- **framerate**: A tu gusto. Experimenta con el framerate para obtener un video más rápido o más lento.
- **min_interval**: Si el intervalo entre frames es de 1 minuto o mayor usa este parámetro.
- **sec_interval**: Si no, utiliza este y pon **use_secs** a true.
- **init\_[unit]**: Configura la fecha y hora inicial de la animación. Esto permitirá añadir un temporizador en la esquina del video.
- **video_title**: Añade un título incrustado en el video en una esquina.
- **realtime_date**: Si está a false, el timer pondrá la fecha inicial y añadirá un contador de días. Recomendado para animaciones de varios meses (no he conseguido calcular correctamente que algunos meses tienen 30 y otros 31 días).
- **show_date**: Si no quieres mostrar la fecha, porque la animación dura menos de un día, déjalo en false.
- **debug**: Muestra texto incrustado a un lado con información adicional.

Por último, ejecuta convert_to_video.bat.

## Requisitos

- Python 3

(Las dependencias adicionales se instalan automáticamente al ejecutar el script convert_to_video.bat por primera vez)

## GIFS

Como recomendación propia, uso [ezgif.com](https://ezgif.com/video-to-gif/ezgif-8529961dbedf1.mp4) para sacar gifs de los videos generados.

Son mucho más ligeros y fáciles de usar para colgarlos en una web.

![gif](gif_demo.gif)
