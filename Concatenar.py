import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, simpledialog  # Importar simpledialog
import threading  # Importar el módulo threading

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

    tk.Button(master, text="Concatenar Videos", command=lambda: threading.Thread(target=process_videos, args=(entry_file1_path, entry_file2_path, entry_output_name)).start()).pack(pady=20)

    center_window(master)

    master.mainloop()

def open_file_dialog(entry_file_path, parent_window):
    # Crear una nueva ventana de nivel superior para evitar que la ventana principal se minimice
    dialog_window = Toplevel(parent_window)
    dialog_window.withdraw()  # Ocultar la nueva ventana

    file_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.wmv;*.avi;*.mov;*.mkv")], parent=parent_window)

    dialog_window.destroy()  # Destruir la ventana emergente después de seleccionar el archivo

    if file_path:  # Solo actualiza si se seleccionó un archivo
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

def process_videos(entry_file1_path, entry_file2_path, entry_output_name):
    file1_path = entry_file1_path.get()
    file2_path = entry_file2_path.get()
    output_name = entry_output_name.get()

    if not file1_path or not file2_path or not output_name:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    if os.path.splitext(file1_path)[1] != os.path.splitext(file2_path)[1]:
        messagebox.showerror("Error", "Los videos deben tener el mismo formato.")
        return

    # Ejecutar en segundo plano usando threading
    try:
        output_path = concatenate_videos(file1_path, file2_path, output_name)
        messagebox.showinfo("Éxito", f"Videos concatenados con éxito: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo concatenar los videos: {e}")

def concatenate_videos(file1_path, file2_path, output_name):
    # Crea la carpeta "ConcatenarFinal" si no existe
    output_dir = "ConcatenarFinal"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Obtener la extensión del primer archivo
    file_ext = os.path.splitext(file1_path)[1].lower()
    output_path = os.path.join(output_dir, f"{output_name}{file_ext}")

    # Verificar si el archivo ya existe
    if os.path.exists(output_path):
        # Mostrar un mensaje de advertencia
        response = messagebox.askyesno("Archivo existente", f"El archivo {output_path} ya existe. ¿Desea cambiar el nombre?")
        if not response:
            # Si el usuario no quiere cambiar el nombre, se aborta la operación
            raise RuntimeError("El archivo ya existe, operación cancelada.")
        else:
            # Si el usuario desea cambiar el nombre, le damos la opción de ingresar uno nuevo
            new_name = simpledialog.askstring("Nuevo nombre", "Ingrese un nuevo nombre para el archivo:")
            if new_name:
                output_path = os.path.join(output_dir, f"{new_name}{file_ext}")
            else:
                raise RuntimeError("No se ha ingresado un nuevo nombre. Operación cancelada.")

    # Obtener el nombre de usuario actual
    username = os.getenv("username")
    if username:
        # Reemplazar el nombre del usuario en las rutas por %username%
        file1_path = file1_path.replace(f"C:\\Users\\{username}\\", "%username%\\")
        file2_path = file2_path.replace(f"C:\\Users\\{username}\\", "%username%\\")

    # Crear un archivo temporal de texto con las rutas de los videos usando UTF-8
    with open("videos.txt", "w", encoding="utf-8") as f:
        f.write(f"file '{file1_path}'\n")
        f.write(f"file '{file2_path}'\n")

    # Comando para concatenar los videos
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'videos.txt',
        '-c', 'copy',
        output_path
    ]

    subprocess.run(cmd, check=True)
    os.remove("videos.txt")  # Eliminar archivo temporal
    return output_path

# Ejecuta esta función si se ejecuta directamente
if __name__ == "__main__":
    create_video_concatenator_window()
