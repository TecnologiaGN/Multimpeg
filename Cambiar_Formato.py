import os
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import threading
import re

def create_format_changer_window():
    master = tk.Tk()
    master.title("Cambiar Formato de Video")

    # Centro de la ventana
    center_window(master)

    # Marco para centrar contenido
    frame = tk.Frame(master)
    frame.pack(expand=True)

    # Elementos de la interfaz dentro del marco
    tk.Label(frame, text="Ruta del archivo de video:").pack(pady=5)
    entry_file_path = tk.Entry(frame, width=40)
    entry_file_path.pack(pady=5)

    select_file_button = tk.Button(frame, text="Seleccionar archivo(s)", command=lambda: select_file(entry_file_path, select_file_button))
    select_file_button.pack(pady=5)

    # Etiqueta para mostrar el estado
    status_label = tk.Label(frame, text="Listo para cambiar el formato", fg="green")
    status_label.pack(pady=5)

    # Botón para cambiar el formato
    change_format_button = tk.Button(frame, text="Cambiar formato de video", 
                                     command=lambda: start_conversion_thread(entry_file_path, change_format_button, status_label))
    change_format_button.pack(pady=20)

    master.mainloop()

def select_file(entry_file_path, select_file_button):
    """Permite seleccionar uno o varios archivos de video y lo pone en el entry"""
    select_file_button.config(state=tk.DISABLED)  # Desactivar botón mientras selecciona
    file_paths = filedialog.askopenfilenames(filetypes=[("Archivos de video", "*.mp4;*.wmv")])
    select_file_button.config(state=tk.NORMAL)  # Activar el botón después de la selección

    if file_paths:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, '; '.join(file_paths))  # Mostrar los archivos seleccionados

def center_window(master):
    """Centrar la ventana en la pantalla"""
    width = 500
    height = 400
    master.geometry(f"{width}x{height}")

    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    master.geometry(f"{width}x{height}+{x}+{y}")

def start_conversion_thread(entry_file_path, button, status_label):
    """Inicia la conversión en un hilo separado para no bloquear la UI"""
    status_label.config(text="Procesando...", fg="orange")

    files = entry_file_path.get().split(';')

    for file_path in files:
        if file_path.strip():
            threading.Thread(target=process_video, args=(file_path.strip(), status_label), daemon=True).start()

def process_video(file_path, status_label):
    if not file_path:
        messagebox.showerror("Error", "Por favor, seleccione un archivo.")
        return

    try:
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

        output_path = change_format(file_path, update_progress)
        progress_window.destroy()
        status_label.config(text=f"Formato cambiado con éxito: {output_path}", fg="green")

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        messagebox.showerror("Error", f"No se pudo cambiar el formato: {str(e)}")

def change_format(file_path, progress_callback):
    """Convierte el archivo de video a otro formato (WMV o MP4)"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".mp4":
        new_ext = ".wmv"
    elif ext == ".wmv":
        new_ext = ".mp4"
    else:
        raise ValueError("Formato no soportado. Solo se admiten .mp4 y .wmv.")

    output_dir = "FormatoFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + new_ext)

    if os.path.exists(output_path):
        response = messagebox.askyesno("Archivo existente", f"El archivo {output_path} ya existe. ¿Desea reemplazarlo?")
        if not response:
            raise RuntimeError(f"El archivo {output_path} no se ha reemplazado.")

    command = [
        "ffmpeg", "-i", file_path, output_path
    ]

    process = subprocess.Popen(command, stderr=subprocess.PIPE, universal_newlines=True)

    total_duration = get_video_duration(file_path)
    current_time = 0

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
    create_format_changer_window()
