"""Seed data, part 1: countries, banks, customers, accounts, background transactions."""

from __future__ import annotations

import random
from datetime import date, timedelta

from .config import SEED
from .ibanutil import make_iban

HOME = "XM"

COUNTRIES = {
    "XM": "Meridia",
    "XA": "Aldoria",
    "XB": "Brevnia",
    "XQ": "Quenmark",
    "XR": "Rovaland",
    "XT": "Tessaly",
    "QN": "Norvania",
    "QP": "Kharnovia",
}
HIGH_RISK_COUNTRIES = ["QP"]

# bank_code, name, country, bic, city
BANKS = [
    ("MRTB", "Meridian Trust Bank", "XM", "MRTBXMM2", "Port Ilvane"),
    ("ALDB", "Aldoria Commerce Bank", "XA", "ALDBXAA1", "Velmora"),
    ("BRVN", "Brevnia Savings Union", "XB", "BRVNXBB1", "Corrowick"),
    ("QNMK", "Quenmark National Bank", "XQ", "QNMKXQQ1", "Hartsfell"),
    ("ROVA", "Rovaland Credit Bank", "XR", "ROVAXRR1", "Duskmere"),
    ("TESL", "Tessaly Mutual Bank", "XT", "TESLXTT1", "Ambrel"),
    ("NRVA", "Norvania First Bank", "QN", "NRVAQNN1", "Silverkeld"),
    ("KHRN", "Kharnovia Development Bank", "QP", "KHRNQPK1", "Gallowmere"),
]
BANK_BY_CODE = {b[0]: b for b in BANKS}


def d_ago(today: date, n: int) -> str:
    return (today - timedelta(days=n)).isoformat()


# id number, kind, name, dob (individual), nationality, home country, town, street, segment
INDIVIDUALS = [
    (1001, "Ilvane Marrowick", "1984-03-12", "XM", "14 Lantern Row", "Port Ilvane"),
    (1002, "Dorian Quillfeather", "1991-08-25", "XM", "3 Copper Kettle Lane", "Port Ilvane"),
    (1003, "Sabine Tarrowgate", "1979-12-02", "XM", "88 Heron Steps", "Marlow Reach"),
    (1004, "Emeric Lowenhall", "1986-05-19", "XM", "27 Pewter Court", "Port Ilvane"),
    (1005, "Wynne Castellane", "1990-07-21", "XM", "9 Orchard Gate", "Marlow Reach"),
    (1006, "Oskar Brindlemoor", "1978-11-03", "XM", "51 Foxglove Walk", "Tallowby"),
    (1007, "Valdis Orrenmoor", "1971-09-30", "XQ", "6 Cinder Quay", "Port Ilvane"),
    (1008, "Katrin Elsdottir-Vance", "1969-04-14", "XT", "112 Saltpan Road", "Tallowby"),
    (1009, "Anselm Drozdowich", "1980-01-09", "XR", "40 Rookery Close", "Marlow Reach"),
    (1010, "Perdita Vanhollow", "1975-06-27", "XQ", "2 Larkspur Terrace", "Port Ilvane"),
    (1011, "Tobias Wrenfield", "1982-10-08", "XM", "73 Millrace Street", "Tallowby"),
    (1012, "Marguerite Oakhaven", "1988-02-16", "XM", "19 Bellwether Close", "Marlow Reach"),
    (1013, "Cassius Dunmore", "1965-09-04", "XM", "5 Thistledown Mews", "Port Ilvane"),
    (1014, "Rosalind Heathcote-Brae", "1994-01-30", "XM", "61 Quillon Street", "Tallowby"),
    (1015, "Leopold Fenwick-Aral", "1958-07-11", "XM", "8 Kestrel Hill", "Marlow Reach"),
    (1016, "Isolde Pennywhistle", "1999-11-22", "XM", "35 Marigold Yard", "Port Ilvane"),
]

# where each individual was born, as town and country
PLACES_OF_BIRTH = {
    1001: "Port Ilvane, Meridia", 1002: "Marlow Reach, Meridia", 1003: "Tallowby, Meridia", 1004: "Port Ilvane, Meridia",
    1005: "Marlow Reach, Meridia", 1006: "Tallowby, Meridia", 1007: "Hartsfell, Quenmark", 1008: "Ambrel, Tessaly",
    1009: "Duskmere, Rovaland", 1010: "Brindlecombe, Quenmark", 1011: "Tallowby, Meridia", 1012: "Marlow Reach, Meridia",
    1013: "Port Ilvane, Meridia", 1014: "Tallowby, Meridia", 1015: "Marlow Reach, Meridia", 1016: "Port Ilvane, Meridia",
}

BUSINESSES = [
    (1017, "Harrowgate Bakery Supplies Ltd", "bakery ingredient wholesaler", "Unit 4, Rye Lane Estate", "Tallowby"),
    (1018, "Pinecrest Tooling Works Ltd", "precision tooling manufacturer", "Works Road 17", "Marlow Reach"),
    (1019, "Lanternfish Logistics Ltd", "regional delivery fleet", "Depot Way 2", "Port Ilvane"),
    (1020, "Brightwater Cash and Carry Ltd", "cash-and-carry grocer", "22 Market Square", "Tallowby"),
    (1021, "Nimbus Transit Consulting Ltd", "transport consulting", "Floor 3, 9 Cinder Quay", "Port Ilvane"),
    (1022, "Copperfield Import Traders Ltd", "import and trading", "Warehouse 6, Dock Road", "Port Ilvane"),
    (1023, "Saltmarsh Catering Co", "festival and event catering", "Kitchen Yard 1", "Marlow Reach"),
    (1024, "Orchard Lane Dental Group", "dental clinics", "30 Orchard Lane", "Tallowby"),
]

EMPLOYERS = ["Brindle and Marsh Printers", "Westergate Water Board", "Oakline Freight Co",
             "Harbourlight Services", "Tallowby Council Works", "Quillon Software Ltd",
             "Stillwater Clinic", "Ferrow Brothers Builders"]
MERCHANTS = ["Ironwood Electronics", "Quickfuel Station 44", "Harbourlight Cinema", "Marlow Reach Grocers",
             "Copperpot Cafe", "Tallowby Pharmacy", "Lantern Books", "Greenwick Garden Centre",
             "Pennyfarthing Bakery", "Velvet Rail Tickets", "Brook and Bay Clothing", "Kestrel Sports"]
SUPPLIERS = ["Tallowmere Packaging", "Rooksnest Components", "Alder and Vine Wholesale",
             "Kettlebridge Utilities", "Fernhollow Office Supplies", "Ashgrove Insurance Services",
             "Oakmeadow Maintenance", "Winterbourne Stationers"]
CUSTOMERS_PAYING = ["Dunmere Retail Group", "Foxfield Hospitality", "Garnet Street Stores",
                    "Hollowbeck Schools Trust", "Ivywick Care Homes", "Juniper Hill Hotels"]


def build_banks() -> dict:
    out = {}
    for code, name, cc, bic, city in BANKS:
        out[bic] = {"bic": bic, "bank_code": code, "name": name, "country": cc,
                    "country_name": COUNTRIES[cc], "city": city, "status": "active"}
    return out


def build_customers(today: date) -> dict:
    out = {}
    for num, name, dob, nat, street, town in INDIVIDUALS:
        cid = f"CUS-{num}"
        out[cid] = {
            "customer_id": cid, "type": "individual", "name": name, "date_of_birth": dob,
            "place_of_birth": PLACES_OF_BIRTH[num],
            "nationality": nat, "nationality_name": COUNTRIES[nat],
            "address": f"{street}, {town}, Meridia", "country_of_residence": "XM",
            "segment": "retail", "customer_since": d_ago(today, 400 + num % 37 * 40),
            "risk_rating": "standard", "status": "active", "kyc_review_due": d_ago(today, -(100 + num % 11 * 20)),
        }
    for num, name, activity, street, town in BUSINESSES:
        cid = f"CUS-{num}"
        out[cid] = {
            "customer_id": cid, "type": "business", "name": name, "business_activity": activity,
            "registration_country": "XM", "registration_number": f"XM-REG-{num * 7:06d}",
            "address": f"{street}, {town}, Meridia", "country_of_residence": "XM",
            "segment": "small business", "customer_since": d_ago(today, 700 + num % 13 * 90),
            "risk_rating": "standard", "status": "active", "kyc_review_due": d_ago(today, -(60 + num % 9 * 25)),
        }
    out["CUS-1010"]["risk_rating"] = "high (related to a politically exposed person)"
    out["CUS-1022"]["risk_rating"] = "medium"
    return out


def build_accounts(customers: dict, rng: random.Random, today: date) -> dict:
    out = {}
    for cid, c in customers.items():
        num = int(cid.split("-")[1])
        if c["type"] == "individual":
            products = [("Everyday Current Account", "USD")]
            if num % 2 == 0 or num in (1001, 1012):
                products.append(("Saver Account", "USD"))
        else:
            products = [("Business Current Account", "USD")]
            if num % 3 != 0:
                products.append(("Business Reserve Account", "USD"))
            if num == 1022:
                products.append(("Business Euro Account", "EUR"))
        for idx, (product, ccy) in enumerate(products, start=1):
            aid = f"ACC-{num}-{idx:02d}"
            number = f"{num:04d}{idx:02d}{rng.randrange(10 ** 8):08d}"
            out[aid] = {
                "account_id": aid, "customer_id": cid, "iban": make_iban("XM", "MRTB", number),
                "product": product, "currency": ccy, "status": "open",
                "opened": d_ago(today, 300 + num % 17 * 50 + idx * 11),
                "balance": 0.0, "bank_code": "MRTB", "bic": "MRTBXMM2",
            }
    return out


class TxnBuilder:
    def __init__(self, today: date):
        self.today = today
        self.rows: dict = {}
        self.counter: dict = {}

    def add(self, account: dict, days_ago: int, amount: float, direction: str, ttype: str,
            counterparty: str, narrative: str, counterparty_id: str = "", txn_id: str = "",
            country: str = "XM") -> str:
        acc_num = account["account_id"].replace("ACC-", "").replace("-", "")
        if not txn_id:
            n = self.counter.get(acc_num, 0) + 1
            self.counter[acc_num] = n
            txn_id = f"TXN-{acc_num}-{n:04d}"
        self.rows[txn_id] = {
            "transaction_id": txn_id, "account_id": account["account_id"],
            "date": d_ago(self.today, days_ago), "amount": round(float(amount), 2),
            "currency": account["currency"], "direction": direction, "type": ttype,
            "counterparty": counterparty, "counterparty_id": counterparty_id,
            "counterparty_country": country, "narrative": narrative,
        }
        return txn_id


SCENARIO_CUSTOMERS = {1020, 1021, 1022, 1023}


def build_background_transactions(customers: dict, accounts: dict, rng: random.Random, today: date) -> TxnBuilder:
    tb = TxnBuilder(today)
    for aid, acc in accounts.items():
        cust = customers[acc["customer_id"]]
        num = int(cust["customer_id"].split("-")[1])
        first = aid.endswith("-01")
        if cust["type"] == "individual":
            if first:
                employer = EMPLOYERS[num % len(EMPLOYERS)]
                salary = 2600 + (num % 9) * 330
                for month in range(3):
                    day = 5 + month * 30 + (num % 3)
                    if day < 90:
                        tb.add(acc, day, salary, "credit", "salary", employer, f"Salary {employer}")
                for k in range(rng.randint(8, 14)):
                    tb.add(acc, rng.randint(1, 89), rng.randint(300, 9500) / 100, "debit", "card_purchase",
                           rng.choice(MERCHANTS), "Card purchase")
                tb.add(acc, 12 + num % 5, 950 + (num % 4) * 60, "debit", "transfer_out",
                       "Rooksnest Property Lettings", "Rent")
                tb.add(acc, 40 + num % 5, 950 + (num % 4) * 60, "debit", "transfer_out",
                       "Rooksnest Property Lettings", "Rent")
                tb.add(acc, 70 + num % 5, 950 + (num % 4) * 60, "debit", "transfer_out",
                       "Rooksnest Property Lettings", "Rent")
                tb.add(acc, 20, rng.randint(4000, 12000) / 100, "debit", "atm_withdrawal", "ATM", "Cash withdrawal")
            else:
                tb.add(acc, 33, rng.randint(200, 900), "credit", "transfer_in", "Own account", "Transfer to savings")
                tb.add(acc, 63, rng.randint(200, 900), "credit", "transfer_in", "Own account", "Transfer to savings")
        else:
            if num in SCENARIO_CUSTOMERS and first:
                continue
            for k in range(rng.randint(9, 14)):
                tb.add(acc, rng.randint(1, 89), rng.randint(250000, 1250000) / 100, "credit", "transfer_in",
                       rng.choice(CUSTOMERS_PAYING), "Customer payment")
            for k in range(rng.randint(8, 12)):
                tb.add(acc, rng.randint(1, 89), rng.randint(120000, 780000) / 100, "debit", "transfer_out",
                       rng.choice(SUPPLIERS), "Supplier payment")
    return tb


def finalise_balances(accounts: dict, txns: dict, rng: random.Random) -> None:
    for aid, acc in accounts.items():
        net = 0.0
        for t in txns.values():
            if t["account_id"] == aid:
                net += t["amount"] if t["direction"] == "credit" else -t["amount"]
        opening = rng.randint(150000, 900000) / 100
        acc["balance"] = round(max(opening + net, 250.0), 2)
