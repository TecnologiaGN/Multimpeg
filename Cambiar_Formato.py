import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

# Lista global de hilos en ejecución
threads = []

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
    # Desactivar solo el botón de selección mientras se procesan los archivos
    status_label.config(text="Procesando...", fg="orange")

    # Obtener los archivos seleccionados
    files = entry_file_path.get().split(';')

    # Crear un hilo para cada archivo
    for file_path in files:
        if file_path.strip():  # Verificar que no esté vacío
            conversion_thread = threading.Thread(target=process_video, args=(file_path.strip(), status_label))
            threads.append(conversion_thread)
            conversion_thread.start()

def process_video(file_path, status_label):
    """Procesar el video para cambiar el formato en un hilo separado"""
    if not file_path:
        messagebox.showerror("Error", "Por favor, seleccione un archivo.")
        return

    try:
        output_path = change_format(file_path)
        status_label.config(text=f"Formato cambiado con éxito: {output_path}", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        messagebox.showerror("Error", f"No se pudo cambiar el formato: {str(e)}")

def change_format(file_path):
    """Convierte el archivo de video a otro formato (WMV o MP4)"""
    ext = os.path.splitext(file_path)[1].lower()

    # Verificar la extensión y determinar el formato de salida
    if ext == ".mp4":
        new_ext = ".wmv"
    elif ext == ".wmv":
        new_ext = ".mp4"
    else:
        raise ValueError("Formato no soportado. Solo se admiten .mp4 y .wmv.")

    # Crear directorio de salida si no existe
    output_dir = "FormatoFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Establecer el archivo de salida
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + new_ext)

    # Verificar si el archivo ya existe en la carpeta de salida
    if os.path.exists(output_path):
        # Preguntar al usuario si quiere reemplazar el archivo
        response = messagebox.askyesno("Archivo existente", f"El archivo {output_path} ya existe. ¿Desea reemplazarlo?")
        if not response:  # Si el usuario elige "No"
            raise RuntimeError(f"El archivo {output_path} no se ha reemplazado.")
    
    # Comando FFmpeg para cambiar el formato
    command = [
        "ffmpeg", "-i", file_path,  # Entrada
        output_path  # Salida
    ]

    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al convertir el video: {e.stderr.decode()}")

    return output_path

if __name__ == "__main__":
    create_format_changer_window()
