import os
import subprocess
import tkinter as tk
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

    # Verificar si el archivo ya existe
    if check_existing_file(output_name, file_path):
        return

    # Deshabilitar botón y lanzar un hilo
    Thread(target=process_audio, args=(master, file_path, output_name, volume_level), daemon=True).start()


def check_existing_file(output_name, file_path):
    """Verifica si el archivo de salida ya existe en la carpeta de destino."""
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
        output_path = adjust_volume(file_path, output_name, volume_level)
        master.after(0, lambda: messagebox.showinfo("Éxito", f"Audio ajustado con éxito: {output_path}"))
    except Exception as e:
        master.after(0, lambda: messagebox.showerror("Error", f"No se pudo ajustar el audio: {e}"))


def adjust_volume(file_path, output_name, volume_level):
    output_dir = "AudioFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Mantener el formato original del archivo
    file_extension = os.path.splitext(file_path)[1]
    output_path = os.path.join(output_dir, f"{output_name}{file_extension}")

    # Comando para ajustar el volumen
    cmd = [
        "ffmpeg",
        "-i", file_path,
        "-af", f"volume={volume_level}",  # Ajustar el volumen dinámicamente
        output_path,
    ]

    # Ejecutar comando de manera no bloqueante
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Error en ffmpeg: {stderr.decode().strip()}")

    return output_path


if __name__ == "__main__":
    create_audio_uploader_window()
