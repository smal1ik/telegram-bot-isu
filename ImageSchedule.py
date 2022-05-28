from html2image import Html2Image

def scheduleImage(schedule, day):
    m_day = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    hti = Html2Image()
    line = ""
    for elem in schedule:
        line +=  "<tr><td>" + elem[1] + "-" + elem[2] + "</td><td>" + elem[0] + "</td></tr>"
    html = f"""
    <table class="tftable" border="1">
    <tr><th>Время</th><th>{m_day[day]}</th></tr>
    {line}
    </table>
    """
    css = """table {
    font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
    font-size: 140px;
    border-radius: 100px;
    border-spacing: 0;
    text-align: center;
    }
    th {
    background: #BCEBDD;
    color: white;
    text-shadow: 0 10px 10px #2D2020;
    padding: 100px 200px;
    }
    th, td {
    border-style: solid;
    border-width: 0 10px 10px 0;
    border-color: white;
    }
    th:first-child, td:first-child {
    text-align: left;
    }
    th:first-child {
    border-top-left-radius: 100px;
    }
    th:last-child {
    border-top-right-radius: 100px;
    border-right: none;
    }
    td {
    padding: 100px 200px;
    background: #F8E391;
    }
    tr:last-child td:first-child {
    border-radius: 0 0 0 100px;
    }
    tr:last-child td:last-child {
    border-radius: 0 0 100px 0;
    }
    tr td:last-child {
    border-right: none;
    }"""


    hti.screenshot(html_str=html, css_str=css, save_as='red_page.png',size=(2500+(20*20), 5000))