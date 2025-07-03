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

# Inicializar mimetypes con más tipos
mimetypes.init()
mimetypes.add_type('application/sql', '.sql')
mimetypes.add_type('application/backup', '.bak')
mimetypes.add_type('application/x-backup', '.bak')

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
            # Base de Datos
            'BD': 'Base de Datos',
            'bd': 'Base de Datos',
            'BASEDATOS': 'Base de Datos',
            'basedatos': 'Base de Datos',
            'base de datos': 'Base de Datos',
            'DB': 'Base de Datos',
            'db': 'Base de Datos',
            'database': 'Base de Datos',
            'DATABASE': 'Base de Datos',
            
            # Programación
            'PROG': 'Programación',
            'prog': 'Programación',
            'programacion': 'Programación',
            'PROGRAMACION': 'Programación',
            'programación': 'Programación',
            'codigo': 'Programación',
            'CÓDIGO': 'Programación',
            'COD': 'Programación',
            
            # Matemáticas
            'CALC': 'Cálculo',
            'calc': 'Cálculo',
            'calculo': 'Cálculo',
            'CÁLCULO': 'Cálculo',
            'MAT': 'Matemáticas',
            'mat': 'Matemáticas',
            'matematicas': 'Matemáticas',
            'MATEMATICAS': 'Matemáticas',
            'matemáticas': 'Matemáticas',
            'LIN': 'Álgebra Lineal',
            'lineal': 'Álgebra Lineal',
            'algebra': 'Álgebra Lineal',
            'ÁLGEBRA': 'Álgebra Lineal',
            'DISCR': 'Matemática Discreta',
            'discreta': 'Matemática Discreta',
            'discretas': 'Matemática Discreta',
            'MDIS': 'Matemática Discreta',
            
            # Ciencias
            'FIS': 'Física',
            'fis': 'Física',
            'fisica': 'Física',
            'FISICA': 'Física',
            'física': 'Física',
            'QUIM': 'Química',
            'quim': 'Química',
            'quimica': 'Química',
            'QUIMICA': 'Química',
            'química': 'Química',
            
            # Tecnologías de la Información
            'REDES': 'Redes de Computadoras',
            'redes': 'Redes de Computadoras',
            'redes comp': 'Redes de Computadoras',
            'REDESCOMP': 'Redes de Computadoras',
            'NET': 'Redes de Computadoras',
            'SO': 'Sistemas Operativos',
            'so': 'Sistemas Operativos',
            'sistemas operativos': 'Sistemas Operativos',
            'SISTOP': 'Sistemas Operativos',
            'OS': 'Sistemas Operativos',
            
            # Inteligencia Artificial
            'IA': 'Inteligencia Artificial',
            'ia': 'Inteligencia Artificial',
            'inteligencia artificial': 'Inteligencia Artificial',
            'INTELART': 'Inteligencia Artificial',
            'AI': 'Inteligencia Artificial',
            'ML': 'Machine Learning',
            'ml': 'Machine Learning',
            'machine learning': 'Machine Learning',
            'MACHINELEARN': 'Machine Learning',
            'aprendizaje automatico': 'Machine Learning',
            
            # Desarrollo
            'WEB': 'Desarrollo Web',
            'web': 'Desarrollo Web',
            'desarrollo web': 'Desarrollo Web',
            'DESWEB': 'Desarrollo Web',
            'frontend': 'Desarrollo Web',
            'backend': 'Desarrollo Web',
            'MOVIL': 'Desarrollo Móvil',
            'movil': 'Desarrollo Móvil',
            'móvil': 'Desarrollo Móvil',
            'DESMOVIL': 'Desarrollo Móvil',
            'android': 'Desarrollo Móvil',
            'ios': 'Desarrollo Móvil',
            'apps': 'Desarrollo Móvil',
            
            # Seguridad
            'SEG': 'Seguridad Informática',
            'seg': 'Seguridad Informática',
            'seguridad': 'Seguridad Informática',
            'SEGINFO': 'Seguridad Informática',
            'cybersecurity': 'Seguridad Informática',
            'ciberseguridad': 'Seguridad Informática',
            'hacking': 'Seguridad Informática',
            
            # Ingeniería de Software
            'INGSOFT': 'Ingeniería de Software',
            'ing soft': 'Ingeniería de Software',
            'ingenieria software': 'Ingeniería de Software',
            'IS': 'Ingeniería de Software',
            'is': 'Ingeniería de Software',
            'software': 'Ingeniería de Software',
            'sw': 'Ingeniería de Software',
            
            # Arquitectura
            'ARQCOMP': 'Arquitectura de Computadoras',
            'arq comp': 'Arquitectura de Computadoras',
            'arquitectura computadoras': 'Arquitectura de Computadoras',
            'ARQ': 'Arquitectura de Computadoras',
            'arq': 'Arquitectura de Computadoras',
            'hardware': 'Arquitectura de Computadoras',
            
            # Ciencia de Datos
            'CIENCDAT': 'Ciencia de Datos',
            'ciencia datos': 'Ciencia de Datos',
            'CD': 'Ciencia de Datos',
            'cd': 'Ciencia de Datos',
            'data science': 'Ciencia de Datos',
            'BIGDATA': 'Big Data',
            'big data': 'Big Data',
            'BDATA': 'Big Data',
            
            # Cloud Computing
            'CLOUD': 'Computación en la Nube',
            'cloud': 'Computación en la Nube',
            'computacion nube': 'Computación en la Nube',
            'NUBE': 'Computación en la Nube',
            'aws': 'Computación en la Nube',
            'azure': 'Computación en la Nube',
            
            # IoT
            'IOT': 'Internet de las Cosas',
            'iot': 'Internet de las Cosas',
            'internet cosas': 'Internet de las Cosas',
            'IDC': 'Internet de las Cosas',
            'sensors': 'Internet de las Cosas',
            
            # Blockchain
            'BLOCK': 'Blockchain',
            'block': 'Blockchain',
            'blockchain': 'Blockchain',
            'CADENA': 'Blockchain',
            'bloque': 'Blockchain',
            
            # UX/UI
            'UX': 'Experiencia de Usuario',
            'ux': 'Experiencia de Usuario',
            'experiencia usuario': 'Experiencia de Usuario',
            'UI': 'Interfaz de Usuario',
            'ui': 'Interfaz de Usuario',
            'interfaz usuario': 'Interfaz de Usuario',
            'diseño': 'Interfaz de Usuario',
            
            # Ciberseguridad avanzada
            'HACK': 'Hacking Ético',
            'hacking etico': 'Hacking Ético',
            'pentest': 'Hacking Ético',
            'CRIPTO': 'Criptografía',
            'cripto': 'Criptografía',
            'criptografia': 'Criptografía',
            'CRIP': 'Criptografía',
            
            # Desarrollo de Juegos
            'GAMES': 'Desarrollo de Juegos',
            'games': 'Desarrollo de Juegos',
            'videojuegos': 'Desarrollo de Juegos',
            'GAMEDEV': 'Desarrollo de Juegos',
            'unity': 'Desarrollo de Juegos',
            'unreal': 'Desarrollo de Juegos',
            
            # DevOps
            'DEVOPS': 'DevOps',
            'devops': 'DevOps',
            'dev ops': 'DevOps',
            'CI/CD': 'DevOps',
            'infraestructura': 'DevOps',
            
            # Ciencias Sociales
            'ECO': 'Economía',
            'economia': 'Economía',
            'ECONOMIA': 'Economía',
            'ADM': 'Administración',
            'administracion': 'Administración',
            'ADMIN': 'Administración',
            'management': 'Administración',
            'MARK': 'Marketing',
            'mark': 'Marketing',
            'mkt': 'Marketing',
            'digital marketing': 'Marketing',
            
            # Idiomas
            'INGL': 'Inglés',
            'ingles': 'Inglés',
            'INGLES': 'Inglés',
            'english': 'Inglés',
            'LANG': 'Idiomas',
            'idiomas': 'Idiomas',
            'languages': 'Idiomas',
            'FRANC': 'Francés',
            'frances': 'Francés',
            'ALEM': 'Alemán',
            'aleman': 'Alemán',
            
            # Ética y Derecho
            'ETICA': 'Ética',
            'etica': 'Ética',
            'ética': 'Ética',
            'DER': 'Derecho',
            'derecho': 'Derecho',
            'law': 'Derecho',
            'LEGAL': 'Derecho Informático',
            'derecho informatico': 'Derecho Informático',
            
            # Gestión de Proyectos
            'PM': 'Gestión de Proyectos',
            'pm': 'Gestión de Proyectos',
            'gestion proyectos': 'Gestión de Proyectos',
            'proyectos': 'Gestión de Proyectos',
            'AGILE': 'Metodologías Ágiles',
            'agile': 'Metodologías Ágiles',
            'scrum': 'Metodologías Ágiles',
            'kanban': 'Metodologías Ágiles'
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
    
    def get_file_category(self, mime_type, extension):
        """Determina la categoría del archivo basado en su tipo MIME y extensión"""
        # Primero intentamos con el tipo MIME
        categories = {
            # Documentos
            'application/pdf': 'Documentos',
            'application/msword': 'Documentos',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Documentos',
            'application/vnd.oasis.opendocument.text': 'Documentos',
            'text/plain': 'Documentos',
            'application/rtf': 'Documentos',
            'application/x-tex': 'Documentos',
            'application/vnd.apple.pages': 'Documentos',
            'application/vnd.google-apps.document': 'Documentos',
            'text/markdown': 'Documentos',
            
            # Hojas de Cálculo
            'application/vnd.ms-excel': 'Hojas de Calculo',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Hojas de Calculo',
            'application/vnd.oasis.opendocument.spreadsheet': 'Hojas de Calculo',
            'text/csv': 'Hojas de Calculo',
            'application/vnd.google-apps.spreadsheet': 'Hojas de Calculo',
            'application/vnd.ms-excel.sheet.macroEnabled.12': 'Hojas de Calculo',
            
            # Presentaciones
            'application/vnd.ms-powerpoint': 'Presentaciones',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'Presentaciones',
            'application/vnd.oasis.opendocument.presentation': 'Presentaciones',
            'application/vnd.google-apps.presentation': 'Presentaciones',
            
            # Imágenes
            'image/jpeg': 'Imagenes',
            'image/png': 'Imagenes',
            'image/gif': 'Imagenes',
            'image/bmp': 'Imagenes',
            'image/svg+xml': 'Imagenes',
            'image/tiff': 'Imagenes',
            'image/webp': 'Imagenes',
            'image/vnd.adobe.photoshop': 'Imagenes',
            'image/x-eps': 'Imagenes',
            
            # Videos
            'video/mp4': 'Videos',
            'video/quicktime': 'Videos',
            'video/x-msvideo': 'Videos',
            'video/x-matroska': 'Videos',
            'video/webm': 'Videos',
            'video/x-flv': 'Videos',
            'video/3gpp': 'Videos',
            
            # Audio
            'audio/mpeg': 'Audio',
            'audio/wav': 'Audio',
            'audio/flac': 'Audio',
            'audio/ogg': 'Audio',
            'audio/aac': 'Audio',
            'audio/x-m4a': 'Audio',
            'audio/x-ms-wma': 'Audio',
            
            # Archivos Comprimidos
            'application/zip': 'Archivos Comprimidos',
            'application/x-rar-compressed': 'Archivos Comprimidos',
            'application/x-7z-compressed': 'Archivos Comprimidos',
            'application/x-tar': 'Archivos Comprimidos',
            'application/gzip': 'Archivos Comprimidos',
            'application/x-bzip2': 'Archivos Comprimidos',
            
            # Código
            'text/x-python': 'Codigo',
            'application/javascript': 'Codigo',
            'text/html': 'Codigo',
            'text/css': 'Codigo',
            'application/json': 'Codigo',
            'text/x-java': 'Codigo',
            'text/x-c': 'Codigo',
            'text/x-c++': 'Codigo',
            'text/x-shellscript': 'Codigo',
            'application/xml': 'Codigo',
            'application/x-httpd-php': 'Codigo',
            
            # Ebooks
            'application/epub+zip': 'Ebooks',
            'application/x-mobipocket-ebook': 'Ebooks',
            'application/vnd.amazon.ebook': 'Ebooks',
            
            # Fuentes
            'font/ttf': 'Fuentes',
            'font/otf': 'Fuentes',
            'application/font-woff': 'Fuentes',
            'application/font-woff2': 'Fuentes',
            'application/vnd.ms-fontobject': 'Fuentes',
            
            # Binarios/Instaladores
            'application/x-msdownload': 'Binarios',
            'application/x-sh': 'Binarios',
            'application/x-executable': 'Binarios',
            'application/vnd.android.package-archive': 'Binarios',
            'application/x-msi': 'Binarios',
            
            # CAD y Modelado 3D
            'application/sldworks': 'CAD',
            'application/vnd.dwg': 'CAD',
            'model/stl': 'CAD',
            'model/obj': 'CAD',
            
            # Bases de Datos
            'application/x-sqlite3': 'Bases de Datos',
            'application/vnd.ms-access': 'Bases de Datos',
            'application/x-dbf': 'Bases de Datos',
            'application/sql': 'Bases de Datos',
            'application/x-sql': 'Bases de Datos',
            'application/backup': 'Bases de Datos',
            'application/x-backup': 'Bases de Datos',
            'application/octet-stream': 'Bases de Datos',
            
            # Virtualización
            'application/x-virtualbox-vdi': 'Virtualizacion',
            'application/x-vmdk-disk': 'Virtualizacion',
            
            # Por defecto
            'application/octet-stream': 'Otros'
        }
        
        # Si no, intentamos con la extensión
        extension_categories = {
            '.sql': 'Bases de Datos',
            '.bak': 'Bases de Datos',
            '.docx': 'Documentos',
            '.doc': 'Documentos',
            '.xlsx': 'Hojas de Calculo',
            '.xls': 'Hojas de Calculo',
            '.pptx': 'Presentaciones',
            '.ppt': 'Presentaciones',
            '.pdf': 'Documentos',
            '.txt': 'Documentos',
            '.rtf': 'Documentos',
            '.odt': 'Documentos',
            '.csv': 'Hojas de Calculo',
            '.jpg': 'Imagenes',
            '.jpeg': 'Imagenes',
            '.png': 'Imagenes',
            '.gif': 'Imagenes',
            '.bmp': 'Imagenes',
            '.svg': 'Imagenes',
            '.mp4': 'Videos',
            '.mov': 'Videos',
            '.avi': 'Videos',
            '.mkv': 'Videos',
            '.mp3': 'Audio',
            '.wav': 'Audio',
            '.flac': 'Audio',
            '.zip': 'Archivos Comprimidos',
            '.rar': 'Archivos Comprimidos',
            '.7z': 'Archivos Comprimidos',
            '.tar': 'Archivos Comprimidos',
            '.gz': 'Archivos Comprimidos',
            '.py': 'Codigo',
            '.js': 'Codigo',
            '.html': 'Codigo',
            '.css': 'Codigo',
            '.json': 'Codigo',
            '.java': 'Codigo',
            '.c': 'Codigo',
            '.cpp': 'Codigo',
            '.php': 'Codigo',
            '.epub': 'Ebooks',
            '.mobi': 'Ebooks',
            '.azw': 'Ebooks',
            '.ttf': 'Fuentes',
            '.otf': 'Fuentes',
            '.woff': 'Fuentes',
            '.woff2': 'Fuentes',
            '.exe': 'Binarios',
            '.sh': 'Binarios',
            '.apk': 'Binarios',
            '.msi': 'Binarios',
            '.dwg': 'CAD',
            '.stl': 'CAD',
            '.obj': 'CAD',
            '.accdb': 'Bases de Datos',
            '.mdb': 'Bases de Datos',
            '.psd': 'Imagenes',
            '.ai': 'Imagenes',
            '.indd': 'Documentos',
            '.dbf': 'Bases de Datos',
            '.log': 'Documentos',
            '.xml': 'Codigo',
            '.sqlite': 'Bases de Datos',
            '.db': 'Bases de Datos',
            '.vdi': 'Virtualizacion',
            '.vmdk': 'Virtualizacion',
            '.db3': 'Bases de Datos',
            '.sdf': 'Bases de Datos',
            '.mdf': 'Bases de Datos',
            '.ndf': 'Bases de Datos',
            '.frm': 'Bases de Datos',
            '.ibd': 'Bases de Datos',
            '.myd': 'Bases de Datos',
            '.myi': 'Bases de Datos',
            '.dmp': 'Bases de Datos',
            '.sql.gz': 'Bases de Datos',
            '.backup': 'Bases de Datos',
            '.db_backup': 'Bases de Datos',
            '.dart': 'Codigo',
            '.swift': 'Codigo',
            '.kt': 'Codigo',
            '.go': 'Codigo',
            '.rb': 'Codigo',
            '.pl': 'Codigo',
            '.lua': 'Codigo',
            '.r': 'Codigo',
            '.ts': 'Codigo',
            '.tsx': 'Codigo',
            '.sass': 'Codigo',
            '.scss': 'Codigo',
            '.less': 'Codigo',
            '.vue': 'Codigo',
            '.cs': 'Codigo',
            '.fs': 'Codigo',
            '.vb': 'Codigo',
            '.asm': 'Codigo',
            '.s': 'Codigo',
            '.rs': 'Codigo',
            '.shader': 'Codigo',
            '.jl': 'Codigo',
            '.ipynb': 'Codigo',
            '.scala': 'Codigo',
            '.hs': 'Codigo',
            '.clj': 'Codigo',
            '.coffee': 'Codigo',
            '.d': 'Codigo',
            '.erl': 'Codigo',
            '.ex': 'Codigo',
            '.exs': 'Codigo',
            '.fsx': 'Codigo',
            '.groovy': 'Codigo',
            '.ino': 'Codigo',
            '.jade': 'Codigo',
            '.pde': 'Codigo',
            '.ps1': 'Codigo',
            '.psm1': 'Codigo',
            '.psd1': 'Codigo',
            '.pyc': 'Codigo',
            '.pyo': 'Codigo',
            '.rpm': 'Binarios',
            '.deb': 'Binarios',
            '.dmg': 'Binarios',
            '.pkg': 'Binarios',
            '.app': 'Binarios',
            '.bat': 'Binarios',
            '.cmd': 'Binarios',
            '.com': 'Binarios',
            '.jar': 'Binarios',
            '.war': 'Binarios',
            '.ear': 'Binarios',
            '.dll': 'Binarios',
            '.so': 'Binarios',
            '.lib': 'Binarios',
            '.a': 'Binarios',
            '.ko': 'Binarios',
            '.o': 'Binarios',
            '.obj': 'Binarios',
            '.msix': 'Binarios',
            '.appx': 'Binarios',
            '.appxbundle': 'Binarios',
            '.msixbundle': 'Binarios',
            '.iso': 'Binarios',
            '.img': 'Binarios',
            '.bin': 'Binarios',
            '.cue': 'Binarios',
            '.dmg': 'Binarios',
            '.toast': 'Binarios',
            '.vcd': 'Binarios',
            '.crdownload': 'Descargas',
            '.part': 'Descargas',
            '.tmp': 'Temporales',
            '.temp': 'Temporales',
            '.download': 'Descargas',
            '.cbr': 'Comics',
            '.cbz': 'Comics',
            '.epub': 'Ebooks',
            '.mobi': 'Ebooks',
            '.azw': 'Ebooks',
            '.azw3': 'Ebooks',
            '.fb2': 'Ebooks',
            '.ibooks': 'Ebooks',
            '.lit': 'Ebooks',
            '.prc': 'Ebooks',
            '.pdb': 'Ebooks',
            '.oxps': 'Documentos',
            '.xps': 'Documentos',
            '.key': 'Presentaciones',
            '.odp': 'Presentaciones',
            '.sxi': 'Presentaciones',
            '.sti': 'Presentaciones',
            '.sxd': 'Presentaciones',
            '.sdd': 'Presentaciones',
            '.sda': 'Presentaciones',
            '.show': 'Presentaciones',
            '.show': 'Presentaciones',
            '.thmx': 'Presentaciones',
            '.pot': 'Presentaciones',
            '.pps': 'Presentaciones',
            '.ppa': 'Presentaciones',
            '.ppam': 'Presentaciones',
            '.sldm': 'Presentaciones',
            '.ppsm': 'Presentaciones',
            '.pptm': 'Presentaciones',
            '.potm': 'Presentaciones',
            '.potx': 'Presentaciones',
            '.pptx': 'Presentaciones',
            '.xlsm': 'Hojas de Calculo',
            '.xltm': 'Hojas de Calculo',
            '.xltx': 'Hojas de Calculo',
            '.xlam': 'Hojas de Calculo',
            '.xla': 'Hojas de Calculo',
            '.ods': 'Hojas de Calculo',
            '.fods': 'Hojas de Calculo',
            '.ots': 'Hojas de Calculo',
            '.sxc': 'Hojas de Calculo',
            '.stc': 'Hojas de Calculo',
            '.dif': 'Hojas de Calculo',
            '.dbf': 'Hojas de Calculo',
            '.wk1': 'Hojas de Calculo',
            '.wks': 'Hojas de Calculo',
            '.123': 'Hojas de Calculo',
            '.wb2': 'Hojas de Calculo',
            '.qpw': 'Hojas de Calculo',
            '.wq1': 'Hojas de Calculo',
            '.xlr': 'Hojas de Calculo',
            '.xlsb': 'Hojas de Calculo',
            '.numbers': 'Hojas de Calculo',
            '.gnumeric': 'Hojas de Calculo',
            '.abw': 'Documentos',
            '.zabw': 'Documentos',
            '.lwp': 'Documentos',
            '.wpd': 'Documentos',
            '.wps': 'Documentos',
            '.602': 'Documentos',
            '.pdb': 'Documentos',
            '.pwi': 'Documentos',
            '.sdw': 'Documentos',
            '.vor': 'Documentos',
            '.sxw': 'Documentos',
            '.stw': 'Documentos',
            '.dot': 'Documentos',
            '.dotx': 'Documentos',
            '.dotm': 'Documentos',
            '.docm': 'Documentos',
            '.mobi': 'Ebooks',
            '.azw': 'Ebooks',
            '.azw3': 'Ebooks',
            '.fb2': 'Ebooks',
            '.ibooks': 'Ebooks',
            '.lit': 'Ebooks',
            '.prc': 'Ebooks',
            '.pdb': 'Ebooks',
            '.oxps': 'Documentos',
            '.xps': 'Documentos',
            '.key': 'Presentaciones',
            '.odp': 'Presentaciones',
            '.sxi': 'Presentaciones',
            '.sti': 'Presentaciones',
            '.sxd': 'Presentaciones',
            '.sdd': 'Presentaciones',
            '.sda': 'Presentaciones',
            '.show': 'Presentaciones',
            '.thmx': 'Presentaciones',
            '.pot': 'Presentaciones',
            '.pps': 'Presentaciones',
            '.ppa': 'Presentaciones',
            '.ppam': 'Presentaciones',
            '.sldm': 'Presentaciones',
            '.ppsm': 'Presentaciones',
            '.pptm': 'Presentaciones',
            '.potm': 'Presentaciones',
            '.potx': 'Presentaciones',
            '.pptx': 'Presentaciones',
            '.xlsm': 'Hojas de Calculo',
            '.xltm': 'Hojas de Calculo',
            '.xltx': 'Hojas de Calculo',
            '.xlam': 'Hojas de Calculo',
            '.xla': 'Hojas de Calculo',
            '.ods': 'Hojas de Calculo',
            '.fods': 'Hojas de Calculo',
            '.ots': 'Hojas de Calculo',
            '.sxc': 'Hojas de Calculo',
            '.stc': 'Hojas de Calculo',
            '.dif': 'Hojas de Calculo',
            '.dbf': 'Hojas de Calculo',
            '.wk1': 'Hojas de Calculo',
            '.wks': 'Hojas de Calculo',
            '.123': 'Hojas de Calculo',
            '.wb2': 'Hojas de Calculo',
            '.qpw': 'Hojas de Calculo',
            '.wq1': 'Hojas de Calculo',
            '.xlr': 'Hojas de Calculo',
            '.xlsb': 'Hojas de Calculo',
            '.numbers': 'Hojas de Calculo',
            '.gnumeric': 'Hojas de Calculo',
            '.abw': 'Documentos',
            '.zabw': 'Documentos',
            '.lwp': 'Documentos',
            '.wpd': 'Documentos',
            '.wps': 'Documentos',
            '.602': 'Documentos',
            '.pdb': 'Documentos',
            '.pwi': 'Documentos',
            '.sdw': 'Documentos',
            '.vor': 'Documentos',
            '.sxw': 'Documentos',
            '.stw': 'Documentos',
            '.dot': 'Documentos',
            '.dotx': 'Documentos',
            '.dotm': 'Documentos',
            '.docm': 'Documentos'
        }
        
        # Primero intentamos con el tipo MIME
        if mime_type in categories:
            return categories[mime_type]
        
        # Si no, intentamos con la extensión
        ext = extension.lower()
        if ext in extension_categories:
            return extension_categories[ext]
        
        return 'Otros'
    
    def organize_files(self):
        """Proceso principal de organización con estructura jerárquica"""
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
            
            # Obtener extensión del archivo
            extension = src.suffix
            
            # Determinar curso universitario
            course_name = "Otros Cursos"
            if self.organize_by_course.get():
                course_name = self.detect_course_from_filename(src.stem)
            
            # Determinar categoría de archivo (usando tanto MIME como extensión)
            file_category = "Otros"
            if self.organize_by_type.get():
                file_category = self.get_file_category(mime_type, extension)
            
            # Crear estructura de carpetas jerárquica
            dest_folder = organized_folder
            
            # 1. Carpeta de curso (si está habilitada)
            if self.organize_by_course.get():
                dest_folder = dest_folder / course_name
            
            # 2. Carpeta de categoría (si está habilitada)
            if self.organize_by_type.get():
                dest_folder = dest_folder / file_category
            
            # Crear carpeta destino si no existe
            if not dest_folder.exists():
                dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Nombre destino
            dest = dest_folder / src.name
            
            # Verificar duplicados
            if dest.exists():
                # Generar nombre único con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{src.stem}_{timestamp}{src.suffix}"
                dest = dest_folder / new_name
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
                f"Archivos duplicados: {duplicates}"
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