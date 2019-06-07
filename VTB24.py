from Bank.Bank import Bank
from datetime import datetime
import hashlib
import json
import requests
from urllib.parse import quote

class VTB24(Bank):

    def __init__(self, rec):
        super().__init__(rec)
        self.key1 = "f3a7336f0c656573ec6232cdf6b4e9dc4f251ffdbea4a219b93779adc75f38cd"
        self.key2 = "3e368852e335c25e78a202891de4b1133b3ce67dbf20d903a091ff6ef34d91d5"

        self.Token = None

        ad = self.auth_data()

        if ad is not None:
            self.Token = ad

    def auth(self):
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S Europe/Moscow')
        hash = hashlib.sha256((self.key2 + hashlib.sha256((self.key1 + date).encode()).hexdigest()).encode()).hexdigest()
        Token = "#" + self.key1 + "#" + hash

        url = "https://mb-partner.bm.ru/auth/ident"

        res = requests.post(url, headers={'Token': Token, "Date": date}, verify=False)

        response = json.loads(res.text)

        self.save_auth_data(response["access_token"]["token"])
        return response["access_token"]["token"]

    def is_allow_uncorrect_address(self):
        return True

    def is_in_odp(self, inn):

        def impl():
            if self.Token is None:
                self.Token = self.auth()

            url = "https://mb-partner.bm.ru//anketa/anketa_exists_inn?inn=" + inn

            res = requests.get(url, headers={'Token': self.Token}, verify=False)

            if res.status_code != 200:
                raise Exception("Возврат не 200")

            response = json.loads(res.text)

            if response["status_code"] == '13':
                return False

            return True

        try:
            return impl()
        except:
            self.Token = None
            return impl()

    def send_org(self, org, log):

        if self.is_in_odp(org["ИНН"]):
            log.write("На момент отправки клиент в ОДП")
            return "На момент отправки клиент в ОДП"

        region = None
        city = None
        office = None

        if org["Комментарий"] is None or org["Комментарий"].find("#ОфисБанка:") == -1:
            log.write("Нет информации об отделении банка")
            return "Нет информации об отделении банка"

        address = org["Комментарий"]
        start_pos = address.find("#ОфисБанка:")
        address = org["Комментарий"][start_pos + 1:]
        end_pos = address.find("#")

        address = address[:end_pos]

        fields = address.split(":")

        region = fields[2]
        city = fields[3]
        office = fields[4]

        if region is None or city is None or office is None:
            raise Exception("Не удалось определить офис банка")

        if self.Token is None:
            self.Token = self.auth()

        url = "https://mb-partner.bm.ru/anketa/add"

        res = requests.post(url, headers={'Token': self.Token}, verify=False)
        add_response = json.loads(res.text)

        body = {
            "inn": org["ИНН"],
            "org_name": org["Название"],
            "contact_phone": org["Телефон"],
            "fio": org["Фамилия"] + ' ' + org["Имя"] + ' ' + org["Отчество"],
            "region": region,
            "city": city,
            "branch": int(office),
            "agreement": "1",
            "add_info": "Профит Сейл"
        }

        url = "https://mb-partner.bm.ru/anketa/" + add_response["id_anketa"] + "/edit"

        log.write("Запрос\n")
        log.write(str(body))

        res = requests.post(url, data="anketaid=" + add_response["id_anketa"] + "&anketadata=" + quote(json.dumps(body)),
                            headers={'Token': self.Token, 'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)

        url = "https://mb-partner.bm.ru/anketa/" + add_response["id_anketa"] + "/apply"

        res = requests.post(url, data="id=" + add_response["id_anketa"],
                            headers={'Token': self.Token, 'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)

        log.write("Результат" + str(res))
        log.write(res.text)

    def get_work_region_list(self):

        def impl():
            if self.Token is None:
                self.Token = self.auth()

            url = "https://mb-partner.bm.ru/misc/regions"

            res = requests.get(url, headers={'Token': self.Token}, verify=False)
            response = json.loads(res.text)

            res = []

            for region in response["region_list"]:
                res.append({'ID': region['value'], 'name': region['name']})

            return res

        try:
            return impl()
        except:
            self.Token = None
            return impl()

    def get_work_region_city_list(self, region):
        if self.Token is None:
            self.Token = self.auth()

        url = "https://mb-partner.bm.ru/misc/cities?region_code=" + region

        res = requests.get(url, headers={'Token': self.Token}, verify=False)
        response = json.loads(res.text)

        res = []

        for city in response["city_list"]:
            res.append({'ID': city['id']['value'], 'name': city['name']['value']})

        return res

    def get_work_region_city_office_list(self, region, city):

        if region == '50' or region == '77':
            return [{"ID": '4327', "name": 'м. Кузнецкий мост, ул. Пушечная, д.5'}]

        if self.Token is None:
            self.Token = self.auth()

        url = "https://mb-partner.bm.ru//misc/branch/" + region + "?city_id=" + city

        res = requests.get(url, headers={'Token': self.Token}, verify=False)
        response = json.loads(res.text)

        res = []

        for branch in response["branch_list"]["list"]:

            if branch['name']['value'] == 'Колл-центр':
                continue

            res.append({'ID': branch['id']['value'], 'name': branch['name']['value']})

        return res

    def is_in_odp_full(self, inn, phone, acc_data):

        return self.is_in_odp(inn)

    def get_org_list(self, from_date, to_date):

        if self.Token is None:
            self.Token = self.auth()

        is_complete = False

        result = []
        offset = 0
        limit = 200

        while not is_complete:
            url = "https://mb-partner.bm.ru/anketa?date_from={}&date_to={}&limit={}&start={}".format(from_date, to_date, limit, offset)

            r = requests.get(url, headers={'Token': self.Token}, verify=False)
            #print(r.text)
            res = json.loads(r.text)

            result += res["anketa_list"]['list']

            if len(res["anketa_list"]['list']) < limit:
                is_complete = True
            else:
                offset += limit


        return result

    def get_fio_by_contact(self, org, cur):
        return org['fields']['fio']['value']

    def get_results_ids(self):
        return [20000018436]

    def get_scenario_id(self):
        return [20000001410]

    def is_multithread_odp(self):
        return False

    def odp_delay(self):
        pass


if __name__ == "__main__":
    from DataBase.DBController import DBController
    controller = DBController()
    cur = controller.get_cursor()

    cur.execute("""SELECT * From Bank WHERE Name = %s;""", ("ВТБ24",))

    bank_list = cur.fetchall()

    bank_rec = bank_list[0]

    bank = VTB24(bank_rec)
    bank.is_in_odp("310262282808")