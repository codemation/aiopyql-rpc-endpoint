import os
import asyncio
from fastapi import FastAPI
from easyrpc.server import EasyRpcServer
from aiopyql.data import Database

server = FastAPI()

@server.on_event('startup')
async def db_setup():
    
    db_config = {}
    # get database type
    db_type = os.environ.get('DB_TYPE')
    if not db_type:
        raise Exception(f"missing required DB_TYPE environment variable")
    
    db_name = os.environ.get('DB_NAME')
    if not db_name:
        raise Exception(f"missing required DB_NAME environment variable")

    db_config['db_type'] = db_type
    db_config['database'] = db_name
    if db_type in {'MYSQL', 'POSTGRES'}:
        db_host = os.environ['DB_HOST']
        if not db_host:
            raise Exception(f"missing required DB_HOST environment variable")
        db_config['host'] = db_host
        for cfg in {'DB_PORT', 'DB_USER', 'DB_PASSWORD'}:
            db_config[cfg] = os.environ.get(cfg)
            if not db_config[cfg]:
                raise Exception(f"missing required {cfg} environment variable")
    else:
        sqlite_db_path = os.environ.get('PYQL_VOLUME_PATH')
        if sqlite_db_path:
            db_config['database'] = f"{sqlite_db_path}/{db_name}"
    db_cache = os.environ.get('DB_CACHE')
    if db_cache:
        db_config['cache_enabled'] = True if not db_cache == 0 else False
    else:
        db_config['cache_enabled'] = True
        
    rpc_config = {}
    
    rpc_secret = os.environ.get('RPC_SECRET')
    if not rpc_secret:
        raise Exception(f"missing required RPC_SECRET environment variable")
    rpc_path = os.environ.get('RPC_PATH')

    rpc_config['origin_path'] = rpc_path if rpc_path else f'/ws/{db_name}'
    rpc_config['server_secret'] = rpc_secret

    rcp_enryption = os.environ.get('RPC_ENCRYPTION')
    if rcp_enryption:
        rpc_config['encryption_enabled'] = True if rcp_enryption == 1 else False
    

    # Rpc Server
    db_server = await EasyRpcServer.create(
        server, 
        **rpc_config
    )

    # Database Conection
    db = await Database.create(
        **db_config
    )

    # register each func table namespace 
    
        
    def register_table(table):
        async def insert(**kwargs):
            return await db.tables[table].insert(**kwargs)
        insert.__name__ = f"{table}_insert"

        async def select(*args, **kwargs):
            return await db.tables[table].select(*args, **kwargs)
        select.__name__ = f"{table}_select"

        async def update(**kwargs):
            return await db.tables[table].update(**kwargs)
        update.__name__ = f"{table}_update"
        
        async def delete(**kwargs):
            return await db.tables[table].delete(*args, **kwargs)
        delete.__name__ = f"{table}_delete"

        async def get_schema(**kwargs):
            return await db.tables[table].delete(*args, **kwargs)
        get_schema.__name__ = f"{table}_get_schema"

        for func in {insert, select, delete, select, get_schema}:
            db_server.origin(func, namespace=db_name)
    for table in db.tables:
        register_table(table)

    @db_server.origin(namespace=db_name)
    async def show_tables():
        table_list = []
        for table in db.tables:
            for func in {'insert', 'update', 'select', 'delete'}:
                if not f"{table}_func" in db_server.namespaces[db_name]:
                    register_table(table)
                    break
            table_list.append(table)
        return table_list
    
    async def refresh_show_tables():
        while True:
            try:
                db.log.warning(f"running show_tables to refresh {db_name} namespace ")
                await asyncio.sleep(10)
                await show_tables()
            except Exception as e:
                break

    
    db_server.origin(db.create_table, namespace=db_name)
    db_server.origin(db.run, namespace=db_name)

    asyncio.create_task(refresh_show_tables())

    server.db_server = db_server
    server.db = db


@server.on_event('shutdown')
async def shutdown():
    await server.db.close()