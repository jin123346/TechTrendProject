import os
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv
import oracledb



load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "postgresql").lower()



def get_postgres_connection() -> psycopg.Connection:
    databse_url = os.getenv("DATABASE_URL")
    if not databse_url:
        raise RuntimeError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
    
    return psycopg.connect(databse_url)

def get_oracle_connection() -> oracledb.Connection:
    user  = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    host = os.getenv("ORACLE_HOST")
    port = os.getenv("ORACLE_PORT", "1521")
    service_name = os.getenv("ORACLE_SERVICE_NAME")
    oracle_client_path = os.getenv("ORACLE_CLIENT_PATH")
    if oracle_client_path:
        oracledb.init_oracle_client(
            lib_dir=oracle_client_path
        )
    
    if not user or not password or not host or not service_name:
        raise RuntimeError("Oracle 연결에 필요한 환경변수가 설정되지 않았습니다.")
    
    dsn = oracledb.makedsn(host=host, port=int(port), service_name=service_name)

    return oracledb.connect(user=user, password=password, dsn=dsn)
    


def get_connection() -> psycopg.Connection:
    if DB_TYPE == "postgresql":
        return get_postgres_connection()
    elif DB_TYPE == "oracle":
        return get_oracle_connection()
    else:
        raise ValueError(f"지원되지 않는 DB_TYPE: {DB_TYPE}")
    

def initialize_oracle_database() -> None:
    try:
        with get_oracle_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM dual")
                result = cursor.fetchone()

        if result != (1,):
            raise RuntimeError("Oracle 연결 테스트 결과가 올바르지 않습니다.")

        print("Oracle 연결 확인 완료")

    except Exception as error:
        print(f"Oracle 데이터베이스 초기화 중 오류 발생: {error}")
        raise

def initialize_postgres_database() -> None:
    schema_path = (
        Path(__file__).parent / "postgre" / "postgre_schema.sql"
    )
    if not schema_path.exists():
        raise FileNotFoundError(
            f"PostgreSQL 스키마 파일을 찾을 수 없습니다: {schema_path}"
        )
        
        
    schema_sql = schema_path.read_text(encoding="utf-8")
    
    try:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(schema_sql)
                
                
            connection.commit()
            
            print("PostgreSQL 연결 확인 완료")
            
    except Exception as e:
        print(f"PostgreSQL 데이터베이스 초기화 중 오류 발생: {e}")
        raise
        


def initialize_database() -> None:
    if DB_TYPE == "postgresql":
        initialize_postgres_database()
    elif DB_TYPE == "oracle":
        initialize_oracle_database()
    else:
        raise ValueError(f"지원되지 않는 DB_TYPE: {DB_TYPE}")


if __name__ == "__main__":
    initialize_database()
    print("데이터베이스 초기화가 완료되었습니다.")