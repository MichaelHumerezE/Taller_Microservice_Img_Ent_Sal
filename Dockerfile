# Usa una imagen de Python como base
FROM python:3.11

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY main.py /app
COPY api/__init__.py /app/api/__init__.py
COPY api/imgAPI.py /app/api/imgAPI.py
COPY api/key.json /app/api/key.json

# Instala las dependencias
RUN pip install flask firebase-admin

# Define el comando por defecto para ejecutar tu aplicación
CMD ["python", "main.py"]
