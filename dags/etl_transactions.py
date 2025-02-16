import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago

from datetime import timedelta


csv_file = "financial_transactions.csv"


def extract_csv():
    df = pd.read_csv(csv_file)
    return df


def clean_transaction_data(df):
    df['amount'] = df['amount'].replace({'\$': '', ',': '', '\s': ''}, regex=True)
    
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

    df['amount'] = df['amount'].abs()

    df['original_transaction_date'] = df['transaction_date']

    mask = df['transaction_date'].str.match(r"^\d{2}/\d{2}/\d{4}$", na=False)
    df.loc[mask, 'transaction_date'] = pd.to_datetime(df.loc[mask, 'transaction_date'], format='%m/%d/%Y', errors='coerce')

    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

    df['transaction_date'].fillna(pd.to_datetime('today').strftime('%Y-%m-%d'), inplace=True)

    df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d')

    df.drop_duplicates(subset=['transaction_id'], inplace=True)

    df.drop(columns=['original_transaction_date'], inplace=True)

    return df


def insert_transactions_and_log(df):
    try:
        hook = PostgresHook(postgres_conn_id='etl_task')
        engine = hook.get_sqlalchemy_engine()

        with engine.connect() as connection:
            for index, row in df.iterrows():
                check_transaction_id = "SELECT 1 FROM transactions WHERE transaction_id = %s"
                result = connection.execute(check_transaction_id, (row['transaction_id'],)).fetchone()

                if not result:
                    insert_stmt = """
                    INSERT INTO transactions (transaction_id, user_id, amount, transaction_date)
                    VALUES (%s, %s, %s, %s)
                    """
                    connection.execute(insert_stmt, 
                                       row['transaction_id'], 
                                       row['user_id'], 
                                       row['amount'], 
                                       row['transaction_date'])

    except Exception as e:
        print(f"Error inserting transactions: {e}")
        raise


def etl():
    df = extract_csv()
    df = clean_transaction_data(df)
    insert_transactions_and_log(df)


default_args = {
    'owner': 'OpenTax',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'etl_transactions',
    default_args=default_args,
    description='ETL pipeline for financial transactions',
    schedule_interval='0 0 * * *',
)

etl_task = PythonOperator(
    task_id='run_postgres_query',
    python_callable=etl,
    dag=dag,
)
