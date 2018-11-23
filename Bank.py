from DataBase.DBController import DBController


class Bank:

    @staticmethod
    def create(name):
        controller = DBController()
        cur = controller.get_cursor()

        cur.execute("SELECT * FROM Region;")
        regions = cur.fetchall()

        cur.execute("INSERT INTO Bank (Name) VALUES(%s);", (name,))
        bank_id = cur.lastrowid

        for region in regions:
            cur.execute("INSERT INTO Bank_Region (Bank, Region) VALUES(%s,%s);", (bank_id, region["ID"]))

        controller.save_changes()

    def __init__(self, db_key):
        pass

if __name__ == "__main__":
    Bank.create("Тинькофф")
    Bank.create("Сбербанк")
