import tkinter as tk
from tkinter import ttk
import os
import datetime
import threading
import time

class TextMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text.txt Monitor")
        self.root.geometry("600x400")
        
        # Пути
        self.bind_mount_file = "/app/data/bind_mount/text.txt"
        self.volume_file = "/app/data/volume/text.txt"
        
        # Создаем папки если их нет
        os.makedirs(os.path.dirname(self.bind_mount_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.volume_file), exist_ok=True)
        
        # Создаем тестовые файлы если их нет
        self.create_initial_files()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Запускаем автообновление
        self.start_auto_refresh()
        
    def create_initial_files(self):
        """Создает начальные файлы если их нет"""
        if not os.path.exists(self.bind_mount_file):
            with open(self.bind_mount_file, 'w') as f:
                f.write("=== Bind Mount File ===\n")
                f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("This file is stored in Bind Mount\n")
                f.write("You can edit it from your host system!\n")
        
        if not os.path.exists(self.volume_file):
            with open(self.volume_file, 'w') as f:
                f.write("=== Volume File ===\n")
                f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("This file is stored in Docker Volume\n")
                f.write("It persists between container restarts\n")
    
    def create_widgets(self):
        """Создает простой интерфейс"""
        # Заголовок
        title = ttk.Label(self.root, text="📄 Text.txt Monitor", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Информация
        info = ttk.Label(self.root, 
                        text="Edit text.txt files outside Docker and see changes here",
                        font=("Arial", 10))
        info.pack(pady=5)
        
        # Вкладки для двух файлов
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка Bind Mount
        bind_frame = ttk.Frame(notebook)
        notebook.add(bind_frame, text="📁 Bind Mount")
        self.create_file_tab(bind_frame, self.bind_mount_file, "bind")
        
        # Вкладка Volume
        volume_frame = ttk.Frame(notebook)
        notebook.add(volume_frame, text="💾 Volume")
        self.create_file_tab(volume_frame, self.volume_file, "volume")
        
        # Кнопки управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)
        
        ttk.Button(control_frame, text="🔄 Refresh All", 
                  command=self.refresh_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📝 Add Sample Text", 
                  command=self.add_sample_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="❌ Exit", 
                  command=self.root.destroy).pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_label = ttk.Label(self.root, 
                                     text="Auto-refresh every 5 seconds",
                                     relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Загружаем данные
        self.refresh_all()
    
    def create_file_tab(self, parent, filepath, file_type):
        """Создает вкладку для файла"""
        # Информация о файле
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.path_label = ttk.Label(info_frame, 
                                   text=f"Path: {filepath}",
                                   font=("Courier", 9))
        self.path_label.pack(anchor=tk.W)
        
        # Содержимое файла
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Текстовое поле с прокруткой
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Сохраняем ссылки на виджеты
        if file_type == "bind":
            self.bind_text = text_widget
            self.bind_path_label = self.path_label
        else:
            self.volume_text = text_widget
            self.volume_path_label = self.path_label
    
    def read_file(self, filepath):
        """Читает содержимое файла"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            return "File not found!"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def update_file_display(self, filepath, text_widget, path_label):
        """Обновляет отображение файла"""
        content = self.read_file(filepath)
        
        # Сохраняем позицию прокрутки
        scroll_position = text_widget.yview()
        
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, content)
        
        # Восстанавливаем позицию прокрутки
        text_widget.yview_moveto(scroll_position[0])
        
        # Обновляем информацию о файле
        if os.path.exists(filepath):
            stats = os.stat(filepath)
            size = stats.st_size
            modified = datetime.datetime.fromtimestamp(stats.st_mtime)
            path_label.config(
                text=f"Path: {filepath} | "
                     f"Size: {size} bytes | "
                     f"Modified: {modified.strftime('%H:%M:%S')}"
            )
    
    def refresh_all(self):
        """Обновляет все файлы"""
        self.update_file_display(self.bind_mount_file, self.bind_text, self.bind_path_label)
        self.update_file_display(self.volume_file, self.volume_text, self.volume_path_label)
        self.status_label.config(text=f"Refreshed at: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def add_sample_text(self):
        """Добавляет пример текста в оба файла"""
        sample_text = f"\n\n--- Added at {datetime.datetime.now().strftime('%H:%M:%S')} ---\n"
        sample_text += "This text was added from the application.\n"
        sample_text += "You can also edit files directly on your host system!\n"
        
        # Добавляем в Bind Mount файл
        try:
            with open(self.bind_mount_file, 'a') as f:
                f.write(sample_text)
        except Exception as e:
            print(f"Error writing to bind mount file: {e}")
        
        # Добавляем в Volume файл
        try:
            with open(self.volume_file, 'a') as f:
                f.write(sample_text)
        except Exception as e:
            print(f"Error writing to volume file: {e}")
        
        self.refresh_all()
    
    def start_auto_refresh(self):
        """Запускает автоматическое обновление"""
        def auto_refresh_thread():
            while True:
                time.sleep(5)  # Обновляем каждые 5 секунд
                self.root.after(0, self.refresh_all)
        
        thread = threading.Thread(target=auto_refresh_thread, daemon=True)
        thread.start()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TextMonitorApp(root)
    root.mainloop()