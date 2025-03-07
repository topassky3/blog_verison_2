# Usamos una imagen oficial de Python (ajusta la versión si lo requieres)
FROM python:3.9-slim

# Evitar que se generen archivos .pyc y salida sin búfer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . /app/

# Ejecutar collectstatic para recopilar los archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer el puerto que usará Gunicorn (en este caso el 7090)
EXPOSE 7090

# Comando para ejecutar el servidor con Gunicorn usando el WSGI de blog_version2_blackend
CMD ["gunicorn", "blog_version2_blackend.wsgi:application", "--bind", "0.0.0.0:7090", "--workers", "3"]
