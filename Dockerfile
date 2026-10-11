FROM python:3.12-slim

# Entorno: Prevenir buffering, bytecode innecesario y prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MALLOC_ARENA_MAX=2 \
    LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2

# Dependencias del sistema (WeasyPrint + jemalloc para reducir consumo de RAM)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libopenjp2-7 \
    shared-mime-info \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-freefont-ttf \
    gir1.2-pango-1.0 \
    gir1.2-gdkpixbuf-2.0 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libjemalloc2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copia e instalación de dependencias sin cache local de pip
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia del código fuente
COPY . .

# Compilación de estáticos comprimidos para el CDN
RUN python manage.py collectstatic --noinput

# Ejecución optimizada de Daphne con timeouts de desconexión y latidos afinados
CMD ["sh", "-c", "exec daphne -b 0.0.0.0 -p $PORT --ping-interval 30 --ping-timeout 15 --application-close-timeout 10 djangocrud.asgi:application"]