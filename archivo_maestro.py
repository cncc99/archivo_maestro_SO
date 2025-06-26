import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Listbox, Scrollbar, StringVar, BooleanVar
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import shutil
import logging
from pathlib import Path
import mimetypes
import threading
import re
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    filename='organizador.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Inicializar mimetypes
mimetypes.init()

class FileOrganizerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Organizador Avanzado de Archivos Universitarios")
        self.geometry("900x750")
        self.configure(bg="#f0f0f0")
        
        # Variables
        self.target_path = StringVar(value="")
        self.dragged_files = []
        self.dry_run = BooleanVar(value=False)
        self.progress = StringVar(value="Listo")
        self.running = False
        self.organize_by_course = BooleanVar(value=True)
        self.organize_by_type = BooleanVar(value=True)
        
        # Diccionario de abreviaturas de cursos universitarios
        self.course_abbreviations = {
            # Patrones comunes para nombres de cursos
            'BD': 'Base de Datos',
            'BASEDATOS': 'Base de Datos',
            'DB': 'Base de Datos',
            'DATABASE': 'Base de Datos',
            'PROG': 'Programación',
            'PROGRAMACION': 'Programación',
            'ALG': 'Algoritmos',
            'ALGORITMOS': 'Algoritmos',
            'CALC': 'Cálculo',
            'CALCULO': 'Cálculo',
            'FIS': 'Física',
            'FISICA': 'Física',
            'QUIM': 'Química',
            'QUIMICA': 'Química',
            'REDES': 'Redes de Computadoras',
            'REDESCOMP': 'Redes de Computadoras',
            'SO': 'Sistemas Operativos',
            'SISTOP': 'Sistemas Operativos',
            'IA': 'Inteligencia Artificial',
            'INTELART': 'Inteligencia Artificial',
            'ML': 'Machine Learning',
            'MACHINELEARN': 'Machine Learning',
            'WEB': 'Desarrollo Web',
            'DESWEB': 'Desarrollo Web',
            'MOVIL': 'Desarrollo Móvil',
            'DESMOVIL': 'Desarrollo Móvil',
            'SEG': 'Seguridad Informática',
            'SEGINFO': 'Seguridad Informática',
            'INGSOFT': 'Ingeniería de Software',
            'IS': 'Ingeniería de Software',
            'ARQCOMP': 'Arquitectura de Computadoras',
            'ARQ': 'Arquitectura de Computadoras',
            'COMP': 'Compiladores',
            'COMPIL': 'Compiladores',
            'GRAF': 'Graficación',
            'GRAFICOS': 'Graficación',
            'BDD': 'Bases de Datos Distribuidas',
            'BDIST': 'Bases de Datos Distribuidas',
            'TGS': 'Teoría General de Sistemas',
            'TEOGS': 'Teoría General de Sistemas',
            'LENG': 'Lenguajes de Programación',
            'LENPROG': 'Lenguajes de Programación',
            'PARA': 'Programación Paralela',
            'PARALELA': 'Programación Paralela',
            'EMB': 'Sistemas Embebidos',
            'EMBEBIDOS': 'Sistemas Embebidos',
            'ROB': 'Robótica',
            'ROBOTICA': 'Robótica',
            'CIENCDAT': 'Ciencia de Datos',
            'CD': 'Ciencia de Datos',
            'BIGDATA': 'Big Data',
            'BDATA': 'Big Data',
            'CLOUD': 'Computación en la Nube',
            'NUBE': 'Computación en la Nube',
            'IOT': 'Internet de las Cosas',
            'IDC': 'Internet de las Cosas',
            'BLOCK': 'Blockchain',
            'CADENA': 'Blockchain',
            'CRIPTO': 'Criptografía',
            'CRIP': 'Criptografía',
            'SIM': 'Simulación',
            'SIMUL': 'Simulación',
            'HPC': 'Computación de Alto Rendimiento',
            'ALTO': 'Computación de Alto Rendimiento',
            'VISION': 'Visión por Computadora',
            'VISCOMP': 'Visión por Computadora',
            'NLP': 'Procesamiento de Lenguaje Natural',
            'PLN': 'Procesamiento de Lenguaje Natural',
            'UX': 'Experiencia de Usuario',
            'UI': 'Interfaz de Usuario',
            'TEST': 'Pruebas de Software',
            'PRUEBAS': 'Pruebas de Software',
            'CAL1': 'Cálculo I',
            'CAL2': 'Cálculo II',
            'CAL3': 'Cálculo III',
            'FIS1': 'Física I',
            'FIS2': 'Física II',
            'FIS3': 'Física III',
            'LIN': 'Álgebra Lineal',
            'LINEAL': 'Álgebra Lineal',
            'DISCR': 'Matemática Discreta',
            'MDIS': 'Matemática Discreta',
            'ESTAD': 'Estadística',
            'EST': 'Estadística',
            'PROBA': 'Probabilidad',
            'PROB': 'Probabilidad',
            'ECON': 'Economía',
            'ECO': 'Economía',
            'ADM': 'Administración',
            'ADMIN': 'Administración',
            'CONT': 'Contabilidad',
            'CONTA': 'Contabilidad',
            'MARK': 'Marketing',
            'MKT': 'Marketing',
            'DER': 'Derecho',
            'DERECHO': 'Derecho',
            'FILO': 'Filosofía',
            'FILOS': 'Filosofía',
            'PSIC': 'Psicología',
            'PSICO': 'Psicología',
            'SOC': 'Sociología',
            'SOCIO': 'Sociología',
            'HIST': 'Historia',
            'HISTORIA': 'Historia',
            'LIT': 'Literatura',
            'LITER': 'Literatura',
            'IDIOM': 'Idiomas',
            'INGL': 'Inglés',
            'INGLES': 'Inglés'
        }
        
        # Crear widgets
        self.create_widgets()
    
    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("vista")
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", background="#0E0F0E", foreground="white")
        style.map("Accent.TButton", background=[("active", "#000000")])
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Organizador de Archivos Universitarios", style="Title.TLabel").pack(pady=(0, 15))
        
        # Sección de ubicación de destino
        location_frame = ttk.LabelFrame(main_frame, text="Ubicación de Destino")
        location_frame.pack(fill="x", pady=10)
        
        ttk.Label(location_frame, text="Carpeta para organización:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        path_entry = ttk.Entry(location_frame, textvariable=self.target_path, width=50)
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Button(
            location_frame, 
            text="Seleccionar...", 
            command=self.browse_folder
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Opciones de organización
        options_frame = ttk.LabelFrame(main_frame, text="Opciones de Organización")
        options_frame.pack(fill="x", pady=10)
        
        ttk.Checkbutton(
            options_frame,
            text="Organizar por curso universitario",
            variable=self.organize_by_course
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        ttk.Checkbutton(
            options_frame,
            text="Organizar por tipo de archivo dentro de cada curso",
            variable=self.organize_by_type
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        ttk.Checkbutton(
            options_frame,
            text="Modo prueba (no mueve archivos)",
            variable=self.dry_run
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Área de arrastre
        drop_frame = ttk.LabelFrame(main_frame, text="Arrastra archivos aquí")
        drop_frame.pack(fill="both", expand=True, pady=10)
        
        list_frame = ttk.Frame(drop_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            height=12,
            bg="white",
            relief="sunken",
            yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)
        
        # Botones de gestión de archivos
        file_btn_frame = ttk.Frame(main_frame)
        file_btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            file_btn_frame, 
            text="Agregar archivos...", 
            command=self.add_files
        ).pack(side="left", padx=2)
        
        ttk.Button(
            file_btn_frame, 
            text="Eliminar seleccionados", 
            command=self.remove_selected_files
        ).pack(side="left", padx=2)
        
        ttk.Button(
            file_btn_frame, 
            text="Limpiar todos", 
            command=self.clear_all_files
        ).pack(side="left", padx=2)
        
        # Botón de organización
        self.organize_btn = ttk.Button(
            main_frame, 
            text="Organizar Archivos", 
            style="Accent.TButton",
            command=self.start_organization_thread
        )
        self.organize_btn.pack(pady=15)
        
        # Barra de progreso
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill="x", pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, textvariable=self.progress)
        self.progress_label.pack(fill="x", pady=5)
        
        # Barra de estado
        self.status = ttk.Label(self, text="Arrastra archivos a la lista o usa 'Agregar archivos'")
        self.status.pack(side="bottom", fill="x", padx=10, pady=5)
        
        self.drop_target_register('DND_Files')
        self.dnd_bind('<<Drop>>', self.on_drop)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_path.set(folder)
    
    def on_drop(self, event):
        files = self.parse_dropped_files(event.data)
        for file in files:
            if file not in self.dragged_files and os.path.isfile(file):
                self.dragged_files.append(file)
                self.file_listbox.insert("end", os.path.basename(file))
        self.status.config(text=f"{len(self.dragged_files)} archivos listos para organizar")
    
    def parse_dropped_files(self, data):
        files = []
        if isinstance(data, str):
            for item in data.split():
                path = item.strip('{}')
                if os.path.exists(path):
                    files.append(path)
        elif isinstance(data, list):
            for path in data:
                if os.path.exists(path):
                    files.append(path)
        return files
    
    def add_files(self):
        files = filedialog.askopenfilenames()
        if files:
            for file in files:
                if file not in self.dragged_files:
                    self.dragged_files.append(file)
                    self.file_listbox.insert("end", os.path.basename(file))
            self.status.config(text=f"{len(self.dragged_files)} archivos listos para organizar")
    
    def remove_selected_files(self):
        selected = self.file_listbox.curselection()
        for index in selected[::-1]:
            self.file_listbox.delete(index)
            self.dragged_files.pop(index)
        self.status.config(text=f"{len(self.dragged_files)} archivos listos para organizar")
    
    def clear_all_files(self):
        self.file_listbox.delete(0, "end")
        self.dragged_files = []
        self.status.config(text="Lista de archivos vacía")
    
    def start_organization_thread(self):
        """Inicia el proceso en un hilo separado para no bloquear la GUI"""
        if not self.target_path.get():
            messagebox.showerror("Error", "Seleccione una ubicación de destino")
            return
            
        if not self.dragged_files:
            messagebox.showerror("Error", "Agregue al menos un archivo para organizar")
            return
        
        if self.running:
            return
        
        self.running = True
        self.organize_btn.config(state="disabled")
        self.progress.set("Iniciando organización...")
        
        # Iniciar hilo
        threading.Thread(target=self.organize_files, daemon=True).start()
    
    def detect_course_from_filename(self, filename):
        """Detecta el curso universitario basado en el nombre del archivo"""
        # Convertir a mayúsculas y eliminar espacios
        filename_upper = filename.upper().replace(" ", "")
        
        # Buscar coincidencias exactas primero
        for abbr, full_name in self.course_abbreviations.items():
            # Patrón para buscar la abreviatura como palabra completa
            pattern = r'(^|_|\W)' + re.escape(abbr) + r'($|_|\W)'
            if re.search(pattern, filename_upper):
                return full_name
        
        # Si no encuentra coincidencia exacta, buscar parciales
        for abbr, full_name in self.course_abbreviations.items():
            if abbr in filename_upper:
                return full_name
        
        # Si no encuentra nada, devolver "Otros Cursos"
        return "Otros Cursos"
    
    def get_file_category(self, mime_type):
        """Determina la categoría del archivo basado en su tipo MIME"""
        # Categorías basadas en tipo MIME
        categories = {
            # Documentos
            'application/pdf': 'Documentos',
            'application/msword': 'Documentos',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Documentos',
            'application/vnd.oasis.opendocument.text': 'Documentos',
            'text/plain': 'Documentos',
            'application/rtf': 'Documentos',
            'application/x-tex': 'Documentos',
            
            # Hojas de Cálculo
            'application/vnd.ms-excel': 'Hojas de Calculo',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Hojas de Calculo',
            'application/vnd.oasis.opendocument.spreadsheet': 'Hojas de Calculo',
            'text/csv': 'Hojas de Calculo',
            
            # Presentaciones
            'application/vnd.ms-powerpoint': 'Presentaciones',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'Presentaciones',
            'application/vnd.oasis.opendocument.presentation': 'Presentaciones',
            
            # Imágenes
            'image/jpeg': 'Imagenes',
            'image/png': 'Imagenes',
            'image/gif': 'Imagenes',
            'image/bmp': 'Imagenes',
            'image/svg+xml': 'Imagenes',
            
            # Videos
            'video/mp4': 'Videos',
            'video/quicktime': 'Videos',
            'video/x-msvideo': 'Videos',
            'video/x-matroska': 'Videos',
            
            # Audio
            'audio/mpeg': 'Audio',
            'audio/wav': 'Audio',
            'audio/flac': 'Audio',
            
            # Archivos Comprimidos
            'application/zip': 'Archivos Comprimidos',
            'application/x-rar-compressed': 'Archivos Comprimidos',
            'application/x-7z-compressed': 'Archivos Comprimidos',
            
            # Código
            'text/x-python': 'Codigo',
            'application/javascript': 'Codigo',
            'text/html': 'Codigo',
            'text/css': 'Codigo',
            'application/json': 'Codigo',
            
            # Por defecto
            'application/octet-stream': 'Otros'
        }
        
        return categories.get(mime_type, 'Otros')
    
    def organize_files(self):
        """Proceso principal de organización"""
        target_path = Path(self.target_path.get())
        organized_folder = target_path / "Archivos Universitarios Ordenados"
        
        # Crear carpeta principal si no existe
        if not organized_folder.exists():
            organized_folder.mkdir(parents=True, exist_ok=True)
        
        # Contadores
        total_files = len(self.dragged_files)
        processed = 0
        duplicates = 0
        
        # Procesar cada archivo
        for file_path in self.dragged_files:
            if not self.running:
                break
                
            src = Path(file_path)
            if not src.exists():
                logging.error(f"Archivo no encontrado: {file_path}")
                continue
            
            # Determinar tipo MIME usando mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'  # Tipo por defecto
            
            # Determinar curso universitario
            course_name = "Otros Cursos"
            if self.organize_by_course.get():
                course_name = self.detect_course_from_filename(src.stem)
            
            # Determinar categoría de archivo
            file_category = "Otros"
            if self.organize_by_type.get():
                file_category = self.get_file_category(mime_type)
            
            # Estructura de carpetas dependiendo de las opciones seleccionadas
            if self.organize_by_course.get() and self.organize_by_type.get():
                # Carpeta Curso > Tipo de Archivo
                dest_folder = organized_folder / course_name / file_category
            elif self.organize_by_course.get():
                # Solo Carpeta Curso
                dest_folder = organized_folder / course_name
            elif self.organize_by_type.get():
                # Solo Carpeta Tipo de Archivo
                dest_folder = organized_folder / file_category
            else:
                # Sin organización, solo en la carpeta principal
                dest_folder = organized_folder
            
            # Crear carpeta destino si no existe
            if not dest_folder.exists():
                dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Nombre destino
            dest = dest_folder / src.name
            
            # Verificar duplicados
            if dest.exists():
                # Generar nombre único
                counter = 1
                while dest.exists():
                    new_name = f"{src.stem}_{counter}{src.suffix}"
                    dest = dest_folder / new_name
                    counter += 1
                duplicates += 1
            
            # Mover o copiar (según modo)
            self.progress.set(f"Procesando: {src.name}...")
            logging.info(f"Procesando: {src.name} -> {dest}")
            
            try:
                if not self.dry_run.get() and self.running:
                    # Mover archivo
                    shutil.move(str(src), str(dest))
            except Exception as e:
                logging.error(f"Error moviendo {src}: {str(e)}")
            
            processed += 1
            self.progress.set(f"Procesados: {processed}/{total_files}")
        
        # Finalización
        if self.running:
            self.progress.set("Organización completada!")
            message = (
                f"Organización {'simulada' if self.dry_run.get() else 'completada'} con éxito!\n"
                f"Total archivos: {total_files}\n"
                f"Duplicados encontrados: {duplicates}"
            )
            messagebox.showinfo("Éxito", message)
            if not self.dry_run.get() and self.running:
                # Abrir carpeta destino
                os.startfile(organized_folder)
                # Limpiar lista
                self.after(100, self.clear_all_files)
        else:
            self.progress.set("Organización cancelada")
        
        self.running = False
        self.organize_btn.config(state="normal")
    
    def on_closing(self):
        """Manejar cierre de ventana durante operación"""
        if self.running:
            if messagebox.askokcancel("Salir", "La organización está en progreso. ¿Desea cancelar y salir?"):
                self.running = False
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()