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
        self.mongo_uri = getattr(settings, 'MONGO_URI', 'mongodb://51.222.159.144:27017')
        self.database_name = getattr(settings, 'MONGO_DATABASE', 'admin')
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

    def _save(self, name, content):
        # Asegurarse de que se lea el contenido desde el inicio
        content.seek(0)
        file_data = content.read()
        new_md5 = self._compute_md5(file_data)
        print("Guardando archivo:", name, "tamaño:", len(file_data), "nuevo MD5:", new_md5)

        # Buscar un archivo existente con el mismo nombre
        existing = self.fs.find_one({'filename': name})
        if existing:
            # El campo 'md5' de GridFS ya contiene el hash calculado
            if existing.md5 == new_md5:
                print("El archivo ya existe con el mismo contenido. No se guarda de nuevo.")
                return name
            else:
                print("El archivo ya existe pero con contenido diferente. Se reemplaza.")
                self.fs.delete(existing._id)

        self.fs.put(file_data, filename=name)
        return name

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
