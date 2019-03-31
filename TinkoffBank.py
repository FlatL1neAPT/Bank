from Bank.Bank import Bank
import json
import requests
import time

from datetime import datetime
from datetime import timedelta


class TinkoffBank(Bank):

    def __init__(self, rec):
        super().__init__(rec)

        self.headers = {'Authorization': """Partner-Basic api-key="0a81e744-c20e-4105-9359-1d8eeebd8c07", api-secret="0OOUQ1BCWOF4X2AJ", agent-id="c9262715-5f2e-4d0f-a114-179add09bd59" """}

        url = "https://origination.tinkoff.ru/api/v1/partner/createApplication"

        data = {"Hello": "World"}
        r = requests.post(url, json=data, headers=self.headers)
        print(r.text)

    def is_allow_uncorrect_address(self):
        return True

    def is_in_odp(self, inn):
        from datetime import datetime

        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + str(inn))

        request = {"fields": {"inn": inn},
                   "inn_checked_status": 4,
                   "errors": {"inn": False}}

        url = "https://ats.tinkoff.ru/uif/partner/f8f513aefb7f3feb47e219995f7d3711/check_inn/"

        res = requests.post(url, json=request)
        response = json.loads(res.text)

        if response['result'] == "Duble":
            return True
        else:
            return False

    def get_score_id(self, inn):

        url = "https://origination.tinkoff.ru/api/v1/public/partner/innScoring"

        r = requests.post(url, json={"inn": inn}, headers=self.headers)
        res = json.loads(r.text)

        return res["result"]["scoreId"]


    def get_odp_status(self, score_id):

        is_ready = False

        while not is_ready:
            url = "https://origination.tinkoff.ru/api/v1/public/partner/innScoring/{}".format(score_id)

            r = requests.get(url, headers=self.headers)
            res = json.loads(r.text)

            is_ready = res['result']['isReady']

            if is_ready:
                return res['result']['result']

    def is_in_odp_full(self, inn, phone, acc_data):

        #acc_data = super().get_acc_data(7)

        #auth_data = json.loads(acc_data["data"])
        auth_data = acc_data["data"]

        print(auth_data["Название"])

        headers = {'Authorization': """Partner-Basic api-key="{}", api-secret="{}", agent-id="{}" """.
            format(auth_data["api-key"], auth_data["api-secret"], auth_data["agent-id"])}

        url = "https://origination.tinkoff.ru/api/v1/public/partner/scoring"
        data = {"inn": inn}

        proxies = {'https': auth_data["Proxy"]}

        try:
            r = requests.post(url, json=data, headers=headers, proxies=proxies)
        except Exception as e:
            raise Exception("\nПрокси: " + auth_data["Proxy"] + "\n" + str(e))

        res = {}

        #super().set_using_acc_data(acc_data)

        try:
            res = json.loads(r.text)
        except Exception as e:
            print(e)
            print(r.text)
            return None

        if "result" not in res:
            return True

        if res["result"] != "OK":
            return True

        url = "https://origination.tinkoff.ru/api/v1/public/partner/checkPhone"
        data = {"phoneNumber": phone}

        r = requests.post(url, json=data, headers=self.headers)
        res = json.loads(r.text)

        if "result" not in res:
            return True

        if "permissions" not in res["result"]:
            return True

        if res["result"]["permissions"] != "ANY":
            return True

        return False

    def get_org_list_old(self, start_date, end_date):

        start_date = start_date[6:] + "-" + start_date[3:5] + "-" + start_date[:2]
        end_date = end_date[6:] + "-" + end_date[3:5] + "-" + end_date[:2]

        url = "https://business-partner.tinkoff.ru/api/v1/partners/5-CVA0CUJK/applications/search"

        data = {"limit":100,"orderBy":"createdOn","orderDir":"desc","search":"","statuses":[],"agentSsoIds":[],"salesMethods":[],"createdBy":[],"strategies":[],"temperatures":[],"from":start_date,"till":end_date,"offset":0}

        r = requests.post(url, json=data, headers={'sessionID': '_ByDIYyRoULEDClcj7E-FwZFlXYL-qUYuVSJjUJ_Yb27GXOe0MlrHmoFdzMaGqi7adPfv-kTJpnbJ4PMakpRAg'})

        res = json.loads(r.text)

        return res['result']

    def get_org_list(self, start_date, end_date):

        start_date = datetime.strptime(start_date, "%d.%m.%Y")
        start_date = start_date - timedelta(days=1)
        start_date = start_date.strftime("%Y-%m-%d") + "T21:00:00Z"

        end_date = datetime.strptime(end_date, "%d.%m.%Y")
        end_date = end_date - timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d") + "T21:00:00Z"

        url = "https://origination.tinkoff.ru/api/v1/public/partner/applications?from={}&till={}".format(start_date, end_date)

        r = requests.get(url, headers=self.headers)

        res = json.loads(r.text)

        return res['result']

    def get_fio_by_contact(self, org, cur):

        cur.execute("""SELECT ContactPerson.* FROM Call_Bank 
                       INNER JOIN Call_ ON Call_.ID = Call_Bank.Call_
                       INNER JOIN ContactPerson ON Call_.ContactPerson = ContactPerson.ID 
                       WHERE Call_Bank.ExtID = '{}'""".format(org["id"]))

        res = cur.fetchall()

        if len(res) == 0:
            return org['id']

        org = res[0]

        return org["Surname"] + " " + org["Name"] + " " + org["MiddleName"]

    def get_results_ids(self):
        return [20000010368, 20000010367, 20000023505]

    def get_scenario_id(self):
        return [20000000783, 20000001779]

    def is_multithread_odp(self):
        return True

    def odp_delay(self):
        time.sleep(5)