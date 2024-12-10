import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import threading

def create_video_cutter_window():
    master = tk.Tk()
    master.title("Cortador de Video")

    # Elementos de la interfaz
    tk.Label(master, text="Ruta del archivo de video:").pack(pady=10)
    entry_file_path = tk.Entry(master, width=40)
    entry_file_path.pack(pady=5)

    label_duration = tk.Label(master, text="Duración del video: 00:00:00")
    label_duration.pack(pady=5)

    tk.Button(master, text="Seleccionar archivo", command=lambda: select_file(entry_file_path, label_duration)).pack(pady=5)

    tk.Label(master, text="Tiempo de inicio (hh:mm:ss):").pack(pady=5)
    entry_start_time = tk.Entry(master, width=10)
    entry_start_time.pack(pady=5)

    tk.Label(master, text="Tiempo de fin (hh:mm:ss):").pack(pady=5)
    entry_end_time = tk.Entry(master, width=10)
    entry_end_time.pack(pady=5)

    tk.Label(master, text="Nombre de salida:").pack(pady=5)
    entry_output_name = tk.Entry(master, width=20)
    entry_output_name.pack(pady=5)

    status_label = tk.Label(master, text="Listo para cortar video", fg="blue")
    status_label.pack(pady=10)

    tk.Button(master, text="Cortar Video", command=lambda: start_cut_video_thread(entry_file_path, entry_start_time, entry_end_time, entry_output_name, label_duration, status_label)).pack(pady=20)

    tk.Button(master, text="Probar Previsualización", command=lambda: start_preview_thread(entry_file_path, entry_start_time, entry_end_time)).pack(pady=5)

    center_window(master)
    master.mainloop()

def start_cut_video_thread(entry_file_path, entry_start_time, entry_end_time, entry_output_name, label_duration, status_label):
    threading.Thread(target=cut_video, args=(entry_file_path, entry_start_time, entry_end_time, entry_output_name, label_duration, status_label)).start()

def start_preview_thread(entry_file_path, entry_start_time, entry_end_time):
    threading.Thread(target=preview_video, args=(entry_file_path, entry_start_time, entry_end_time)).start()

def select_file(entry_file_path, label_duration):
    file_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.wmv;*.avi;*.mov;*.mkv;*.mp3;*.aac")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(0, file_path)

    duration = get_video_duration(file_path)
    label_duration.config(text=f"Duración del video: {duration}")

def center_window(master):
    width = 600
    height = 500
    master.geometry(f"{width}x{height}")

    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    master.geometry(f"{width}x{height}+{x}+{y}")

def time_to_seconds(time_str):
    """Convierte un tiempo en formato hh:mm:ss a segundos."""
    try:
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        raise ValueError("El formato del tiempo debe ser hh:mm:ss")

def get_video_duration(file_path):
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        duration = float(result.stdout.strip())
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    except Exception as e:
        print(f"Error al obtener la duración del video: {e}")
        return "00:00:00"

def cut_video(entry_file_path, entry_start_time, entry_end_time, entry_output_name, label_duration, status_label):
    file_path = entry_file_path.get()
    inicio = entry_start_time.get()
    fin = entry_end_time.get()
    output_name = entry_output_name.get()

    if not file_path or not inicio or not fin or not output_name:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    # Obtener la duración del video y convertirla a segundos
    duration_str = label_duration.cget("text").split(": ")[1]
    duration_seconds = time_to_seconds(duration_str)

    # Validar que el tiempo de fin no sea mayor que la duración del video
    fin_segundos = time_to_seconds(fin)
    if fin_segundos > duration_seconds:
        messagebox.showerror("Error", "El tiempo ingresado en la casilla de Tiempo de fin es mayor que la duración del video seleccionado.")
        return

    # Verificar si el archivo con el nombre de salida ya existe en la carpeta VideoFinal
    output_path = os.path.join("VideoFinal", f"{output_name}{os.path.splitext(file_path)[1]}")
    if os.path.exists(output_path):
        messagebox.showerror("Error", "El nombre existe en la carpeta. Elija otro.")
        return

    try:
        status_label.config(text="Procesando...", fg="orange")
        output_path = process_video(file_path, inicio, fin, output_name)
        status_label.config(text=f"Video '{output_name}' cortado", fg="green")
        messagebox.showinfo("Éxito", f"Video cortado con éxito: {output_path}")
    except Exception as e:
        status_label.config(text="Error al cortar el video", fg="red")
        messagebox.showerror("Error", f"No se pudo cortar el video: {e}")

def process_video(file_path, inicio, fin, output_name):
    inicio_segundos = time_to_seconds(inicio)
    fin_segundos = time_to_seconds(fin)

    if fin_segundos <= inicio_segundos:
        raise ValueError('El tiempo de fin debe ser mayor que el tiempo de inicio')

    duracion_segundos = fin_segundos - inicio_segundos
    file_extension = os.path.splitext(file_path)[1]
    output_path = os.path.join("VideoFinal", f"{output_name}{file_extension}")

    if not os.path.exists("VideoFinal"):
        os.makedirs("VideoFinal")

    # Procesamiento para MP4
    if file_extension.lower() == '.mp4':
        cmd = [
            'ffmpeg',
            '-ss', str(inicio_segundos),
            '-i', file_path,
            '-t', str(duracion_segundos),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-movflags', 'faststart',
            '-loglevel', 'quiet',  # Suprimir salida en CMD
            output_path
        ]
        subprocess.run(cmd, check=True)

    # Procesamiento para WMV
    elif file_extension.lower() == '.wmv':
        cmd_wmv = [
            'ffmpeg',
            '-i', file_path,
            '-ss', str(inicio_segundos + 1),  # Agregar un segundo para evitar congelamiento
            '-t', str(duracion_segundos),
            '-c:v', 'wmv2',
            '-c:a', 'wmav2',
            '-b:v', '1024k',
            '-b:a', '128k',
            '-strict', 'experimental',
            '-movflags', 'faststart',
            output_path
        ]
        subprocess.run(cmd_wmv, check=True)

    return output_path

def preview_video(entry_file_path, entry_start_time, entry_end_time):
    # Aquí puedes mantener el código original sin cambios, si es funcional.
    pass

if __name__ == "__main__":
    create_video_cutter_window()
