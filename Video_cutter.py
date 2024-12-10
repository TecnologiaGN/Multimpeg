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

    status_label = tk.Label(master, text="Listo para cortar video", fg="Blue")
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
    file_path = entry_file_path.get()
    inicio = entry_start_time.get()
    fin = entry_end_time.get()

    if not file_path or not inicio or not fin:
        messagebox.showerror("Error", "Por favor, complete todos los campos para la previsualización.")
        return

    start_sec = time_to_seconds(inicio)
    end_sec = time_to_seconds(fin)

    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir el archivo de video.")
        return

    preview_window = tk.Toplevel()
    preview_window.title("Previsualización")

    # Configurar tamaño de la ventana
    preview_window.geometry("800x600")
    preview_window.minsize(600, 400)
    preview_window.maxsize(1200, 800)

    # Canvas para mostrar el video
    canvas = tk.Canvas(preview_window, bg="white")
    canvas.pack(fill="both", expand=True)

    # Controles inferiores
    controls_frame = tk.Frame(preview_window)
    controls_frame.pack(fill="x", side="bottom", padx=5, pady=5)

    time_label = tk.Label(controls_frame, text=f"{inicio} / {fin}")
    time_label.pack(side="left", padx=5)

    is_paused = [False]
    duration = int(end_sec - start_sec)
    progress_var = tk.DoubleVar(value=0)

    def format_time(seconds):
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def toggle_play_pause():
        is_paused[0] = not is_paused[0]
        play_pause_btn.config(text="Reproducir" if is_paused[0] else "Pausar")
        if not is_paused[0]:
            show_frame()

    def reset_to_start():
        cap.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000)
        progress_var.set(0)
        time_label.config(text=f"{format_time(start_sec)} / {format_time(end_sec)}")
        toggle_play_pause()

    def update_frame(target_time=None):
        if target_time is not None:
            cap.set(cv2.CAP_PROP_POS_MSEC, target_time * 1000)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor="nw", image=img_tk)
            canvas.image = img_tk

    def on_progress_change(value):
        target_time = start_sec + float(value)
        update_frame(target_time=target_time)
        time_label.config(text=f"{format_time(target_time)} / {format_time(end_sec)}")

    def show_frame():
        if not is_paused[0]:
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)
                canvas.create_image(0, 0, anchor="nw", image=img_tk)
                canvas.image = img_tk

                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                progress_var.set(current_time - start_sec)
                time_label.config(text=f"{format_time(current_time)} / {format_time(end_sec)}")

                if current_time < end_sec:
                    preview_window.after(20, show_frame)
                else:
                    reset_to_start()
            else:
                reset_to_start()

    # Barra de progreso
    progress_bar = tk.Scale(
        controls_frame,
        variable=progress_var,
        orient="horizontal",
        length=500,
        from_=0,
        to=duration,
        showvalue=False,
        sliderlength=20,
        command=lambda value: on_progress_change(value),
    )
    progress_bar.pack(side="left", padx=5)

    # Botones de control
    play_pause_btn = tk.Button(controls_frame, text="Pausar", command=toggle_play_pause)
    play_pause_btn.pack(side="left", padx=5)

    reset_btn = tk.Button(controls_frame, text="Reiniciar", command=reset_to_start)
    reset_btn.pack(side="left", padx=5)

    show_frame()


if __name__ == "__main__":
    create_video_cutter_window()
