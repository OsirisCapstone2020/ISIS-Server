FROM usgsastro/isis

# Install gdal globally
RUN echo 'deb http://deb.debian.org/debian bullseye main' > /etc/apt/sources.list.d/gdal.list && \
    apt-get update && \
    apt-get install -y gdal-bin && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN useradd -m -s /bin/bash appUser && \
    chown -R appUser:appUser /app

# Install the app
WORKDIR /app
RUN conda env update -n base -f environment.yml && \
    printf '#!/bin/bash\nconda activate base\n' > /etc/profile.d/isis.sh

USER appUser
ENTRYPOINT ["/bin/bash", "-lc"]
CMD ["gunicorn -c gunicorn.conf.py isis_server:app"]
