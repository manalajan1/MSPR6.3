import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import uvicorn

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

# Connexion à PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

app = FastAPI(title="API MSPR6.1 CRUD")


class CovidItem(BaseModel):
    id: int
    country_region: str
    date: str
    total_cases: float
    total_deaths: float
    total_gueris: float

class CovidCreate(BaseModel):
    country_region: str
    date: str
    total_cases: float
    total_deaths: float
    total_gueris: float

class MpoxItem(BaseModel):
    id: int
    country_region: str
    date: str
    total_cases: float
    total_deaths: float
    total_recovered: float

class MpoxCreate(BaseModel):
    country_region: str
    date: str
    total_cases: float
    total_deaths: float
    total_recovered: float

# -------------------------------
# Helpers
# -------------------------------
def fetchall_dicts(query: str, params=None):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params or ())
        return cur.fetchall()

def fetchone_dict(query: str, params=None):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params or ())
        return cur.fetchone()

# -------------------------------
# Routes COVID19_DAILY
# -------------------------------
@app.get("/api/covid19_daily", response_model=List[CovidItem])
def read_covid():
    query = """
        SELECT
            id,
            country_region,
            date,
            total_cases,
            total_deaths,
            total_gueris
        FROM covid19_daily
    """
    return fetchall_dicts(query)

@app.post("/api/covid19_daily", response_model=CovidItem, status_code=201)
def create_covid(item: CovidCreate):
    query = """
        INSERT INTO covid19_daily (country_region, date, total_cases, total_deaths, total_gueris)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, country_region, date, total_cases, total_deaths, total_gueris
    """
    row = fetchone_dict(query, [
        item.country_region,
        item.date,
        item.total_cases,
        item.total_deaths,
        item.total_gueris
    ])
    return row

@app.put("/api/covid19_daily/{id}", response_model=CovidItem)
def update_covid(id: int, item: CovidCreate):
    query = """
        UPDATE covid19_daily
        SET country_region = %s,
            date           = %s,
            total_cases    = %s,
            total_deaths   = %s,
            total_gueris   = %s
        WHERE id = %s
        RETURNING id, country_region, date, total_cases, total_deaths, total_gueris
    """
    row = fetchone_dict(query, [
        item.country_region,
        item.date,
        item.total_cases,
        item.total_deaths,
        item.total_gueris,
        id
    ])
    if not row:
        raise HTTPException(status_code=404, detail="Data not found")
    return row

@app.delete("/api/covid19_daily/{id}", response_model=CovidItem)
def delete_covid(id: int):
    query = """
        DELETE FROM covid19_daily
        WHERE id = %s
        RETURNING id, country_region, date, total_cases, total_deaths, total_gueris
    """
    row = fetchone_dict(query, [id])
    if not row:
        raise HTTPException(status_code=404, detail="Data not found")
    return row

# -------------------------------
# Routes MPOX
# -------------------------------
@app.get("/api/mpox", response_model=List[MpoxItem])
def read_mpox():
    query = """
        SELECT
            id,
            "Country/Region" AS country_region,
            "Date"           AS date,
            "Total_Cases"    AS total_cases,
            "Total_Deaths"   AS total_deaths,
            "Total_Gueris"   AS total_recovered
        FROM mpox
    """
    return fetchall_dicts(query)

@app.post("/api/mpox", response_model=MpoxItem, status_code=201)
def create_mpox(item: MpoxCreate):
    query = """
        INSERT INTO mpox ("Country/Region", "Date", "Total_Cases", "Total_Deaths", "Total_Gueris")
        VALUES (%s, %s, %s, %s, %s)
        RETURNING
            id,
            "Country/Region" AS country_region,
            "Date"           AS date,
            "Total_Cases"    AS total_cases,
            "Total_Deaths"   AS total_deaths,
            "Total_Gueris"   AS total_recovered
    """
    row = fetchone_dict(query, [
        item.country_region,
        item.date,
        item.total_cases,
        item.total_deaths,
        item.total_recovered
    ])
    return row

@app.put("/api/mpox/{id}", response_model=MpoxItem)
def update_mpox(id: int, item: MpoxCreate):
    query = """
        UPDATE mpox
        SET "Country/Region" = %s,
            "Date"           = %s,
            "Total_Cases"    = %s,
            "Total_Deaths"   = %s,
            "Total_Gueris"   = %s
        WHERE id = %s
        RETURNING
            id,
            "Country/Region" AS country_region,
            "Date"           AS date,
            "Total_Cases"    AS total_cases,
            "Total_Deaths"   AS total_deaths,
            "Total_Gueris"   AS total_recovered
    """
    row = fetchone_dict(query, [
        item.country_region,
        item.date,
        item.total_cases,
        item.total_deaths,
        item.total_recovered,
        id
    ])
    if not row:
        raise HTTPException(status_code=404, detail="Data not found")
    return row

@app.delete("/api/mpox/{id}", response_model=MpoxItem)
def delete_mpox(id: int):
    query = """
        DELETE FROM mpox
        WHERE id = %s
        RETURNING
            id,
            "Country/Region" AS country_region,
            "Date"           AS date,
            "Total_Cases"    AS total_cases,
            "Total_Deaths"   AS total_deaths,
            "Total_Gueris"   AS total_recovered
    """
    row = fetchone_dict(query, [id])
    if not row:
        raise HTTPException(status_code=404, detail="Data not found")
    return row

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
