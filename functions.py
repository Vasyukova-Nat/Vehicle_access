import psycopg2
from psycopg2 import sql

def connect_to_db(): # Подключение к БД
    conn = psycopg2.connect(
            dbname="traffic_violators",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
    )
    return conn

###############################################################################
# Таблица нарушителей #

def create_table_violations(conn):
    try:
        cursor = conn.cursor() 

        # SQL-запрос для создания таблицы
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS violations (
            id SERIAL PRIMARY KEY,
            number TEXT,
            comment TEXT,
            address TEXT,
            date DATE
        );
        '''

        cursor.execute(create_table_query) # Выполнение запроса
        conn.commit() # Сохранение изменений
        print("Таблица успешно создана")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        
    finally:
        if cursor:
            cursor.close() # Закрытие 

def connect_and_save_violations(conn, number: str, comment: str, address: str, date: str):
    cursor = conn.cursor()
    try:
        # SQL-запрос для вставки данных
        insert_query = sql.SQL("INSERT INTO violations (number, comment, address, date) VALUES (%s, %s, %s, %s)")  
        cursor.execute(insert_query, (number, comment, address, date)) # Выполнение запроса    
        conn.commit() # Сохранение изменений
        print("Данные успешно сохранены в БД")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        
    finally:
        if cursor: # Закрытие курсора
            cursor.close()

def drop_table(): # Функция для удаления таблицы
    try:
        connection = psycopg2.connect(
                dbname="traffic_violators",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS violations")
    
        connection.commit()
        cursor.close()
        print("Таблица 'violations' успешно удалена.")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    finally:
        if cursor:
            cursor.close() #Закрытие курсора

###############################################################################
# Таблица жильцов дома #

def create_table_residents(conn):
    try:
        cursor = conn.cursor() 

        # SQL-запрос для создания таблицы
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS residents_Lunnaya_10 (
            id SERIAL PRIMARY KEY,
            number TEXT,
            car_model TEXT,
            owner TEXT
        );
        '''

        cursor.execute(create_table_query) # Выполнение запроса
        conn.commit() # Сохранение изменений
        print("Таблица жителей дома 10 на улице Лунной успешно создана")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        
    finally:
        if cursor:
            cursor.close() # Закрытие 

def connect_and_save_residents(conn, number: str, car_model: str, owner: str):
    cursor = conn.cursor()
    try:
        # SQL-запрос для вставки данных
        insert_query = sql.SQL("INSERT INTO residents_Lunnaya_10 (number, car_model, owner) VALUES (%s, %s, %s)")  
        cursor.execute(insert_query, (number, car_model, owner)) # Выполнение запроса    
        conn.commit() # Сохранение изменений
        print("Данные успешно сохранены в БД")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        
    finally:
        if cursor: # Закрытие курсора
            cursor.close()

def check_resident_in_table(conn, number: str):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM residents_Lunnaya_10 WHERE number = %s', (number,))
        resident = cursor.fetchone()
        conn.commit() 
        return resident  
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    finally:
        if cursor: # Закрытие курсора
            cursor.close()

###############################################################################
# Работа с файлом .txt , содержащем подписи к фотографиям нарушений #
# Функция для получения информации о фотографии
def get_photo_info(index, captions_file):
    with open(captions_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if index < len(lines):
            return lines[index].strip().split(';')  # Предполагаем, что данные разделены запятыми
        else:
            return None

