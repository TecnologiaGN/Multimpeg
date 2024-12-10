@echo off
:: Establecer la codificación en UTF-8 para manejar caracteres especiales como "ñ"
chcp 65001

:: Obtener la ruta del directorio actual (donde se ejecuta el archivo .bat)
set "ruta=%cd%"



    :: Buscar y eliminar todos los archivos .mp4, .wmv y .mp3 en la carpeta actual y subcarpetas
    del /f /q /s "%ruta%\*.mp4"
    del /f /q /s "%ruta%\*.wmv"
    del /f /q /s "%ruta%\*.mp3"

    echo Archivos eliminados.
) else (
    echo Operación cancelada.
)

pause
