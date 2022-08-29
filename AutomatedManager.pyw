import os.path
from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# SOSTITUIRE CON LE DIRECTORY DEI RELATIVI TIPI DI FILE
# SE LE DIRECTORY DEI VARI FAIL NON ESISTONO TI CREA IN AUTOMATICO LE CARTELLE
# DIRECTORY DEI DOWNLOAD
source_dir = 'DOWNLOADS_DIR'
# VARIE DIRECTORY PER TIPO CON CONTROLLO SE ESISTE O MENO (boolean type)
dest_dir_sfx = 'SFX_DIR'
check_dir_sfx = os.path.isdir(dest_dir_sfx)
dest_dir_music = 'MUSIC_DIR'
check_dir_music = os.path.isdir(dest_dir_music)
dest_dir_video = 'VIDEO_DIR'
check_dir_video = os.path.isdir(dest_dir_video)
dest_dir_image = 'IMAGE_DIR'
check_dir_image = os.path.isdir(dest_dir_image)
dest_dir_documents = 'DOCUMENT_DIR'
check_dir_documents = os.path.isdir(dest_dir_documents)


# TIPI DI ESTENSIONI PER TIPO

# immagini
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd",
                    ".raw", ".arw", ".cr2", ".nrw", ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt",
                    ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]

# video
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg", ".mp4", ".mp4v", ".m4v", ".avi", ".wmv",
                    ".mov", ".qt", ".flv", ".swf", ".avchd"]

# audio
audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]

# documenti
document_extensions = [".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]


# AGGIUNGERE SE CARTELLA ESISTE
def dir_exist(check, dir):
    if not check:
        os.makedirs(dir)
    return dir


# RENDERE UNICO IL FILE, SE SI CREA UN ALTRO FILE CON STESSO NOME SI AGGIUNGE (N) ALLA FINE
def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name

# MUOVERE FILE DALLA DIRECTORY DEI DOWNLOAD A QUELLA APPOSITA
def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)

def control_extension(type, check, dest, name, entry):
    if name.endswith(type) or name.endswith(type.upper()):
        move_file(dir_exist(check, dest), entry, name)
        logging.info(f"Moved document file: {name}")


# CLASSE ORCHESTRATRICE
class MoverHandler(FileSystemEventHandler):

    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_document_files(entry, name)

    def check_audio_files(self, entry, name):  # CHECKARE I FILE AUDIO
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 5_000_000 or "SFX" in name:  # CONTROLLO SE L'AUDIO E' MINORE DI 5MB
                    dest = dir_exist(check_dir_sfx, dest_dir_sfx)
                else:
                    dest = dir_exist(check_dir_music, dest_dir_music)
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")

    def check_video_files(self, entry, name):  # CHECKARE FILE VIDEO
        for video_extension in video_extensions:
            control_extension(video_extension, check_dir_video, dest_dir_video, name, entry)

    def check_image_files(self, entry, name):  # CHECKARE FILE IMMAGINE
        for image_extension in image_extensions:
            control_extension(image_extension, check_dir_image, dest_dir_image, name, entry)

    def check_document_files(self, entry, name):  # CHECKARE FILE DOCUMENTO
        for documents_extension in document_extensions:
            control_extension(documents_extension, check_dir_documents, dest_dir_documents, name, entry)


# IF DI DEFAULT PER LIBRERIA WATCHDOG
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
