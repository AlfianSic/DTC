

#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import click
import warnings
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine
from tqdm.auto import tqdm

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-password', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default='2025', type=int, help='Year of the data')
@click.option('--month', default='11', type=int, help='Month of the data')
@click.option('--chunksize', default='100000', type=int, help='Chunk size for ingestion')
@click.option('--target-table', default='green_taxi_data', help='Target table name')

def run(pg_user,pg_password, pg_host, pg_port, pg_db, year, month, target_table,chunksize):
    
    prefix = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
    url = f'{prefix}/green_tripdata_{year}-{month:02}.parquet'
    print(f"Downloading from: {url}")
    print(f"Chunksize: {chunksize}")
    print(f"Target table: {target_table}")
    
    engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
    
    df = pd.read_parquet(url)

    for i in tqdm(range(0,len(df),chunksize)):
        df_chunk = df.iloc[i:i+chunksize]
        if i == 0:
            df_chunk.head(0).to_sql(
                name=target_table, 
                con=engine,
                if_exists='replace'
            )
            
        df_chunk.to_sql(
            name=target_table, 
            con=engine,
            if_exists='append'
        )

if __name__ == '__main__':
    run()