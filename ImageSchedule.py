from html2image import Html2Image

hti = Html2Image()
m_day = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
css = """table {
    font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
    font-size: 400%;
    border-spacing: 0;
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

def scheduleImageday(schedule, day):
    line = ""
    if schedule:
        n = len(schedule) * 400
        for elem in schedule:
            line +=  "<tr><td>" + elem[1] + "-" + elem[2] + "</td><td>" + elem[0] + "</td></tr>"
    else:
        n = 400
        line = "<tr><td></td><td>Занятий нет</td></tr>"
    html = f"""
            <table class="tftable" border="1">
            <tr><th>Время</th><th>{m_day[day]}</th></tr>
            {line}
            </table>
            """
    hti.screenshot(html_str=html, css_str=css, save_as='red_page.png',size=(2000, 200 + n))

def scheduleImageWeek(schedule_week):
    i = 0
    for schedule in schedule_week:
        line = ""
        if schedule:
            n = len(schedule) * 400
            for elem in schedule:
                line += "<tr><td>" + elem[1] + "-" + elem[2] + "</td><td>" + elem[0] + "</td></tr>"
        else:
            n = 400
            line = "<tr><td></td><td>Занятий нет</td></tr>"
        html = f"""
                    <table class="tftable" border="1">
                    <tr><th>Время</th><th>{m_day[i]}</th></tr>
                    {line}
                    </table>
                    """
        i += 1
        hti.screenshot(html_str=html, css_str=css, save_as='red_page.png', size=(2000, 200 + n))
