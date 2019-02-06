from Bank.Bank import Bank
import json
import requests
import smtplib

from email.mime.text import MIMEText
from email.header import Header

class MTS(Bank):

    def __init__(self, rec):
        super().__init__(rec)

    def is_allow_uncorrect_address(self):
        return True

    def is_in_odp(self, inn):
        return False

    def is_in_odp_full(self, inn, phone):

        return False

    def get_work_region_list(self):

        return [{"ID": "876", "name": "Амурская область"},
                {"ID": "585", "name": "Волгоградская область"},
                {"ID": "877", "name": "Еврейская автономная область"},
                {"ID": "878", "name": "Забайкальский край"},
                {"ID": "879", "name": "Иркутская область"},
                {"ID": "590", "name": "Калининградская область"},
                {"ID": "596", "name": "Краснодарский край"},
                {"ID": "602", "name": "Красноярский край"},
                {"ID": "604", "name": "Москва"},
                {"ID": "613", "name": "Нижегородская область"},
                {"ID": "615", "name": "Новосибирская область"},
                {"ID": "617", "name": "Омская область"},
                {"ID": "880", "name": "Приморский край"},
                {"ID": "623", "name": "Республика Башкортостан"},
                {"ID": "628", "name": "Республика Коми"},
                {"ID": "631", "name": "Республика Татарстан"},
                {"ID": "633", "name": "Ростовская область"},
                {"ID": "637", "name": "Самарская область"},
                {"ID": "639", "name": "Санкт-Петербург"},
                {"ID": "641", "name": "Саратовская область"},
                {"ID": "882", "name": "Сахалинская область"},
                {"ID": "644", "name": "Свердловская область"},
                {"ID": "648", "name": "Ставропольский край"},
                {"ID": "651", "name": "Томская область"},
                {"ID": "653", "name": "Тюменская область"},
                {"ID": "883", "name": "Хабаровский край"},
                {"ID": "660", "name": "Челябинская область"}]

    def get_work_region_city_list(self, region):

        data = { '648': [{'name': 'Ставрополь', 'ID': '650'}],
                 '585': [{'name': 'Волгоград', 'ID': '586'},
                         {'name': 'Волжский', 'ID': '587'}],
                 '883': [{'name': 'Хабаровск', 'ID': '884'},
                         {'name': 'Солнечный', 'ID': '1071'},
                         {'name': 'Чегдомын', 'ID': '1076'},
                         {'name': 'Бикин', 'ID': '1053'},
                         {'name': 'Вяземский', 'ID': '1056'},
                         {'name': 'Хор', 'ID': '1075'},
                         {'name': 'Переяславка', 'ID': '1068'},
                         {'name': 'СоветскаяГавань', 'ID': '1070'},
                         {'name': 'Комсомольск-на-Амуре', 'ID': '894'},
                         {'name': 'Амурск', 'ID': '1050'},
                         {'name': 'Де-Кастри', 'ID': '1057'},
                         {'name': 'Ванино', 'ID': '1055'},
                         {'name': 'Николаевск-на-Амуре', 'ID': '1066'}],
                 '623': [{'name': 'Нефтекамск', 'ID': '624'},
                         {'name': 'Уфа', 'ID': '627'},
                         {'name': 'Октябрьский', 'ID': '858'},
                         {'name': 'Стерлитамак', 'ID': '625'},
                         {'name': 'Туймазы', 'ID': '626'}],
                 '604': [{'name': 'Москва', 'ID': '605'}],
                 '639': [{'name': 'Санкт-Петербург', 'ID': '640'}],
                 '879': [{'name': 'Иркутск', 'ID': '1060'},
                         {'name': 'Ангарск', 'ID': '1051'}],
                 '631': [{'name': 'Казань', 'ID': '632'}],
                 '590': [{'name': 'Калининград', 'ID': '591'}],
                 '596': [{'name': 'Краснодар', 'ID': '599'},
                         {'name': 'Армавир', 'ID': '597'},
                         {'name': 'Новороссийск', 'ID': '600'},
                         {'name': 'Сочи', 'ID': '601'}],
                 '602': [{'name': 'Красноярск', 'ID': '603'}],
                 '613': [{'name': 'НижнийНовгород', 'ID': '614'}],
                 '617': [{'name': 'Омск', 'ID': '618'}],
                 '628': [{'name': 'Ухта', 'ID': '630'},
                         {'name': 'Сыктывкар', 'ID': '629'}],
                 '876': [{'name': 'Соловьевск', 'ID': '1072'},
                         {'name': 'Благовещенск', 'ID': '1049'},
                         {'name': 'Тында', 'ID': '1073'}],
                 '880': [{'name': 'Уссурийск', 'ID': '1074'},
                         {'name': 'Владивосток', 'ID': '1046'}],
                 '882': [{'name': 'Южно-Сахалинск', 'ID': '1079'}],
                 '877': [{'name': 'Биробиджан', 'ID': '1054'}],
                 '878': [{'name': 'Чита', 'ID': '1077'}],
                 '615': [{'name': 'Новосибирск', 'ID': '616'}],
                 '633': [{'name': 'Ростов-на-Дону', 'ID': '634'}],
                 '637': [{'name': 'Самара', 'ID': '638'}],
                 '641': [{'name': 'Саратов', 'ID': '642'}],
                 '651': [{'name': 'Томск', 'ID': '652'}],
                 '653': [{'name': 'Тюмень', 'ID': '654'}],
                 '644': [{'name': 'Екатеринбург', 'ID': '645'}],
                 '660': [{'name': 'Челябинск', 'ID': '661'}]}

        return data[region]

    def get_work_region_city_office_list(self, region, city):
        url = "https://www.mtsbank.ru/ajax/lightbox/affiliates.php?settlement_id={}&view_ul=1".format(city)
        res = requests.get(url)
        response = json.loads(res.text)

        res = []

        for branch in response["data"]:
            res.append({'ID': branch["value"], 'name': branch["display"]})

        return res

    def send_org(self, org, log):

        region = None
        city = None
        office = None

        if org["Комментарий"] is None or org["Комментарий"].find("#ОфисБанка:") == -1:
            log.write("Нет информации об отделении банка")
            raise Exception("Нет информации об отделении банка")

        address = org["Комментарий"]
        start_pos = address.find("#ОфисБанка:")
        address = org["Комментарий"][start_pos + 1:]
        end_pos = address.find("#")

        address = address[:end_pos]
        comment = org["Комментарий"]
        comment = comment.replace(address, "")

        fields = address.split(":")

        region = fields[2]
        city = fields[3]
        office = fields[4]
        email = fields[5]

        if region is None or city is None or office is None:
            raise Exception("Не удалось определить офис банка")

        org_type = "Общества с ограниченной ответственностью"
        if len(org["ИНН"]) == 12:
            org_type = "Индивидуальные предприниматели"

        text = """Мобильный телефон: {}\n"""\
               """Электронная почта: {}\n"""\
               """Регион: {}\n"""\
               """Населенный пункт: {}\n"""\
               """Филиал: {}\n"""\
               """Организационно прововая форма: {}\n"""\
               """ФИО: {}\n"""\
               """Название: {}\n"""\
               """ИНН: {}\n"""\
               """Комментарий: {}\n"""

        text = text.format(org["Телефон"], email, region, city, office, org_type,
                           org["Фамилия"] + ' ' + org["Имя"] + ' ' + org["Отчество"],
                           org["Название"], org["ИНН"], comment)

        url = "https://script.google.com/macros/s/AKfycbzcuzZkZ4cUmwsvKkgPOpm5p01UaSBd4nM-xaCYTaP35N8Qqmg/exec?subject={}&message={}".format("Профит сейл.Заявка {}".format(org["Номер"]), text)
        res = requests.post(url, json={"subject": "123111", "message": "231111"})

        i = 0

        #smtpObj = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        #smtpObj.starttls()
        #smtpObj.login('litrez007@yahoo.com', 'hj7Gsv4lOe')

        #msg = MIMEText(text, _charset="UTF-8")
        #msg["Subject"] = Header("Профит сейл.Заявка {}".format(org["Номер"])).encode()

        #smtpObj.sendmail("litrez007@yahoo.com", ["koromandeu@mail.ru", "Rgusejnov@mtsbank.ru"], msg.as_string())
        #smtpObj.sendmail("litrez007@yahoo.com", ["koromandeu@mail.ru", "koroman100@mail.ru"], msg.as_string())
        #smtpObj.quit()


if __name__ == "__main__":
    from DataBase.DBController import DBController

    controller = DBController()
    cur = controller.get_cursor()

    cur.execute("""SELECT * From Bank WHERE Name = %s;""", ("МТС",))

    bank_list = cur.fetchall()

    bank_rec = bank_list[0]

    bank = MTS(bank_rec)

    data_to_send = {
        "Имя": "Иван",
        "Отчество": "Иванович",
        "Фамилия": "Иванов",
        "Телефон": "+79056335029",
        "Название": "ИП КБ",
        "ИНН": "123123123123",
        "Адрес": "123",
        "Комментарий": "#ОфисБанка:МТС:Омская область:Омск:Омский операционный офис#",
        "Номер": "332"
    }

    bank.send_org(data_to_send, None)
