from Bank.Bank import Bank
from DataBase.Region import Region
import requests
import json
import time
import random
import string


class SberBank(Bank):

    def __init__(self, rec):
        self.SID = {"id": None, "time": None}
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

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/order/new?merchant_id=39&product_" \
              "type=2&product_profile_id=53&vat_number=" + inn

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")
            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
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
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_city?merchant_id=39&" \
              "merchant_branch_region_id={}&profile_id=56&is_active=1".format(int(region.get_number()) + 1)

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 401:
            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
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

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        office = response['entries'][0]

        return region, city["id"], office["id"]

    def send_org(self, org, log):

        region = None
        city = None
        office = None

        try:
            region, city, office = self._auto_detect_office(org, log)
            region = int(region.get_number()) + 1
        except Exception as exc:
            log.write("Ошибка при автоопределении офиса " + str(exc))

        if org["Комментарий"] is not None:
            if org["Комментарий"].find("#ОфисБанка:") != -1:
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
                            headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                     "UserTime": self.SID['time'], "Source": "ui",
                                     "Content-Type": "multipart/form-data; boundary=" + boundary})

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

            res = requests.post(url, data=body.encode(),
                                headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui",
                                         "Content-Type": "multipart/form-data; boundary=" + boundary})

        log.write("Результат" + str(res))
        log.write(res.text)

    def get_work_region_list(self):

        region_list = self.region_list()

        res = []

        for region in region_list:
            res.append( {'ID': int(region.get_number()) + 1, 'name': region.get_name()})

        return res

    def get_work_region_city_list(self, region):
        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_city?merchant_id=39&" \
              "merchant_branch_region_id={}&profile_id=56&is_active=1".format(int(region))

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                             "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        city_list = response['entries']

        res = []

        for city in city_list:
            res.append({'ID': city["id"], 'name': city["name"]})

        return res

    def get_work_region_city_office_list(self, region, city):

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_address?merchant_id=39&" \
              "merchant_branch_city_id={}&profile_id=56&is_active=1".format(city)

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        if res.status_code == 401:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

            res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                             "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        office_list = response['entries']

        res = []

        for office in office_list:
            res.append({'ID': office["id"], 'name': office["name"]})

        return res