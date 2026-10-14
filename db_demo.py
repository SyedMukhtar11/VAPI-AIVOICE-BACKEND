from __future__ import annotations

from sqlalchemy import text

from database import engine,init_db

def run_sql_query(query:str):
    init_db()
    with engine.begin() as conn:
        result = conn.execute(text(query))
        return result.fetchall if result.returns_rows else result.rowcount
    
query = """SELECT  * FROM APPOINTMENTS"""
run_sql_query(query=query)