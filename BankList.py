from DataBase.DBController import DBController


class BankList:

    @staticmethod
    def get():
        controller = DBController()
        cur = controller.get_cursor()

        cur.execute("""SELECT * From Bank;""")

        bank_list = cur.fetchall()

        res = []

        for bank_rec in bank_list:
            module = __import__("Bank." + bank_rec["Module"])
            res.append(getattr(getattr(module, bank_rec["Module"]), bank_rec["Module"])(bank_rec))

        return res

    @staticmethod
    def get_by_name(name):
        controller = DBController()
        cur = controller.get_cursor()

        cur.execute("""SELECT * From Bank WHERE Name = %s;""", (name,))

        bank_list = cur.fetchall()

        if len(bank_list) == 0:
            return None

        bank_rec = bank_list[0]

        module = __import__("Bank." + bank_rec["Module"])
        return getattr(getattr(module, bank_rec["Module"]), bank_rec["Module"])(bank_rec)


if __name__ == "__main__":
    import sys

    sys.path.append("../")
    bank = BankList.get_by_name("МТС")

    res = bank.is_region_allow("171385,ТВЕРСКАЯ ОБЛАСТЬ,СТАРИЦКИЙ РАЙОН, ,БОЛЬШИЕ ЛЕДИНКИ ДЕРЕВНЯ, ,ДОМ 2А, ,КВАРТИРА 2", "505198256549")

