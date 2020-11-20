FROM joshjamison/python37:latest

ENV PATH="$V_ENV/bin:$PATH"

RUN git clone https://github.com/codemation/aiopyql-rpc-endpoint.git

RUN pip install -r aiopyql-rpc-endpoint/requirements.txt

WORKDIR /aiopyql-rpc-endpoint

ENV PYQL_VOLUME_PATH="/mnt/pyql-db-endpoint"

EXPOSE 8190

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8190", "db_server:server"]