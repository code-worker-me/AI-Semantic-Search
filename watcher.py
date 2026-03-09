import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database import process_single_pdf, remove_single_pdf

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            time.sleep(1)
            
            filename = os.path.basename(event.src_path)
            
            try:
                process_single_pdf(event.src_path, filename)
            except Exception as e:
                print(f"Terjadi kesalahan saat memproses {filename}: {str(e)}")
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            filename = os.path.basename(event.src_path)
            try:
                remove_single_pdf(filename)
            except Exception as e:
                print(f"Terjadi kesalahan saat menghapus {filename}: {str(e)}")
                
def start_watching(folder_path="arsip"):
    """Fungsi untuk menjalankan Watchdog Observer"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    return observer