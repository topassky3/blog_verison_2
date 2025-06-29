# Usamos una imagen oficial de Python (ajusta la versión si lo requieres)
FROM python:3.9-slim

# Evitar que se generen archivos .pyc y salida sin búfer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ===== AÑADIR ESTO =====
# Creamos un grupo y un usuario sin privilegios llamado 'app'
RUN groupadd -r app && useradd --no-log-init -r -g app app
# ========================

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar Supervisor y dependencias del sistema necesarias
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . /app/

# ===== AÑADIR ESTO =====
# Le damos la propiedad de los archivos de la app al nuevo usuario
RUN chown -R app:app /app
# ========================

# Ejecutar collectstatic para recopilar los archivos estáticos
RUN python manage.py collectstatic --noinput

# Copiar la configuración de Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer el puerto
EXPOSE 7090

# Comando para iniciar Supervisor
CMD ["/usr/bin/supervisord", "-n"]
