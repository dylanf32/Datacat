import pandas as pd
from sqlalchemy import URL, create_engine, text


def get_engine(username, password):
    """Configure a connection to the local Datacat database."""
    url = URL.create(
        drivername="mysql+pymysql",
        username=username,
        password=password,
        host="localhost",
        port=3306,
        database="datacat"
    )

    return create_engine(url)


def save_to_database(df, table_name, engine):
    """Save a DataFrame as a new table."""
    with engine.begin() as connection:
        df.to_sql(
            name=table_name,
            con=connection,
            if_exists="fail",
            index=False
        )


def run_query(query, engine, params=None):
    """Run a query that returns rows and return a DataFrame."""
    with engine.connect() as connection:
        return pd.read_sql_query(
            sql=text(query),
            con=connection,
            params=params
        )