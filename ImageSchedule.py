from html2image import Html2Image

hti = Html2Image()
m_day = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
css_day = """table {
    font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
    font-size: 300%;
    border-spacing: 0;
    border-width: 10;
    text-align: center;
    width: 100%;
    height: 100%;
    }
    th {
    background: #405bab;
    color: white;
    padding: 50px 100px;
    height: 10%;
    }
    th, td {
    border-style: solid;
    border-width: 0 5px 5px 0;
    border-color: white;
    }
    th:first-child, td:first-child {
    text-align: left;
    }
    td {
    padding: 50px 100px;
    background: #e5f1fd;
    }
    tr td:last-child {
    border-right: none;
    }"""

css_week = """table {
    font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
    font-size: 200%;
    border-spacing: 0;
    text-align: center;
    width: 100%;
    height: 100%;
    }
    th {
    background: #405bab;
    color: white;
    
    height: 10%;
    width: 14.28%;
    }
    th, td {
    border-style: solid;
    border-color: white;
    }
    
    th:first-child{
    width: 8%;
    }
    td {
    text-align: left;
    vertical-align: top;
    background: #e5f1fd;
    }
    
    """

def short_fio(fio):
    fio = fio.split(' ')
    return fio[0] + " " + fio[1][0] + '.' + fio[2][0] + '.'

def short_type(type_pair):
    if type_pair == 'практика':
        return 'пр. '
    if type_pair == 'уч.практика':
        return 'уч.пр. '
    return type_pair[0:3] + '. '

def scheduleImageday(schedule, day):
    line = ""
    if schedule:
        n = len(schedule) * 400
        for elem in schedule:
            line +=  "<tr><td>" + elem[1] + "-" + elem[2] + "</td><td>" + short_type(elem[3]) + elem[0] + "<br><i>" + short_fio(elem[4]) + "</i><br><b>" + elem[5] + "</b></td></tr>"
    else:
        n = 400
        line = "<tr><td></td><td>Занятий нет</td></tr>"
    html = f"""
            <table class="tftable" border="1">
            <tr><th>Время</th><th>{m_day[day]}</th></tr>
            {line}
            </table>
            """
    hti.screenshot(html_str=html, css_str=css_day, save_as='red_page.png',size=(2000, 200 + n))

def scheduleImageWeek(schedule_week):
    time_mas = ['8:30-10.00', '10:10-11.40', '11:50-13.20', '13:50-15.20', '15:30-17.00', '17:10-18.40']

    html = f"""
            <table class="tftable" border="1">
            <tr><th>Время</th>"""

    for day in m_day.values():
        if day == 'Воскресенье':
            continue
        html += "<th>" + day + "</th>"

    for time in time_mas:
        line = ""
        line += "<tr> <th>" + time + "</th>"
        for schedule in schedule_week:
            line += "<td>"
            for disc in schedule:
                if disc[2] == time[-5:]:
                    line += disc[0] + "<br>"
            line += "</td>"

        line += "</tr>"
        html += line

    html += "</table>"

    hti.screenshot(html_str=html, css_str=css_week, save_as='red_page.png', size=(4000, 1300))