import os
import logging
from sqlalchemy import create_engine, MetaData, Table, insert, select, exc

# Configuration
SOURCE_DB = f'sqlite:///{os.environ["SQLITE_PATH"]}'
DEST_DB = f'sqlite:///{os.environ["MARZNESHIN_SQLITE_PATH"]}'
CHUNK_SIZE = 1000  # Optimal batch size for SQLite performance/memory balance


def migrate_data(tables_to_copy: list[str]) -> None:
    src_engine = create_engine(SOURCE_DB)
    dest_engine = create_engine(DEST_DB)
    metadata = MetaData()

    # Open both connections in a single block
    try:
        with src_engine.connect() as src_conn, dest_engine.connect() as dest_conn:
            logging.info('Established connections to both databases.')

            for table_name in tables_to_copy:
                logging.info(f'Starting migration for table: {table_name}')

                # Reflect table schema from source
                table = Table(table_name, metadata, autoload_with=src_engine)

                # Execute select on source
                result_proxy = src_conn.execute(select(table))

                total_rows = 0
                while True:
                    rows = result_proxy.fetchmany(CHUNK_SIZE)
                    if not rows:
                        break

                    # Convert rows to dicts for the insert statement
                    data = [row._asdict() for row in rows]

                    try:
                        # Use a sub-transaction for each chunk
                        with dest_conn.begin():
                            dest_conn.execute(insert(table), data)

                        total_rows += len(data)
                        logging.info(f'Migrated {total_rows} rows so far for {table_name}...')

                    except exc.IntegrityError as e:
                        logging.warning(f'Integrity error in {table_name} (possibly duplicates): {e}')
                        # Depending on requirements, you could skip or handle specific rows here
                        continue

                logging.info(f'Finished migration for {table_name}. Total: {total_rows} rows.')

    except Exception as e:
        logging.error(f'Critical migration error: {e}')
        raise


if __name__ == '__main__':
    # Setup logging
    logging.getLogger().setLevel(logging.INFO)

    tables_to_copy = (
        'node_usages',
        'node_user_usages',
    )

    migrate_data(tables_to_copy)
