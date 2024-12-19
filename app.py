from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from functions import connect_to_db, create_table_violations, connect_and_save_violations, drop_table, create_table_residents, connect_and_save_residents
from model_launch_function import decode_batch, model_launch

import psycopg2
from psycopg2 import sql
import glob
import requests,io
from io import BytesIO
import datetime
from datetime import datetime

app = Flask(__name__)

# Перезагрузка папки с фотографиями
tich_file=glob.glob('./Object_Detection/test/*')
# print(len(tich_file),tich_file)

@app.route('/')
def index():
    global show_interaction_window
    show_interaction_window = 0 # Окно взаимодействия с нейросетью скрыто
    return render_template('index.html')

@app.route('/violators')
def violators():
    global show_interaction_window
    show_interaction_window = 0 # Окно взаимодействия с нейросетью скрыто
    return render_template('violators.html')

@app.route('/start', methods=['POST'])
def start():
    global current_image_index
    current_image_index = 0  # Сбрасываем индекс изображений
    global show_interaction_window
    show_interaction_window = 1 
    return redirect(url_for('show_image'))

@app.route('/image')
def show_image():
    # for current_image_index in range(len(tich_file)):
    global current_image_index
    global show_interaction_window
    if current_image_index < len(tich_file):
        pred_texts, path = model_launch(tich_file, current_image_index)
        global text 
        # for text in pred_texts:
        text = pred_texts[0]
        return render_template('violators.html', show_interaction_window=show_interaction_window, pred_text=pred_texts, path=path)
    else:
        return "Все изображения обработаны!"

@app.route('/answer', methods=['POST'])
def answer():
    global current_image_index
    global text 
    answer = request.form['answer']
    
    comment = request.form.get('comment', '')
    address = request.form.get('address', '')

    date = request.form.get('date', '')
    # Проверяем, выбрана ли опция "использовать сегодняшнюю"
    if request.form.get('use_today'):
        date = datetime.today().strftime("%Y-%m-%d")

    print(f"Текущий номер: {text}")
    print(f"Ответ пользователя на данное ТС {answer}")

    if not answer:
        return render_template('index.html')
    elif answer.lower() == "да":
            conn = connect_to_db()  # Соединяемся с БД
            create_table_violations(conn) # Создание таблицы
            connect_and_save_violations(conn, text, comment, address, date) # Сохранение в БД
            conn.close()  #Закрытие соединения с БД

    else:
        print('Ответ - нет')

    # result = 'Все случаи проверены.'
    # return render_template('index.html', result=result)

    current_image_index += 1  # Переходим к следующему изображению
    return redirect(url_for('show_image'))

@app.route('/image/<path:filename>')
def image(filename):
    return send_file(filename)

###############################################################################

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

###############################################################################

@app.route('/residents', methods=['GET', 'POST'])
def residents():
    return render_template('residents.html')

@app.route('/add_resident', methods=['POST'])
def add_resident():
    if request.method == 'POST':
        conn = connect_to_db()
        cursor = conn.cursor()
        number = request.form['number']
        car_model = request.form['car_model']
        owner = request.form['owner']
        conn = connect_to_db()  
        create_table_residents(conn) 
        connect_and_save_residents(conn, number, car_model, owner) 
        conn.close()
        return redirect(url_for('residents')) #вероятно после выполнения возвращается обратно на основную страницу о жителях

@app.route('/list_residents', methods=['GET'])
def list_residents():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM residents_Lunnaya_10')
    residents = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('residents.html', residents=residents)

@app.route('/check_resident', methods=['POST'])
def check_resident():
    conn = connect_to_db()
    cursor = conn.cursor()
    number = request.form['number']
    cursor.execute('SELECT * FROM residents_Lunnaya_10 WHERE number = %s', (number,))
    resident = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if resident:
        flag_yes=1
        return render_template('residents.html', check_result=resident, flag_yes=flag_yes)
    else:
        flag_no=1
        return render_template('residents.html', check_result='Resident not found.', flag_no=flag_no)
    
    

if __name__ == '__main__':
    app.run(debug=True)


