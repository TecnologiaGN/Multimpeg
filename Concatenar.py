import os
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, Toplevel, simpledialog
import threading
import re

def create_video_concatenator_window():
    master = tk.Tk()
    master.title("Concatenar Videos")

    # Elementos de la interfaz 
    tk.Label(master, text="Seleccionar Video 1:").pack(pady=10)
    entry_file1_path = tk.Entry(master, width=40)
    entry_file1_path.pack(pady=5)

    tk.Button(master, text="Seleccionar Video 1", command=lambda: open_file_dialog(entry_file1_path, master)).pack(pady=5)

    tk.Label(master, text="Seleccionar Video 2:").pack(pady=10)
    entry_file2_path = tk.Entry(master, width=40)
    entry_file2_path.pack(pady=5)

    tk.Button(master, text="Seleccionar Video 2", command=lambda: open_file_dialog(entry_file2_path, master)).pack(pady=5)

    tk.Label(master, text="Nombre de salida:").pack(pady=5)
    entry_output_name = tk.Entry(master, width=20)
    entry_output_name.pack(pady=5)

    status_label = tk.Label(master, text="Listo para concatenar", fg="Blue")
    status_label.pack(pady=10)

    tk.Button(master, text="Concatenar Videos", command=lambda: threading.Thread(target=process_videos, args=(entry_file1_path, entry_file2_path, entry_output_name, status_label)).start()).pack(pady=20)

    center_window(master)
    master.mainloop()

def open_file_dialog(entry_file_path, parent_window):
    dialog_window = Toplevel(parent_window)
    dialog_window.withdraw()

    file_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.wmv")], parent=parent_window)

    dialog_window.destroy()

    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def center_window(master):
    width = 500
    height = 450
    master.geometry(f"{width}x{height}")

    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    master.geometry(f"{width}x{height}+{x}+{y}")

def process_videos(entry_file1_path, entry_file2_path, entry_output_name, status_label):
    file1_path = entry_file1_path.get()
    file2_path = entry_file2_path.get()
    output_name = entry_output_name.get()

    if not file1_path or not file2_path or not output_name:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    if os.path.splitext(file1_path)[1] != os.path.splitext(file2_path)[1]:
        messagebox.showerror("Error", "Los videos deben tener el mismo formato.")
        return

    try:
        progress_window = tk.Toplevel()
        progress_window.title("Concatenando Videos")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)

        progress_label = tk.Label(progress_window, text="Iniciando concatenación...", wraplength=250)
        progress_label.pack(pady=10)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(padx=20, pady=10, fill='x')

        percentage_label = tk.Label(progress_window, text="0%")
        percentage_label.pack()

        status_label.config(text="Procesando...", fg="orange")

        def update_progress(percentage):
            progress_var.set(percentage)
            percentage_label.config(text=f"{percentage:.1f}%")
            progress_window.update()

        def run_concatenation_process():
            try:
                output_path = concatenate_videos(file1_path, file2_path, output_name, update_progress)
                progress_window.destroy()
                status_label.config(text=f"Videos concatenados exitosamente", fg="green")
                messagebox.showinfo("Éxito", f"Videos concatenados con éxito: {output_path}")
            except Exception as e:
                progress_window.destroy()
                status_label.config(text="Error al concatenar videos", fg="red")
                messagebox.showerror("Error", f"No se pudo concatenar los videos: {e}")

        threading.Thread(target=run_concatenation_process, daemon=True).start()

    except Exception as e:
        status_label.config(text="Error al concatenar videos", fg="red")
        messagebox.showerror("Error", f"No se pudo concatenar los videos: {e}")

def get_video_duration(file_path):
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return float(result.stdout.strip())
    except Exception:
        return 0

def concatenate_videos(file1_path, file2_path, output_name, progress_callback):
    output_dir = "ConcatenarFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_ext = os.path.splitext(file1_path)[1].lower()
    output_path = os.path.join(output_dir, f"{output_name}{file_ext}")

    if os.path.exists(output_path):
        response = messagebox.askyesno("Archivo existente", f"El archivo {output_path} ya existe. ¿Desea cambiar el nombre?")
        if not response:
            raise RuntimeError("El archivo ya existe, operación cancelada.")
        else:
            new_name = simpledialog.askstring("Nuevo nombre", "Ingrese un nuevo nombre para el archivo:")
            if new_name:
                output_path = os.path.join(output_dir, f"{new_name}{file_ext}")
            else:
                raise RuntimeError("No se ha ingresado un nuevo nombre. Operación cancelada.")

    total_duration = get_video_duration(file1_path) + get_video_duration(file2_path)

    username = os.getenv("username")
    if username:
        file1_path = file1_path.replace(f"C:\\Users\\{username}\\", "%username%\\")
        file2_path = file2_path.replace(f"C:\\Users\\{username}\\", "%username%\\")

    with open("videos.txt", "w", encoding="utf-8") as f:
        f.write(f"file '{file1_path}'\n")
        f.write(f"file '{file2_path}'\n")

    def run_ffmpeg_with_progress(cmd):
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

        current_time = 0
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break

            time_match = re.search(r'time=(\d+:\d+:\d+\.\d+)', output)
            if time_match:
                h, m, s = map(float, time_match.group(1).split(':'))
                current_time = h * 3600 + m * 60 + s
                progress = min(100, (current_time / total_duration) * 100)
                progress_callback(progress)

        progress_callback(100)
        return process.poll() == 0

    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'videos.txt',
        '-c', 'copy',
        output_path
    ]

    if not run_ffmpeg_with_progress(cmd):
        os.remove("videos.txt")
        raise Exception("Error en el proceso de concatenación de video")

    os.remove("videos.txt")
    return output_path

if __name__ == "__main__":
    create_video_concatenator_window()
