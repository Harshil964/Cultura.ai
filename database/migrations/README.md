# Reserved: schema migrations

Not used yet — `database/connection.init_db()` currently just calls
`Base.metadata.create_all()`, which creates missing tables but never
alters existing ones. That's fine for the MVP (SQLite file, single dev),
but if you move to Postgres with real data you don't want to lose,
introduce Alembic and put its migration scripts here:

    pip install alembic
    alembic init database/migrations
