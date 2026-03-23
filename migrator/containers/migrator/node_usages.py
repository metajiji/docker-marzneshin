import os
import logging
import sqlalchemy


class MarzbanMigrator:
    def __init__(self, src_url: str, dest_url: str, chunk_size: int = 1000):
        self.src_engine = sqlalchemy.create_engine(src_url)
        self.dest_engine = sqlalchemy.create_engine(dest_url)
        self.chunk_size = chunk_size

        self.src_metadata = sqlalchemy.MetaData()
        self.dest_metadata = sqlalchemy.MetaData()

        self.src_conn = None
        self.dest_conn = None

    def __enter__(self):
        """Initializes connections when entering 'with' block."""
        self.src_conn = self.src_engine.connect()
        self.dest_conn = self.dest_engine.connect()
        logging.info('Connected to source and destination databases.')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes connections when exiting 'with' block."""
        if self.src_conn:
            self.src_conn.close()
        if self.dest_conn:
            self.dest_conn.close()
        logging.info('Database connections closed.')

    def migrate_usage_logs(self, tables: list[str]):
        """Copies log tables row-by-row in chunks."""
        for table_name in tables:
            logging.info(f'Migrating table: {table_name}')

            # Reflect schema
            table = sqlalchemy.Table(table_name, self.src_metadata, autoload_with=self.src_engine)
            result = self.src_conn.execute(sqlalchemy.select(table))

            while True:
                rows = result.fetchmany(self.chunk_size)
                if not rows:
                    break

                data = [row._asdict() for row in rows]
                try:
                    with self.dest_conn.begin():
                        self.dest_conn.execute(sqlalchemy.insert(table), data)
                except sqlalchemy.exc.IntegrityError:
                    logging.warning(f'Duplicates found in {table_name}, skipping batch.')
                    continue

    def sync_user_traffic(self):
        """Syncs total used_traffic from Marzban to Marzneshin users."""
        logging.info("Syncing user traffic totals...")

        src_users = sqlalchemy.Table('users', self.src_metadata, autoload_with=self.src_engine)
        dest_users = sqlalchemy.Table('users', self.dest_metadata, autoload_with=self.dest_engine)

        result = self.src_conn.execute(sqlalchemy.select(src_users.c.username, src_users.c.used_traffic))

        while True:
            rows = result.fetchmany(self.chunk_size)
            if not rows:
                break

            # Bulk update mapping
            payload = [
                {
                    'u_name': self._normalize_username(r.username),
                    'val': r.used_traffic
                }
                for r in rows if r.username
            ]

            with self.dest_conn.begin():
                stmt = (
                    sqlalchemy.update(dest_users)
                    .where(dest_users.c.username == sqlalchemy.bindparam('u_name'))
                    .values(used_traffic=sqlalchemy.bindparam('val'))
                )
                self.dest_conn.execute(stmt, payload)

            logging.info(f'Updated traffic for {len(payload)} users.')

    def sync_user_created_at(self):
        """Syncs created_at from Marzban to Marzneshin users."""
        logging.info("Syncing user created_at...")

        src_users = sqlalchemy.Table('users', self.src_metadata, autoload_with=self.src_engine)
        dest_users = sqlalchemy.Table('users', self.dest_metadata, autoload_with=self.dest_engine)

        result = self.src_conn.execute(sqlalchemy.select(src_users.c.username, src_users.c.created_at))

        while True:
            rows = result.fetchmany(self.chunk_size)
            if not rows:
                break

            # Bulk update mapping
            payload = [
                {
                    'u_name': self._normalize_username(r.username),
                    'val': r.created_at,
                } for r in rows if r.username
            ]

            with self.dest_conn.begin():
                stmt = (
                    sqlalchemy.update(dest_users)
                    .where(dest_users.c.username == sqlalchemy.bindparam('u_name'))
                    .values(created_at=sqlalchemy.bindparam('val'))
                )
                self.dest_conn.execute(stmt, payload)

            logging.info(f'Updated created_at for {len(payload)} users.')

    def _normalize_username(self, username: str) -> str:
        """Converts 'User-Name' to 'user_name' to match destination format."""
        if not username:
            return ''
        return username.lower().replace('-', '_')


if __name__ == '__main__':
    # Setup logging
    logging.getLogger().setLevel(logging.INFO)

    # Paths from environment
    src_db = f'sqlite:///{os.environ.get("SQLITE_PATH")}'
    dest_db = f'sqlite:///{os.environ.get("MARZNESHIN_SQLITE_PATH")}'

    try:
        with MarzbanMigrator(src_db, dest_db) as migrator:
            tables_to_copy = (
                'node_usages',
                'node_user_usages',
            )
            # migrator.migrate_usage_logs(tables_to_copy)
            migrator.sync_user_traffic()
            migrator.sync_user_created_at()
        logging.info('Migration finished successfully!')
    except Exception as e:
        logging.error(f'Migration failed: {e}')
        exit(1)
