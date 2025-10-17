from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

engine = create_engine(f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}", echo=True)

meta = MetaData()

users = Table(
    "users",
    meta,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('age', Integer),
    Column('address', String)
)

meta.create_all(engine)

conn = engine.connect()

stmnt = users.update().where((users.c.age > 30) & (users.c.name == "John Lt2.")).values(name="John Lt2.", address="New York").returning()
res = conn.execute(stmnt)
conn.commit()
