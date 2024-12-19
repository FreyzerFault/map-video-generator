@echo off

:: Este script utiliza ffmpeg para convertir una secuencia de imágenes en un video.
:: %input_path% es la ruta de entrada donde se encuentran las imágenes.
:: %output_path% es la ruta de salida donde se guardará el video generado.
:: Verifica si se ha proporcionado un argumento de entrada.
if "%~1"=="" (
  echo Por favor, proporciona la ruta de entrada de las imágenes.
  exit /b 1
)

:: Asigna el argumento de entrada a la variable input_path.
set input_path=%~1

:: Entrada y salida del video.
set input_path=".\Belen Agosto - 246064 15m\Belen246064f%%04d.png"
set output_path="output 15m.mp4"
set framerate=5

:: Configura la fecha y hora de inicio para mostrarlo como un timer.
set init_year=2024
set init_month=8
set init_day=5
set init_hour=0
set init_min=0
set min_interval=15

:: Calcula la fecha y hora actual en función del número de fotogramas (n).
set min=%%{eif\:%init_min% + mod(n*%min_interval%,60)\:d\:2}
set hour=%%{eif\:%init_hour% + mod((n*%min_interval%)/60,24)\:d\:2}
set day=%%{eif\:%init_day% + mod((n*%min_interval%)/60/24,31)\:d\:2}
set month=%%{eif\:%init_month% + (n*%min_interval%)/60/24/31\:d\:2}

:: Formatea la fecha y hora actual como texto.
set text=%init_year%-%month%-%day% %hour%\:%min%

ffmpeg -framerate %framerate% -i %input_path% -vf "drawtext=text='%text%':x=10:y=10:fontsize=24:fontcolor=white" %output_path%

:: -framerate %framerate%: Establece la tasa de fotogramas a %framerate% fps.
:: -i %input_path%: Especifica la ruta de entrada de las imágenes.
:: -vf "drawtext=...": Aplica un filtro de video para dibujar texto en cada fotograma.
:: drawtext=text='%%{eif\:mod(n\,3600)/60\:d\:2}:%%{eif\:mod(n\,60)\:d\:2}':
::     Dibuja un temporizador en el video que muestra minutos y segundos.
::     %%{eif\:mod(n\,3600)/60\:d\:2}: Calcula los minutos transcurridos en el video.
::         eif\: Ejecuta una expresión.
::         mod(n\,3600): Calcula el número de segundos transcurridos en la hora actual.
::         /60: Convierte los segundos en minutos.
::         d\:2: Formatea el número como un entero de dos dígitos.
::     %%{eif\:mod(n\,60)\:d\:2}: Calcula los segundos transcurridos en el minuto actual.
::         eif\: Ejecuta una expresión.
::         mod(n\,60): Calcula el número de segundos transcurridos en el minuto actual.
::         d\:2: Formatea el número como un entero de dos dígitos.
:: x=10:y=10: Establece la posición del texto en las coordenadas (10, 10).
:: fontsize=24: Establece el tamaño de la fuente a 24.
:: fontcolor=white: Establece el color de la fuente a blanco.

pause