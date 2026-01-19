#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import click

from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string"
}

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-password', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for ingestion')
@click.option('--target-table', default='zone', help='Zone of the data')


def run(pg_user,pg_password, pg_host, pg_port, pg_db, target_table, chunksize):
    
    prefix = 'https://d37ci6vzurychx.cloudfront.net/misc'
    url = f'{prefix}/taxi_zone_lookup.csv'

    print(f"Downloading from: {url}")
    print(f"Chunksize: {chunksize}")
    print(f"Target table: {target_table}")
    
    engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
    
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        iterator=True,
        chunksize=chunksize,
    )

    first = True
    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(
                name=target_table, 
                con=engine,
                if_exists='replace'
            )
            first = False
            
        df_chunk.to_sql(
            name=target_table, 
            con=engine,
            if_exists='append'
        )

if __name__ == '__main__':
    run()