import psycopg2
import requests
from datetime import datetime, timedelta

host = "127.0.0.1"
user = "postgres"
password = "356211"
dbname = "test"

connection = psycopg2.connect(host=host, user=user, password=password, database=dbname)
url = "http://raspmath.isu.ru/getSchedule"
data = requests.get(url)
begin_date_pairs = data.json()[0]["begin_date_pairs"]
end_date_pairs = data.json()[0]["end_date_pairs"]

def check_group(group):
    cursor = connection.cursor()
    cursor.execute(f"SELECT number FROM group_number WHERE number = '{group}'")
    result = cursor.fetchone()
    connection.commit()
    cursor.close()
    return result


def get_group():
    cursor = connection.cursor()
    cursor.execute("SELECT number FROM group_number")
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    return result


def load_descipline():
    insert_query = "INSERT INTO descipline (name) VALUES "
    cursor = connection.cursor()
    cursor.execute("DELETE from descipline")
    connection.commit()
    for elem in data.json():
        subject_name = elem['subject_name']
        if not f"'{subject_name}'" in insert_query:
            insert_query += '(\'' + subject_name + '\')' + ', '
    cursor.execute(insert_query[:-2])
    connection.commit()
    cursor.close()


def load_teacher():
    insert_query = "INSERT INTO teacher (fio) VALUES "
    cursor = connection.cursor()
    for elem in data.json():
        FIO = elem['lastname'] + " " + elem['firstname'] + " " + elem['patronymic']
        if not FIO in insert_query:
            insert_query += '(\'' + FIO + '\')' + ', '
    cursor.execute(insert_query[:-2])
    connection.commit()
    cursor.close()


def load_group():
    insert_query = "INSERT INTO group_number (number) VALUES "
    cursor = connection.cursor()
    for elem in data.json():
        group_number = elem['group_name']
        if not group_number in insert_query:
            insert_query += '(\'' + group_number + '\')' + ', '
    cursor.execute(insert_query[:-2])
    connection.commit()
    cursor.close()


def load_audience():
    insert_query = "INSERT INTO audience (name) VALUES "
    cursor = connection.cursor()
    for elem in data.json():
        audience = elem['class_name']
        if not audience in insert_query:
            insert_query += '(\'' + audience + '\')' + ', '
    cursor.execute(insert_query[:-2])
    connection.commit()
    cursor.close()


def load_pair_type():
    insert_query = "INSERT INTO type_pair (name) VALUES "
    cursor = connection.cursor()
    for elem in data.json():
        pair_type = elem['pair_type']
        if not pair_type in insert_query:
            insert_query += '(\'' + pair_type + '\')' + ', '
    cursor.execute(insert_query[:-2])
    connection.commit()
    cursor.close()


def load_pair_time():
    insert_query = "INSERT INTO time (start_time, end_time) VALUES "
    cursor = connection.cursor()
    for elem in data.json():
        start_time = elem['pair_start_time']
        end_time = elem['pair_end_time']
        if not start_time in insert_query and not end_time in insert_query:
            insert_query += '(\'' + start_time + '\'' + ", " + '\'' + end_time + '\')' + ', '
    cursor.execute(insert_query[:-2])
    connection.commit()
    cursor.close()


def load_week():
    insert_query = "INSERT INTO week (parity, dayweek) VALUES "
    cursor = connection.cursor()
    for elem in data.json():
        if not elem['week_type']:
            parity = 0
        elif elem['week_type'] == 'нижняя':
            parity = 1
        elif elem['week_type'] == 'верхняя':
            parity = 2
        day = elem['weekday']
        if not f"('{parity}', '{day}')" in insert_query:
            insert_query += '(\'' + str(parity) + '\'' + ", " + '\'' + day + '\')' + ', '
    cursor.execute(insert_query[:-2])
    connection.commit()
    cursor.close()


def load_schedule():
    schedule = []
    cursor = connection.cursor()
    cursor.execute("DELETE from shedule")
    for elem in data.json():

        if not elem['week_type']:
            parity = 0
        elif elem['week_type'] == 'нижняя':
            parity = 1
        elif elem['week_type'] == 'верхняя':
            parity = 2

        cursor.execute(f"SELECT id FROM group_number WHERE number = '{elem['group_name']}'")
        group_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM time WHERE start_time = '{elem['pair_start_time']}'")
        time_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM type_pair WHERE name = '{elem['pair_type']}'")
        type_pair_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM week WHERE parity = '{parity}' and dayweek = '{elem['weekday']}'")
        week_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM descipline WHERE name = '{elem['subject_name']}'")
        descipline_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM audience WHERE name = '{elem['class_name']}'")
        audience_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM teacher WHERE fio = '{elem['lastname']} {elem['firstname']} {elem['patronymic']}'")
        teacher_id = cursor.fetchone()[0]
        schedule.append((group_id, time_id, type_pair_id, week_id, descipline_id, audience_id, teacher_id))

    insert_query = "INSERT INTO shedule (group_number_id, time_id, type_pair_id, week_id, descipline_id, audience_id, teacher_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(insert_query, schedule)
    connection.commit()
    cursor.close()

def insert_user(user_id, number_group):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id FROM user_telegram WHERE id = '{user_id}'")
    if not cursor.fetchone():
        cursor.execute(f"SELECT id FROM group_number WHERE number = '{number_group}'")
        group_id = cursor.fetchone()[0]
        cursor.execute(f"INSERT INTO user_telegram (id, group_number_id) VALUES ({user_id}, {group_id})")
        connection.commit()
        cursor.close()
        return True
    else:
        cursor.close()
        return False


def get_number_group_id_by_user(user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT group_number_id FROM user_telegram WHERE id = '{user_id}'")
    return cursor.fetchone()[0]


def get_schedule_one_day(user_id, date):
    cursor = connection.cursor()
    group_number_id = get_number_group_id_by_user(user_id)
    m_day = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    cursor.execute(f"SELECT id, parity FROM week WHERE dayweek = '{m_day[datetime.weekday(date)]}' ")
    days = cursor.fetchall()

    cursor.execute(f"SELECT start_time FROM time")
    schedule = []

    cursor.execute(f"SELECT number FROM group_number WHERE id = '{group_number_id}'")
    print("Расписание для группы: " + cursor.fetchone()[0])
    #=============================================================================================
    #Расписание на 1 день
    for day in days:
        if day[1] == 0 or day[1] == get_parity(date):
            cursor.execute(f"SELECT group_number_id, time_id, descipline_id FROM shedule WHERE group_number_id = '{group_number_id}' and week_id = '{day[0]}'")

            for elem in cursor.fetchall():
                cursor.execute(f"SELECT name FROM descipline WHERE id = '{elem[2]}'")
                descipline = cursor.fetchone()[0]
                cursor.execute(f"SELECT start_time, end_time FROM time WHERE id = '{elem[1]}'")
                time = cursor.fetchone()
                schedule.append([descipline, time[0], time[1]])
    #==============================================================================================
    schedule.sort(key=lambda x: x[2])
    print(schedule)
    cursor.close()
    return schedule


def get_schedule_week(user_id, date):
    cursor = connection.cursor()
    group_number_id = get_number_group_id_by_user(user_id)
    m_day = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    minus = datetime.weekday(date)
    date -= timedelta(days = minus)

    cursor.execute(f"SELECT number FROM group_number WHERE id = '{group_number_id}'")
    print("Расписание для группы: " + cursor.fetchone()[0])
    for i in range(6):
        cursor.execute(f"SELECT id, parity FROM week WHERE dayweek = '{m_day[datetime.weekday(date)]}' ")
        days = cursor.fetchall()

        cursor.execute(f"SELECT start_time FROM time")
        schedule = []

        cursor.execute(f"SELECT number FROM group_number WHERE id = '{group_number_id}'")

        for day in days:
            if day[1] == 0 or day[1] == get_parity(date):
                cursor.execute(f"SELECT group_number_id, time_id, descipline_id FROM shedule WHERE group_number_id = '{group_number_id}' and week_id = '{day[0]}'")
                #иф для препода и студента

                for elem in cursor.fetchall():
                    cursor.execute(f"SELECT name FROM descipline WHERE id = '{elem[2]}'")
                    descipline = cursor.fetchone()[0]
                    cursor.execute(f"SELECT start_time, end_time FROM time WHERE id = '{elem[1]}'")
                    time = cursor.fetchone()
                    schedule.append([descipline, time[0], time[1]])
        schedule.sort(key=lambda x: x[2])
        print(m_day[i], ":")
        print(schedule)
        date += timedelta(days = 1)
    cursor.close()

def get_parity(date):
    d1 = datetime.strptime(begin_date_pairs, "%Y-%m-%d")
    return (2 - (date - d1).days // 7 % 2)










# load_descipline()
# load_schedule()
# load_teacher()
# load_group()
# load_audience()
# load_pair_type()
# load_pair_time()
# load_week()
# load_schedule()
# {
#   'id': 1,
#   'group_name': '02121-ДБ',
#   'weekday': 'Понедельник',
#   'pair_start_time': '10.10',
#   'pair_end_time': '11.40',
#   'subject_name': 'Иностранный язык',
#   'pair_type': 'практика',
#   'lastname': 'Петрова',
#   'firstname': 'Наталья',
#   'patronymic': 'Васильевна',
#   'class_name': '222',
#   'week_type': '',
#   'begin_date_pairs': '2022-02-07',
#   'end_date_pairs': '2022-06-11'
# }

#----поиск изменений
#----расписание для преподователей
#----изменение информации о пользователе
#