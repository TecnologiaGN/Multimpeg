import os
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import threading
import re

def create_reduce_video_size_window():
    master = tk.Tk()
    master.title("Reducir Tamaño de Video")

    # Centro de la ventana
    center_window(master)

    # Marco para centrar contenido
    frame = tk.Frame(master)
    frame.pack(expand=True)

    # Elementos de la interfaz dentro del marco
    tk.Label(frame, text="Ruta del archivo de video:").pack(pady=5)
    entry_file_path = tk.Entry(frame, width=40)
    entry_file_path.pack(pady=5)

    select_file_button = tk.Button(frame, text="Seleccionar archivo", command=lambda: select_file(entry_file_path, select_file_button))
    select_file_button.pack(pady=5)

    tk.Label(frame, text="Nombre de salida (sin extensión):").pack(pady=5)
    entry_output_name = tk.Entry(frame, width=20)
    entry_output_name.pack(pady=5)

    tk.Button(frame, text="Bajar Peso", command=lambda: threading.Thread(target=process_video, args=(entry_file_path, entry_output_name)).start()).pack(pady=20)

    master.mainloop()

def select_file(entry_file_path, select_file_button):
    select_file_button.config(state=tk.DISABLED)
    file_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.avi;*.wmv;*.mkv")])
    select_file_button.config(state=tk.NORMAL)

    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def center_window(master):
    width = 500
    height = 400
    master.geometry(f"{width}x{height}")

    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    master.geometry(f"{width}x{height}+{x}+{y}")

def process_video(entry_file_path, entry_output_name):
    file_path = entry_file_path.get()
    output_name = entry_output_name.get()

    if not file_path or not output_name:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    try:
        # Verificar si el archivo ya existe en la carpeta de destino
        output_path = check_file_exists(output_name, file_path)
        if output_path:
            messagebox.showerror("Error", f"El archivo '{output_path}' ya existe en la carpeta de destino. Elija otro nombre.")
            return

        progress_window = tk.Toplevel()
        progress_window.title("Procesando Video")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)

        progress_label = tk.Label(progress_window, text="Iniciando procesamiento...", wraplength=250)
        progress_label.pack(pady=10)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(padx=20, pady=10, fill='x')

        percentage_label = tk.Label(progress_window, text="0%")
        percentage_label.pack()

        def update_progress(percentage):
            progress_var.set(percentage)
            percentage_label.config(text=f"{percentage:.1f}%")
            progress_window.update()

        output_path = reduce_video_size(file_path, output_name, update_progress)
        progress_window.destroy()
        messagebox.showinfo("Éxito", f"Tamaño de video reducido con éxito: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo reducir el tamaño del video: {e}")

def check_file_exists(output_name, file_path):
    output_dir = "PesoFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_extension = os.path.splitext(file_path)[1]
    output_path = os.path.join(output_dir, f"{output_name}{file_extension}")

    # Verificar si el archivo ya existe
    if os.path.exists(output_path):
        return output_path
    return None

def reduce_video_size(file_path, output_name, progress_callback):
    output_dir = "PesoFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_extension = os.path.splitext(file_path)[1]
    output_path = os.path.join(output_dir, f"{output_name}{file_extension}")

    # Seleccionar comando dependiendo del formato del archivo
    if file_extension.lower() == ".mp4":
        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-vf', 'scale=640:480',  # Escalar a resolución 640x480
            '-c:v', 'libx264',       # Codec de video H.264 (compatible con MP4)
            '-b:v', '1M',            # Bitrate reducido (ajusta según necesidad)
            '-c:a', 'aac',           # Codec de audio AAC
            '-b:a', '128k',          # Bitrate de audio reducido
            '-preset', 'fast',       # Velocidad de procesamiento rápida
            '-y',                    # Sobrescribe si el archivo de salida ya existe
            output_path
        ]

    elif file_extension.lower() == ".wmv":
        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-vf', 'scale=640:480',  # Resolución baja para máxima velocidad
            '-c:v', 'wmv2',          # Códec WMV2 para la máxima compatibilidad con Windows Media Player
            '-b:v', '1M',            # Bitrate menor para reducir tamaño
            '-c:a', 'wmav2',         # Códec de audio WMAV2 para la compatibilidad
            '-b:a', '128k',          # Bitrate de audio reducido
            '-y',                    # Sobrescribe si el archivo de salida ya existe
            output_path
        ]
    else:
        raise ValueError("Formato no soportado para reducción de tamaño.")

    total_duration = get_video_duration(file_path)
    current_time = 0

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    while True:
        output = process.stderr.readline()
        if output == '' and process.poll() is not None:
            break

        time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', output)
        if time_match:
            h, m, s = map(float, time_match.groups())
            current_time = h * 3600 + m * 60 + s
            progress = min(100, (current_time / total_duration) * 100)
            progress_callback(progress)

    progress_callback(100)

    if process.poll() != 0:
        raise RuntimeError("Error en ffmpeg")

    return output_path

def get_video_duration(file_path):
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return float(result.stdout.strip())

if __name__ == "__main__":
    create_reduce_video_size_window()
