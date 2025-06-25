# Frames to Video Generator

Esta herramienta **convierte imágenes en masa como frames de un video**.  
Y **automatiza** el proceso de generación de varios videos.

Permite añadir un **timer** para visualizar el tiempo real.  
Además de **texto** y **suponer una imagen** a modo de HUD.
Útil para crear **Timelapses**.

Nació de la necesidad de generar **mapas animados** a partir de datos de trazabilidad de un rebaño.  
Nos permite generarlos en distintos intervalos de tiempo y distintos ritmos, superponer la leyenda automáticamente y etiquetarlos correctamente.

QGIS permite renderizar animaciones con su herramienta de línea de tiempo a partir de datos con atributos temporales.  
QGIS se encarga de generar frames. En un intervalo de tiempo y a un ritmo dado. Los guarda como imágenes en una carpeta.

Este programa está programada sobre python, usando la librería _ffmpeg_, tanto para generar video como superponer texto dinámico e imágenes.

## USO

Descarga [la última Release](https://github.com/FreyzerFault/frames-to-video-generator/releases).

Ejecuta "**_RUN ME_**" antes de nada.

Mete todos los frames dentro de su carpeta (el nombre de la carpeta será el del video generado) en la carpeta "**_- frames_**".

Las imágenes de leyendas en la carpeta "**_- overlay images_**".

Configura todo en el "**_config.yaml_**".
Si no entiendes algo mira los detalles [más abajo](#configuración).

Y ejecuta "**Generar Videos**".

Los videos generados aparecerán en la carpeta "**_- videos_**"

### ¿Algo ha ido mal?

Ejecuta el test: "**TEST - Generar Videos de prueba**".  
Generará unos videos de prueba en la carpeta "**_test_**".

Fíjate en el "**_test/config.yaml_**", que contiene la configuración de la prueba.  
Si la prueba tampoco funciona bien mándame la salida del terminal para que pueda ayudarte.

## CONFIGURACIÓN

Configura su funcionamiento con el archivo **_config.yaml_**.

### RUTAS

- **input_frames_folder_path**: Carpeta contenedora de las carpetas con los frames de cada video.
- **output_videos_folder_path**: Carpeta contenedora de los videos que se generan
- **overlay_images_folder_path**: Carpeta contenedora de las imágenes con la leyenda que quieras superponer al video

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

### VIDEOS

"_**videos**_" Contiene la lista de videos para automatizar la ejecución del script con varios videos, cada uno con su configuración propia.  
Copia y pega cada bloque de video para generar otro video en el orden de la lista.

- **name**: Nombre del video. Debe coincidir con la carpeta que contiene sus frames y el nombre del video generado.
- **frame_name**: Nombre dinámico de cada frame (configurado en QGIS en su generación). Ejemplo: f%04d.png
- **framerate**: frames por segundo. Ejemplo: 2fps para un video de 5 minutos por frame => 10 minutos reales por segundo de video.

- **overlay_image**: nombre de la imagen que quieras superponer (dentro de "_- overlay images_").

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

## Código

Para probar o modificar el código clona el repositorio.

Dentro de src está todo el funcionamiento del programa.

### Compilación

Para compilarlo ejecuta:

```cmd
py build_bundle.py
```

#### ¿Qué hace?

- Comprueba que estén las **dependencias** instaladas.
- **Compila el RUN ME.exe** con _pyInstaller_. Servirá dentro del bundle para crear los accesos directos.
- **Compila el bundle** con _pyInstaller_.  
El .spec se ejecuta en pyInstaller como un script de python, por lo que he añadido al final que ejecute el script setup_bundle.py.  
Puedes cambiar la versión y nombre del programa en el .spec.  
El cual:
  - **Inserta los assets** (archivos y carpetas necesarias para usar el programa, junto al .exe), y el RUN ME.exe, para ejecutarlo en el pc del usuario.  
Debe ejecutarse cuando el usuario tenga el bundle, ya que crea accesos directos dependientes de la ruta absoluta de su equipo.
  - **Comprime el bundle** en un .zip para publicar directamente.

### Ejecutar

Ejecuta main.py

```cmd
py ./src/main.py
```

Como opciones está:

- y: Yes to all. Para aceptar automáticamente cualquier pregunta.
- t: Test Mode. Para ejecutarlo sobre los datos y config de la carpeta test
- d: Debug Mode. Para mostrar información en el video como texto superpuesto.
- v: Verbose. Muestra más información de lo que hace por dentro

La ejecución rápida:

```cmd
py ./src/main.py -y
```

Lo que uso para testear:

```cmd
py ./src/main.py -yt
```

## GIFS

Como recomendación propia, uso [ezgif.com](https://ezgif.com/video-to-gif) para sacar gifs de los videos generados.

Son mucho más ligeros y fáciles de usar para colgarlos en una web o almacenarlos.

![gif](./docs/gif_demo.gif)
