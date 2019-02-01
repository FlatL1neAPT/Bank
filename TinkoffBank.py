from Bank.Bank import Bank
import json
import requests


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

    def is_in_odp_full(self, inn, phone):

        acc_data = super().get_acc_data(7)

        auth_data = json.loads(acc_data["Data"])

        print(auth_data["Название"])

        headers = {'Authorization': """Partner-Basic api-key="{}", api-secret="{}", agent-id="{}" """.
            format(auth_data["api-key"], auth_data["api-secret"], auth_data["agent-id"])}

        url = "https://origination.tinkoff.ru/api/v1/public/partner/scoring"
        data = {"inn": inn}

        r = requests.post(url, json=data, headers=headers)
        res = {}

        super().set_using_acc_data(acc_data)

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
