import os
import re
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from threading import Thread

def create_audio_uploader_window():
    master = tk.Tk()
    master.title("Subir Audio")

    tk.Label(master, text="Ruta del archivo de audio:").pack(pady=5)
    entry_file_path = tk.Entry(master, width=40)
    entry_file_path.pack(pady=5)

    tk.Button(master, text="Seleccionar archivo", command=lambda: select_file(entry_file_path)).pack(pady=5)

    tk.Label(master, text="Nombre de salida:").pack(pady=5)
    entry_output_name = tk.Entry(master, width=20)
    entry_output_name.pack(pady=5)

    tk.Label(master, text="Ajustar volumen (x):").pack(pady=5)
    volume_scale = tk.Scale(master, from_=0.5, to=3, resolution=0.1, orient=tk.HORIZONTAL)
    volume_scale.set(2)  # Volumen predeterminado
    volume_scale.pack(pady=5)

    tk.Button(
        master,
        text="Subir audio",
        command=lambda: start_audio_processing(
            master, entry_file_path.get(), entry_output_name.get(), volume_scale.get()
        ),
    ).pack(pady=20)

    center_window(master)
    master.mainloop()

def select_file(entry_file_path):
    file_path = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.*")])
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

def start_audio_processing(master, file_path, output_name, volume_level):
    if not file_path or not output_name:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    if check_existing_file(output_name, file_path):
        return

    Thread(target=process_audio, args=(master, file_path, output_name, volume_level), daemon=True).start()

def check_existing_file(output_name, file_path):
    output_dir = "AudioFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_extension = os.path.splitext(file_path)[1]
    output_path = os.path.join(output_dir, f"{output_name}{file_extension}")

    if os.path.exists(output_path):
        messagebox.showwarning(
            "Archivo existente",
            f"El archivo '{output_name}{file_extension}' ya existe en la carpeta {output_dir}. Por favor, elija otro nombre.",
        )
        return True

    return False

def process_audio(master, file_path, output_name, volume_level):
    try:
        progress_window = tk.Toplevel()
        progress_window.title("Procesando Audio")
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

        def run_audio_process():
            try:
                output_path = adjust_volume(file_path, output_name, volume_level, update_progress)
                progress_window.destroy()
                messagebox.showinfo("Éxito", f"Audio ajustado con éxito: {output_path}")
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Error", f"No se pudo ajustar el audio: {e}")

        Thread(target=run_audio_process, daemon=True).start()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar el proceso de audio: {e}")

def adjust_volume(file_path, output_name, volume_level, progress_callback):
    output_dir = "AudioFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_extension = os.path.splitext(file_path)[1]
    output_path = os.path.join(output_dir, f"{output_name}{file_extension}")

    cmd = [
        "ffmpeg",
        "-i", file_path,
        "-af", f"volume={volume_level}",
        output_path,
    ]

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    total_duration = get_audio_duration(file_path)
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

def get_audio_duration(file_path):
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
    create_audio_uploader_window()
