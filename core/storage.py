# --- CÓDIGO COMPLETO PARA: ~/blog_verison_2/core/storage.py ---

import hashlib
from django.utils.deconstruct import deconstructible
from django.core.files.storage import Storage
import gridfs
import pymongo
from django.core.files.base import ContentFile
from django.conf import settings

@deconstructible
class GridFSStorage(Storage):
    """
    Almacenamiento en MongoDB usando GridFS.
    Los archivos se almacenan en dos colecciones:
      - fs.files: Contiene metadatos como el nombre, tamaño, uploadDate y el MD5 calculado.
      - fs.chunks: Contiene los fragmentos (chunks) de cada archivo.
    """

    def __init__(self, **kwargs):
        # Recupera la URI, la base de datos y las credenciales desde settings.
        self.mongo_uri = getattr(settings, 'MONGO_URI')
        self.database_name = getattr(settings, 'MONGO_DATABASE')
        mongo_username = getattr(settings, 'MONGO_USERNAME', None)
        mongo_password = getattr(settings, 'MONGO_PASSWORD', None)

        if mongo_username and mongo_password:
            self.client = pymongo.MongoClient(
                self.mongo_uri,
                username=mongo_username,
                password=mongo_password
            )
        else:
            self.client = pymongo.MongoClient(self.mongo_uri)

        self.db = self.client[self.database_name]
        self.fs = gridfs.GridFS(self.db)

    def _open(self, name, mode='rb'):
        grid_out = self.fs.find_one({'filename': name})
        if not grid_out:
            raise IOError("El archivo no existe: " + name)
        return ContentFile(grid_out.read(), name=name)

    def _compute_md5(self, data):
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()

    # ===== INICIO DE LA FUNCIÓN DE DEPURACIÓN =====
    # Esta versión tiene "micrófonos" para decirnos qué está pasando.
    def _save(self, name, content):
        print("--- [DEBUG STORAGE] Entrando a la función _save ---")
        print(f"--- [DEBUG STORAGE] Nombre de archivo recibido: {name}")

        try:
            content.seek(0)
            file_data = content.read()
            print(f"--- [DEBUG STORAGE] Tamaño del archivo leído: {len(file_data)} bytes")
            new_md5 = self._compute_md5(file_data)
            print(f"--- [DEBUG STORAGE] MD5 calculado: {new_md5}")

            existing = self.fs.find_one({'filename': name})
            if existing:
                print(f"--- [DEBUG STORAGE] Archivo existente encontrado. Reemplazando...")
                self.fs.delete(existing._id)

            file_id = self.fs.put(file_data, filename=name)
            print(f"--- [DEBUG STORAGE] ¡Éxito! Archivo guardado con ID: {file_id}")
            print("--- [DEBUG STORAGE] Saliendo de _save ---")
            return name
        except Exception as e:
            print(f"--- [DEBUG STORAGE] !!! ERROR DURANTE EL GUARDADO: {e} !!!")
            # Volvemos a lanzar la excepción para que Django sepa que algo falló
            raise
    # ===== FIN DE LA FUNCIÓN DE DEPURACIÓN =====

    def exists(self, name):
        return self.fs.exists({'filename': name})

    def delete(self, name):
        grid_out = self.fs.find_one({'filename': name})
        if grid_out:
            self.fs.delete(grid_out._id)

    def size(self, name):
        grid_out = self.fs.find_one({'filename': name})
        return grid_out.length if grid_out else 0

    def url(self, name):
        # Devuelve la URL para acceder al archivo mediante nuestra vista.
        return "/media2/" + name
