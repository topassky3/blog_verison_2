# Usamos una imagen oficial de Python (ajusta la versión si lo requieres)
FROM python:3.9-slim

# Evitar que se generen archivos .pyc y salida sin búfer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar Supervisor y dependencias del sistema necesarias
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . /app/

# Ejecutar collectstatic para recopilar los archivos estáticos
RUN python manage.py collectstatic --noinput

# Copiar la configuración de Supervisor (asegúrate de que supervisord.conf se encuentre en el contexto de build)
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer el puerto que usará Gunicorn (en este caso el 7090)
EXPOSE 7090

# Comando para iniciar Supervisor en modo no daemon (nodaemon=true)
CMD ["/usr/bin/supervisord", "-n"]
