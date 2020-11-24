# aiopyql-rpc-endpoint
Template for deploying an EasyRpcServer in front of an aiopyql conncted database

## Key Features
- Quickly depoy and share an aiopyql database connection 
- Shared Database Cache

# Quick Start - Sqlite

    $ docker run -d --name aiopyql-testdb \
        -p 8590:8190 \
        -e DB_TYPE='sqlite' \
        -e DB_NAME='testdb' \
        -e RPC_SECRET='abcd1234' \
        -v dbtest:/mnt/pyql-db-endpoint \
        joshjamison/aiopyql-rpc-endpoint:latest

# Quick Start - MySql

    $ docker run -d --name aiopyql-testdb \
        -p 8590:8190 \
        -e DB_TYPE='mysql' \
        -e DB_NAME='testdb' \
        -e DB_USER='mysql_user' \
        -e DB_HOST='127.0.0.1' \ 
        -e DB_PORT=3304 \
        -e DB_PASSWORD='abcd1234' \
        -e RPC_SECRET='abcd1234' \
        joshjamison/aiopyql-rpc-endpoint:latest

# Quick Start - Postgres

    # Deploy a test Postgres Container

    $ mkdir pg_data

    $ docker run --name pgtest  -e POSTGRES_PASSWORD=abcd1234 -e POSTGRES_DB=postgres_db -p 5432:5432 -v $(pwd)/pg_data:/var/lib/postgresql/data -d postgres:latest


    $ docker run -d --name aiopyql-pg-testdb \
        -p 8590:8190 \
        -e DB_TYPE='postgres' \
        -e DB_NAME='postgres_db' \
        -e DB_USER='postgres' \
        -e DB_HOST='localhost' \
        -e DB_PORT=5432 \
        -e DB_PASSWORD='abcd1234' \
        -e RPC_SECRET='abcd1234' \
        joshjamison/aiopyql-rpc-endpoint:latest

# Shared Functions
Connected proxies will have access the the following methdods:

### Database Methods
- create_table: aiopyql method for creating new tables
- show_tables: list existing table names
- run: run a database query, results are unformatted

<br>

### Table methods: <br>

For each table, the following methods exists within the EasyProxy 

    proxy['namespace'][f'{table}_{method}']

- insert 
- update 
- delete
- select

Usage for each function can be found in [aiopyql](https://github.com/codemation/aiopyql)




# Example: Accessing the Endpoint

    # client.py

    from easyrpc.proxy import EasyRpcProxy
    from fastapi import FastAPI

    server = FastAPI()

    @server.on_event('startup')
    async def setup():
        server.data = {}

        server.data['testdb'] = await EasyRpcProxy.create(
            '192.168.122.100', 
            30111, 
            '/sqlite/database', 
            server_secret='abcd1234',
            namespace='testdb'
        )
<br>

    # create_table

    create_table_result = await server.data['testdb']['create_table'](
        'keystore',
        [
            ['key', 'str', 'UNIQUE NOT NULL'],
            ['value', 'str']
        ],
        prim_key='key',
        cache_enabled=True
    )
    print(f"create_table_result: {create_table_result}")
<br>

    # show_tables

    show_tables = await server.data['testdb']['show_tables']()
    print(f"show tables: {show_tables}")
<br>

    # run

    query = 'select * from sqlite_master'

    run_query = await server.data['testdb']['run'](query)
    print(f"run_query results: {run_query}")
<br>

    # insert
    await server.data['testdb']['keystore_insert']('new_key': 'new_value')
<br>

    # update
    await server.data['testdb']['keystore_update'](
        'value': 'updated_value', 
        where={'key': 'new_key'}
    )
<br>

    # delete
    await server.data['testdb']['keystore_update']( 
        where={'key': 'new_key'}
    )
<br>

    # select
    selection = await server.data['testdb']['keystore_update']( 
        '*',
        where={'key': 'new_key'}
    )
    print(f"selection: {selection}")
<br>

    # get_schema
    schema = await server.data['testdb]['keystore_get_schema']()
    print(f"schema: {schema}")



