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

    def _save(self, name, content):
        file_data = content.read()  # Leer el contenido una única vez
        print("Guardando archivo:", name, "tamaño:", len(file_data))
        if self.exists(name):
            existing = self.fs.find_one({'filename': name})
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
