from DataBase.DBController import DBController
from DataBase.Region import Region
import json

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

    def __init__(self, rec):
        self.rec = rec
        self.controller = DBController()
        self.cur = self.controller.get_cursor()

        self.cur.execute("""SELECT Region.* 
                            FROM Region 
                            INNER JOIN Bank_Region ON Bank_Region.Region = Region.ID
                            WHERE Bank_Region.Bank = %s;""", (self.rec["ID"],))

        region_list = self.cur.fetchall()
        self.regions = []

        for region_rec in region_list:
            self.regions.append(Region(region_rec))

    def get_acc_data(self):

        acc_list = []

        while(len(acc_list) == 0):
            self.cur.execute("""SELECT * FROM BankAccount WHERE TIMESTAMPDIFF( SECOND, LastUsing, NOW()) > 10;""")
            acc_list = self.cur.fetchall()

        return acc_list[0]

    def set_using_acc_data(self, acc_data):

        self.cur.execute("""UPDATE BankAccount SET LastUsing = NOW() WHERE ID = """ + str(acc_data["ID"]) )
        self.controller.save_changes()

    def apeend_organization(self, org_id):

        self.cur.execute("""INSERT INTO Organization_Bank_CallCenter (Organization, Bank, CallCenter) 
                            VALUES (%s,%s, 1)""",
                         (org_id, self.rec["ID"]))

        self.controller.save_changes()

    def name(self):
        return self.rec["Name"]

    def id(self):
        return self.rec["ID"]

    def auth_data(self):
        return self.rec["AuthData"]

    def main_acc_data(self):
        return json.loads(self.rec["AuthData"])

    def acc_list(self):
        self.cur.execute("SELECT Data FROM BankAccount WHERE Bank = %s;", (self.rec["ID"],))
        acc_list = self.cur.fetchall()

        return [json.loads(row["Data"]) for row in acc_list]

    def save_auth_data(self, data):
        self.cur.execute("UPDATE Bank SET AuthData = %s WHERE ID = %s;", (data, self.rec["ID"]))
        self.controller.save_changes()

    def region_list(self):
        return self.regions

    def is_region_allow(self, address):

        if not Region.is_adress_correct(address):
            if self.is_allow_uncorrect_address():
                return True
            else:
                return False

        for region in self.regions:
            if region.address_in_region(address):
                return True

        return False


if __name__ == "__main__":
    Bank.create("ВТБ24")
