FROM usgsastro/isis

COPY . /app

RUN useradd -m -s /bin/bash appUser && \
    chown -R appUser:appUser /app

WORKDIR /app
RUN conda env update -n base -f environment.yml && \
    printf '#!/bin/bash\nconda activate base\n' > /etc/profile.d/isis.sh

USER appUser
ENTRYPOINT ["/bin/bash", "-lc"]
CMD ["gunicorn -c gunicorn.conf.py isis_server:app"]
