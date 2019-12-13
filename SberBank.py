from Bank.Bank import Bank
from DataBase.Region import Region
import requests
import json
import time
import random
import string
from datetime import datetime
from datetime import timedelta


class SberBank(Bank):

    def __init__(self, rec):
        self.SID = {"id": None, "time": None}
        self.merchant_id = 39
        self.headers = {"Authorization": "Token token={}".format("d98e25d8e89b44eb89804fa8ddafcadb")}
        super().__init__(rec)

        ad = self.auth_data()

        if ad is not None:
            self.SID = json.loads(ad)

    def _login(self, username, password):


        request = {"data": {
            "username": username,
            "password": password
        }}
        url = "https://ppapi.dasreda.ru/api/v1/login"

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://partners.dasreda.ru',
            'UseraAgent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/65.0.3325.181 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://partners.dasreda.ru/auth',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        res = requests.post(url, json=request, headers=headers)

        response = json.loads(res.text)

        if "eo_token" in response:
            guid = response["eo_token"]

            ts = int(time.time() * 1000)
            cts = ts % 0x2710

            res = ""
            for i in range(0, len(guid)):
                res += guid[cts % (i + 0x1)]

            self.save_auth_data(json.dumps({"id": res, "time": str(ts)}))
            return res, str(ts)

        return "", ""

    def is_allow_uncorrect_address(self):
        return False

    def is_in_odp(self, inn):

        url = "https://ppapi.dasreda.ru/api/v1/sber_mq/order"

        data = {
            "inn": inn,
            "product_ids": [1]
        }

        res = requests.post(url, headers=self.headers, json={"data": data})
        print(res)

        res = json.loads(res.text)

        for error in res["errors"]:
            if "blocked_by_other" in error and error["blocked_by_other"] == "blocked":
                return True

        return False

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

        url = "https://ppapi.dasreda.ru/api/v1/order/new?merchant_id=39&product_" \
              "type=2&product_profile_id=53&vat_number=" + inn

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 422:
            return True

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")
            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                             "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        if "errors" in response:
            if 'blocked' in response["errors"]["blocked_by_other"]:
                return True

        return False

    def _auto_detect_office(self, org, log):

        log.write("Автоопределение офиса\n")

        region = Region.find_region_by_address(org["Адрес"])

        if region is None:
            err = "По адресу {} не найден регион".format(org["Адрес"])
            log.write(err)
            raise Exception(err)

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_city?merchant_id=39&" \
              "merchant_branch_region_id={}&profile_id=56&is_active=1".format(int(region.get_number()) + 1)

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 401:
            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                             "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        if res.status_code == 401:
            if response["errors"][0]["_error"] == "authorization_required":
                pass

        city_list = response['entries']
        our_city = None

        for city in city_list:
            if org["Адрес"].upper().find(city['name'].upper()) != -1:
                our_city = city
                break

        if our_city is None:
            err = "По адресу {} в регионе {} не найден город среди {}".format(org["Адрес"], region.get_name(),
                                                                              str(city_list))
            log.write(err)
            raise Exception(err)

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_address?merchant_id=39&" \
              "merchant_branch_city_id={}&profile_id=56&is_active=1".format(city["id"])

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        office = response['entries'][0]

        return region, city["id"], office["id"]

    def send_org(self, org, log, project_params=None):

        if self.is_in_odp(org["ИНН"]):
            log.write("На момент отправки клиент в ОДП")
            return "СБ: На момент отправки клиент в ОДП"

        region = None
        city = None
        office = None
        comment = org["Комментарий"]

        try:
            test = self.decode(comment)
        except:
            pass

        #try:
        #    region, city, office = self._auto_detect_office(org, log)
        #    region = int(region.get_number()) + 1
        #except Exception as exc:
        #    log.write("Ошибка при автоопределении офиса " + str(exc))

        if comment is not None:
            if comment.find("#ОфисБанка:") != -1:
                address = comment
                start_pos = address.find("#ОфисБанка:")
                address = comment[start_pos + 1:]
                end_pos = address.find("#")

                address = address[:end_pos]

                fields = address.split(":")

                region = fields[2]
                city = fields[3]
                office = fields[4]
                comment = comment[:start_pos] + comment[end_pos + 2:]

        data = {
            "inn": org["ИНН"],
            "merchant_id": self.merchant_id,
            "product_ids": [1],
            "company_name": org["Название"],
            "last_name": org["Фамилия"],
            "first_name": org["Имя"],
            "middle_name": org["Отчество"],
            "email": "",
            "phone": org["Телефон"],
            "add_info": comment,
            "region_id": region,
            "city_id": city,
            "merchant_branch_id": office
        }

        url = "https://ppapi.dasreda.ru/api/v1/sber_mq/order"

        res = requests.post(url, headers=self.headers, json={"data": data})

        log.write("Результат\n" + res.text)

        return

        if region is None or city is None or office is None:
            raise Exception("Не удалось определить офис банка")

        url = "https://ppapi.dasreda.ru/api/v1/order"

        boundary = "----WebKitFormBoundary" + \
                   ''.join(random.choices(string.ascii_uppercase + string.digits, k=16)).lower()

        body = "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][merchant_branch_id]"\r\n\r\n{}\r\n""".\
            format(office)

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][merchant_branch_city_id]"\r\n\r\n{}\r\n""".\
            format(city)

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][vat_number]"\r\n\r\n{}\r\n""".format(org["ИНН"])

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][company_name]"\r\n\r\n{}\r\n""".format(org["Название"])

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][last_name]"\r\n\r\n{}\r\n""".format(org["Фамилия"])

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][first_name]"\r\n\r\n{}\r\n""".format(org["Имя"])

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][middle_name]"\r\n\r\n{}\r\n""".format(org["Отчество"])

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][email]"\r\n\r\n\r\n"""

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][mobile_phone]"\r\n\r\n{}\r\n""".format(org["Телефон"])

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][add_info]"\r\n\r\n\r\n"""

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][merchant_branch_region_id]"\r\n\r\n{}\r\n""".\
            format(region)

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][product_profile_id]"\r\n\r\n56\r\n"""

        body += "--" + boundary + "\r\n"
        body += """Content-Disposition: form-data; name="[data][merchant_id]"\r\n\r\n39\r\n"""

        body += "--" + boundary + "--\r\n"
        res = requests.post(url, data=body.encode(),
                            headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                     "UserTime": self.SID['time'], "Source": "ui",
                                     "Content-Type": "multipart/form-data; boundary=" + boundary})

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

            res = requests.post(url, data=body.encode(),
                                headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                         "UserTime": self.SID['time'], "Source": "ui",
                                         "Content-Type": "multipart/form-data; boundary=" + boundary})

        log.write("Результат" + str(res))
        log.write(res.text)

    def get_work_region_list(self):

        #url = "https://ppapi.dev.dasreda.ru/api/v1/sber_mq/region?with_merchant_branches={}".format(self.merchant_id)
        url = "https://ppapi.dasreda.ru/api/v1/sber_mq/region?page={}&with_merchant_branches=1"
        page = 1
        res = []

        while page != -1:
            region_list_row = requests.get(url.format(page), headers={"Authorization": "Token token={}".format("c69d620363833f3a586f4beeb7b9df45")})
            region_list = json.loads(region_list_row.text)

            for region in region_list['entries']:
                res.append({'ID': region['id'], 'name': region['name']})

            if len(res) >= region_list['total_entries']:
                page = -1
            else:
                page += 1

        return res

    def old_get_work_region_list(self):

        #url = "https://ppapi.dev.dasreda.ru/api/v1/sber_mq/region?with_merchant_branches={}".format(self.merchant_id)
        url = "https://ppapi.dev.dasreda.ru/api/v1/sber_mq/region?page={}&with_merchant_branches=1"
        page = 1
        res = []

        while page != -1:
            region_list_row = requests.get(url.format(page), headers=self.headers)
            region_list = json.loads(region_list_row.text)

            for region in region_list['entries']:
                res.append({'ID': region['id'], 'name': region['name']})

            if len(res) >= region_list['total_entries']:
                page = -1
            else:
                page += 1

        return res

    def _old_get_work_region_list(self):

        region_list = self.region_list()

        res = []

        for region in region_list:
            res.append( {'ID': int(region.get_number()) + 1, 'name': region.get_name()})

        return res

    def get_work_region_city_list(self, region):

        url = "https://ppapi.dasreda.ru/api/v1/sber_mq/city?region_id={}&with_merchant_branches=1&page=".format(region)
        url += "{}"

        page = 1
        res = []

        while page != -1:
            city_list_row = requests.get(url.format(page), headers=self.headers)
            city_list = json.loads(city_list_row.text)

            for city in city_list['entries']:
                res.append({'ID': city['id'], 'name': city['name']})

            if len(res) >= city_list['total_entries']:
                page = -1
            else:
                page += 1

        return res

    def old_get_work_region_city_list(self, region):

        url = "https://ppapi.dev.dasreda.ru/api/v1/sber_mq/city?region_id={}&with_merchant_branches=1&page=".format(region)
        url += "{}"

        page = 1
        res = []

        while page != -1:
            city_list_row = requests.get(url.format(page), headers=self.headers)
            city_list = json.loads(city_list_row.text)

            for city in city_list['entries']:
                res.append({'ID': city['id'], 'name': city['name']})

            if len(res) >= city_list['total_entries']:
                page = -1
            else:
                page += 1

        return res

    def _old_get_work_region_city_list(self, region):

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_city?merchant_id=39&" \
              "merchant_branch_region_id={}&profile_id=56&is_active=1".format(int(region))

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                             "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        city_list = response['entries']

        res = []

        for city in city_list:
            res.append({'ID': city["id"], 'name': city["name"]})

        return res

    def get_work_region_city_office_list(self, region, city):

        url = "https://ppapi.dasreda.ru/api/v1/sber_mq/merchant_branch?city_id={}&region_id={}&with_merchant_branches=1".format(city, region)

        office_list_row = requests.get(url, headers=self.headers)

        office_list = json.loads(office_list_row.text)
        res = []

        for office in office_list['entries']:
            res.append({'ID': office["id"], 'name': office["name"] + " " + office["address"]})

        return res

    def old_get_work_region_city_office_list(self, region, city):

        url = "https://ppapi.dev.dasreda.ru/api/v1/sber_mq/merchant_branch?city_id={}&region_id={}&with_merchant_branches=1".format(city, region)

        office_list_row = requests.get(url, headers=self.headers)

        office_list = json.loads(office_list_row.text)
        res = []

        for office in office_list['entries']:
            res.append({'ID': office["id"], 'name': office["name"] + " " + office["address"]})

        return res

    def _old_get_work_region_city_office_list(self, region, city):

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_address?merchant_id=39&" \
              "merchant_branch_city_id={}&profile_id=56&is_active=1".format(city)

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                             "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        office_list = response['entries']

        res = []

        for office in office_list:
            res.append({'ID': office["id"], 'name': office["name"]})

        return res

    def is_in_odp_full(self, inn, phone, acc_data):

        return self.is_in_odp(inn)

    def get_org_list(self, start_date, end_date):

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")

        start_date = start_date[6:] + "-" + start_date[3:5] + "-" + start_date[:2]

        end_date = datetime.strptime(end_date, "%d.%m.%Y")
        end_date = end_date - timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")

        result = []

        is_complete = False
        offset = 1
        limit = 30

        while not is_complete:
            url = "https://ppapi.dasreda.ru/api/v1/order?per_page={}&page={}&for_filters=1&merchant_id=39&from={}&to={}".\
                format(limit, offset, start_date, end_date)

            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                             "UserTime": self.SID['time'], "Source": "ui"})

            if res.status_code == 401:
                self.SID['id'], self.SID['time'] = self._login("uliakravcenko523@gmail.com", "fJt4b2Knayc")
                res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "12092",
                                                 "UserTime": self.SID['time'], "Source": "ui"})

            response = json.loads(res.text)
            result += response['entries']

            if len(response['entries']) < limit:
                is_complete = True
            else:
                offset += 1

        return result

    def get_fio_by_contact(self, org, cur):
        return org['contact_details'][0]['value'] + ' ' + org['contact_details'][1]['value'] + ' ' + org['contact_details'][2]['value']

    def get_results_ids(self):
        return [20000014499]

    def get_scenario_id(self):
        return [20000001128]

    def is_multithread_odp(self):
        return False

    def odp_delay(self):
        pass

    def decode(self, comment):
        fields = comment.split(":")

        r = fields[0]
        c = fields[1]
        o = fields[2]

        res = ""

        region_list = self._old_get_work_region_list()

        for region in region_list:
            if region["ID"] == int(r):
                res += region["name"] + "\n"
                break

        city_list = self._old_get_work_region_city_list(r)

        for city in city_list:
            if city["ID"] == int(c):
                res += city["name"] + "\n"
                break

        office_list = self._old_get_work_region_city_office_list(r, c)

        for office in office_list:
            if office["ID"] == int(o):
                res += office["name"]
                break

        return res

    def get_product_info(self):
        url = "https://ppapi.dasreda.ru/api/v1/sber_mq/product?merchant_id={}".format(self.merchant_id)

        product_list_row = requests.get(url, headers=self.headers)

        product_list = json.loads(product_list_row.text)

        pass

if __name__ == "__main__":
    from DataBase.DBController import DBController
    controller = DBController()
    cur = controller.get_cursor()

    cur.execute("""SELECT * From Bank WHERE Name = %s;""", ("Сбербанк",))

    bank_list = cur.fetchall()

    bank_rec = bank_list[0]

    bank = SberBank(bank_rec)

    test = bank.decode("33:2361773:2582")

    pass
