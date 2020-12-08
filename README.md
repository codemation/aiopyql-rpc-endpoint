# aiopyql-rpc-endpoint
Template for deploying an EasyRpcServer in front of an aiopyql conncted database

## Key Features
- Quickly depoy and share an aiopyql database connection 
- Shared Database Cache

## Env
| ENV Variable | Values | Required? |
|--------------|--------|-----------|
| DB_TYPE | 'sqlite', 'mysql', 'postgres' | yes |
| DB_NAME | 'database-name' | yes |
| RPC_SECRET | 'abcd1234' | yes |
| DB_USER | "database-user' | yes - mysql / postgres |
| DB_PASSWORD | 'abcd1234' | yes - mysql / postgres |
| DB_HOST | 'localhost', '0.0.0.0', '192.168.1.1' | yes - mysql / postgres |
| DB_PORT | defaults: 3304 - mysql, 5432 - postgres | yes - yes - mysql / postgres |
| RPC_PATH | '/special-db-path' '/generic' '/ws/nested' | no - defaults to '/ws/DB_NAME' |
| RPC_DEBUG | 'True', 'False' | no - 'False' if unspecified |

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

    $ docker run --name pgtest -d \ 
        -e POSTGRES_PASSWORD=abcd1234 \
        -e POSTGRES_DB=postgres_db \
        -p 5432:5432 \
        -v $(pwd)/pg_data:/var/lib/postgresql/data \
        postgres:latest


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
Connected proxies will have access to aiopyql Database & Table methods

### Database Methods
- create_table: aiopyql method for creating new tables
- show_tables: list existing table names
- run: run a database query, results are unformatted

<br>

### Table methods: <br>

For each table, the following methods exists within the EasyProxy 

    proxy['namespace'][f'{table}_{method}']

Methods
- insert 
- update 
- delete
- select
- get_schema

Usage for each function can be found in [aiopyql](https://github.com/codemation/aiopyql)


# Example: Accessing the Endpoint

    import asyncio
    from easyrpc.tools.database import EasyRpcProxyDatabase

    async def main():

        db = await EasyRpcProxyDatabase.create(
            'localhost', 
            8190, 
            '/ws/testdb', 
            server_secret='abcd1234',
            namespace='testdb'
        )
<br>

        create_table_result = await db.create_table(
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

        show_tables = await db.show_tables()

        print(f"show tables: {show_tables}")
<br>

        query = 'select * from sqlite_master'
        run_query = await db.run(query)

        print(f"run_query results: {run_query}")
<br>

        keystore = db.tables['keystore']

<br>

        # insert
        await keystore.insert(
            **{'key': 'new_key', 'value': 'new_value'}
        )
<br>

        # update
        await keystore.update(
            value='updated_value',
            where={'key': 'new_key'}
        )
<br>

        # delete
        await keystore.delete( 
            where={'key': 'new_key'}
        )
<br>

        # select
        selection = await keystore.select( 
            '*',
            where={'key': 'new_key'}
        )
        print(f"selection: {selection}")
<br>

    asyncio.run(main())
