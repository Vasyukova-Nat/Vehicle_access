from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from functions import connect_to_db, create_table_violations, connect_and_save_violations, drop_table, create_table_residents, connect_and_save_residents, check_resident_in_table, get_photo_info
from model_launch_function import decode_batch, model_launch

import psycopg2
from psycopg2 import sql
import glob
# import requests,io
# from io import BytesIO
import datetime
from datetime import datetime

app = Flask(__name__)

# Перезагрузка папки с фотографиями
tich_file = glob.glob('./Object_Detection/test/*')
# print(len(tich_file),tich_file)
captions_file = './Object_Detection/photo_captions.txt'

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
        global violation_name 
        global violation_address
        global violation_date
        violation_name, violation_address, violation_date = get_photo_info(current_image_index, captions_file) # violation_name - это название нарушения, комментарий.
        # for text in pred_texts:
        text = pred_texts[0]
        return render_template('violators.html', show_interaction_window=show_interaction_window, pred_text=pred_texts, path=path, violation_name=violation_name, violation_address=violation_address, violation_date=violation_date)
    else:
        return render_template('completed.html')

@app.route('/answer', methods=['POST'])
def answer():
    global current_image_index
    global text 
    global violation_name 
    global violation_address
    global violation_date

    print(f"Текущий номер: {text}")
    if request.method == 'POST':
        if 'report_error' in request.form:  # Если нажата кнопка "Сообщить об ошибке"
            # error_message = request.form.get('error_message', 'Без описания ошибки')  # Получаем текст ошибки
            # send_vk_message(error_message)  # Отправляем сообщение в VK
            return "Сообщение об ошибке отправлено!"  # Возвращаем ответ пользователю
        conn = connect_to_db()  # Соединяемся с БД
        create_table_violations(conn) # Создание таблицы
        connect_and_save_violations(conn, text, violation_name, violation_address, violation_date) # Сохранение в БД
        conn.close()  #Закрытие соединения с БД
        # return "Данные успешно сохранены в базу данных!"  # Возвращаем ответ пользователю
        
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
    conn = connect_to_db()  # Соединяемся с БД
    create_table_violations(conn) # Создание таблицы
    number = request.form['number']
    resident = check_resident_in_table(conn, number) 
    conn.close()

    if resident:
        flag_yes=1
        return render_template('residents.html', check_result=resident, flag_yes=flag_yes)
    else:
        flag_no=1
        return render_template('residents.html', check_result='Resident not found.', flag_no=flag_no)

# Перезагрузка папки с фотографиями
tich_file=glob.glob('./Object_Detection/photos_from_video_camera/*')

@app.route('/start_showing_video_camera', methods=['POST'])
def start_showing_video_camera():
    global current_image_index
    current_image_index = 0  # Сбрасываем индекс изображений
    return redirect(url_for('show_video_camera'))

@app.route('/show_video_camera', methods=['GET', 'POST'])
def show_video_camera():
    global current_image_index 
    if request.method == 'POST': # Обработка запроса на нажатие кнопки "Далее"
        current_image_index += 1

    if current_image_index < len(tich_file):
        pred_resident_car_number, path = model_launch(tich_file, current_image_index)
        conn = connect_to_db()
        create_table_violations(conn)
        resident = check_resident_in_table(conn, pred_resident_car_number[0]) 
        if resident:
            return render_template('show_video_camera.html', check_result=resident, flag_yes=1, pred_resident_car_number=pred_resident_car_number, resident=resident, path=path)
        else:
            return render_template('show_video_camera.html', check_result='Resident not found.', flag_no=1, pred_resident_car_number=pred_resident_car_number, resident=resident, path=path)

    else:
        return render_template('completed.html')

if __name__ == '__main__':
    app.run(debug=True)


