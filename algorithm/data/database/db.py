from sqlalchemy import create_engine

DATABASE_URL = ("postgresql://postgres:roblox80@localhost:5432/tradingAI_History")

engine = create_engine(DATABASE_URL)

from sqlalchemy import text

with engine.connect() as conn:
    print(conn.execute(text("SELECT current_database();")).fetchone())