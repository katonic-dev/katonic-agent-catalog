"""Seed data, part 6: an invented press archive for adverse media screening.

Two invented outlets. 25 articles with fixed ids. The groups are: adverse coverage of people and companies that are
in the data (ART-6001 to 6006), namesakes who are plainly someone else (6007 to 6011), neutral or good news about
customers (6012 to 6015) and unrelated noise (6016 to 6025). SCENARIOS.md has a table per subject.
"""

from __future__ import annotations

from datetime import date

from .seed_base import d_ago

COURIER = "The Meridia Courier"
DAILY = "Port Ilvane Business Daily"

# id, outlet, days ago, section, title, body (paragraphs separated by a blank line)
ARTICLES = [
    ("ART-6001", COURIER, 410, "World", "Quenmark freezes the assets of arms broker Valdis Orrenmoor",
     "Authorities in Quenmark have frozen the assets of Valdis Orrenmoor, a Quenmark national born on 30 September 1971 "
     "who lives on Cinder Quay in Port Ilvane. They say he brokered shipments of weapons to buyers under an embargo.\n\n"
     "The order covers bank accounts, two warehouses and a share in a shipping company. The Quenmark foreign ministry "
     "said it followed a two-year inquiry. Mr Orrenmoor has not commented. His lawyer said the order would be challenged."),
    ("ART-6002", DAILY, 95, "Law", "Court upholds the freezing order on Valdis Orrenmoor",
     "A court in Quenmark has upheld the order that froze the assets of Valdis Orrenmoor, the arms broker who lives in "
     "Port Ilvane. The judge said the evidence of arms brokering was strong and that the order must stay in place.\n\n"
     "Mr Orrenmoor was born in 1971. The court heard that payments linked to the shipments passed through accounts "
     "in several countries. His lawyer said he will appeal."),
    ("ART-6003", DAILY, 52, "Trade", "Gallowmere customs open an inquiry into Karn Harbour Freight Agency",
     "Customs officers in Gallowmere, Kharnovia, have opened an inquiry into Karn Harbour Freight Agency. Inspectors "
     "found containers declared as machine parts that held other goods. They are also checking whether the values on "
     "the papers were too low.\n\n"
     "The agency handles freight for importers in several countries. It has said it follows the rules and will help the "
     "inquiry. Two shipments are being held at the port."),
    ("ART-6004", COURIER, 14, "World", "Freight agency in Kharnovia accused of moving goods for listed buyers",
     "Karn Harbour Freight Agency, a company based in Gallowmere, Kharnovia, is accused of moving goods for buyers "
     "named on Meridia's consolidated sanctions list. The claim comes from a report by a trade monitoring group.\n\n"
     "The report says the agency used short-lived shell companies to book the cargo. The agency did not answer "
     "questions. Kharnovia's customs service said the inquiry it opened earlier this year is still running."),
    ("ART-6005", COURIER, 160, "Politics", "Minister Leopold Vanhollow questioned over a road contract",
     "Leopold Vanhollow, the Minister of Public Works in Quenmark, is under pressure over a road contract worth "
     "USD 41 million. The firm that won it is owned by his brother-in-law.\n\n"
     "Mr Vanhollow, born in 1972, says the tender was fair and that he took no part in the choice. The opposition has "
     "asked for an independent inquiry. The ministry says the firm was the lowest bidder."),
    ("ART-6006", DAILY, 40, "Politics", "Audit office widens its inquiry into road tenders under Minister Vanhollow",
     "Quenmark's audit office has widened its inquiry into road tenders overseen by Public Works Minister Leopold "
     "Vanhollow. It will now look at four more contracts awarded in the past three years.\n\n"
     "The office said it found gaps in the records of two earlier tenders. The minister says he welcomes the review. "
     "No one has been charged."),
    ("ART-6007", COURIER, 230, "Courts", "Skipper fined for landing more fish than his quota allows",
     "Ilvane Marrowick, 63, a trawler skipper from Corrowick in Brevnia, was fined USD 8,000 for landing more fish than "
     "his quota allows. The court heard that he had done so on six trips over two years.\n\n"
     "Mr Marrowick said he had been misled by his broker over the size of the quota. He plans to sell one of his "
     "two boats to pay the fine."),
    ("ART-6008", COURIER, 75, "Courts", "Machinery dealer jailed for hiding sales from tax inspectors",
     "Wynne Castellane, 54, a farm machinery dealer from Brandymoor in Tessaly, was jailed for 18 months for hiding "
     "sales from tax inspectors. The court heard that he kept a second set of books for six years.\n\n"
     "Castellane's company has been closed. A Tessaly tax official said the unpaid tax is about USD 600,000."),
    ("ART-6009", DAILY, 130, "Sport", "Teenage sprinter banned for two years after a failed test",
     "Oskar Brindlemoor, 19, a student sprinter from Silverkeld in Norvania, has been banned for two years after a "
     "failed doping test. The test was taken at the national junior games.\n\n"
     "His club said it was shocked and will help with his appeal. The ban ends his place in next year's national "
     "squad."),
    ("ART-6010", COURIER, 300, "Courts", "Former hospital administrator convicted of embezzlement",
     "Sabine Tarrowgate, 71, who ran a hospital in Velmora, Aldoria, for twelve years, was convicted of embezzling "
     "USD 1.2 million from its building fund. She will be sentenced next month.\n\n"
     "The court heard that she paid fake invoices to a company owned by a relative. Ms Tarrowgate told the court she "
     "had made mistakes but had not stolen the money."),
    ("ART-6011", DAILY, 205, "Companies", "Hartsfell flour mill Harrowgate Bakery Supplies Ltd enters administration",
     "Harrowgate Bakery Supplies Ltd, a flour mill in Hartsfell, Quenmark, has entered administration with debts of "
     "about USD 3 million. The mill supplied bakeries across Quenmark.\n\n"
     "The administrators said a poor wheat harvest and a loss of two large customers brought the company down. About "
     "40 jobs are at risk. The company has no link to any business in Meridia."),
    ("ART-6012", DAILY, 36, "Awards", "Pinecrest Tooling Works wins the export award",
     "Pinecrest Tooling Works Ltd of Marlow Reach has won this year's regional export award. The precision tooling "
     "maker sells to buyers in five countries and grew its exports by nearly a fifth.\n\n"
     "The judges praised its record on delivery times and its apprentice scheme. The company said the prize belongs to "
     "its 85 staff."),
    ("ART-6013", DAILY, 21, "Companies", "Lanternfish Logistics adds five vehicles and a second depot",
     "Lanternfish Logistics Ltd of Port Ilvane has added five delivery vehicles to its fleet and plans a second depot "
     "on the east side of the city. The regional delivery firm says demand from local shops has doubled in two years.\n\n"
     "The expansion will create about 30 jobs. The company said the new vehicles were bought with a bank loan."),
    ("ART-6014", COURIER, 18, "Food", "Saltmarsh Catering Co will feed the harvest festival",
     "Saltmarsh Catering Co of Marlow Reach has won the contract to feed visitors at this year's harvest festival. The "
     "event caterer is hiring about twenty seasonal staff.\n\n"
     "The owner said preparations began weeks ago. The festival opens in a fortnight and is expected to draw "
     "30,000 visitors."),
    ("ART-6015", COURIER, 90, "Community", "Marguerite Oakhaven elected chair of the Marlow Reach schools parents' group",
     "Marguerite Oakhaven, who lives on Bellwether Close in Marlow Reach, has been elected chair of the Marlow Reach "
     "schools parents' group. She takes over from a chair who served for six years.\n\n"
     "Ms Oakhaven said her first task is a safer crossing outside the primary school. The group has about 300 members."),
    ("ART-6016", COURIER, 5, "Weather", "Dry fortnight forecast for the Meridia harvest",
     "Forecasters expect a dry fortnight across Meridia, which should help farmers bring in the late harvest. "
     "Temperatures will stay mild. Rain is likely at the end of the month."),
    ("ART-6017", DAILY, 8, "Infrastructure", "Port Ilvane dredging contract goes to Tidewater Dredging",
     "Tidewater Dredging Co has won the contract to deepen the main channel at Port Ilvane. Work starts in the spring "
     "and should take eight months. The port authority said the larger channel will take bigger ships."),
    ("ART-6018", COURIER, 12, "Sport", "Marlow Reach beat Tallowby United 2-1",
     "Marlow Reach came from behind to beat Tallowby United 2-1 on Saturday. Two goals in the last ten minutes "
     "settled the match. The win lifts the club to third in the table."),
    ("ART-6019", DAILY, 17, "Economy", "Central Bank of Meridia holds its policy rate",
     "The Central Bank of Meridia has left its policy rate unchanged. The governor said price rises are slowing but "
     "wage growth is still strong. The next decision is due in six weeks."),
    ("ART-6020", COURIER, 26, "Transport", "New bus timetable for the Heron Steps route",
     "A new timetable starts on Monday on the Heron Steps bus route. Buses will run every ten minutes at peak hours. "
     "The last bus on weekdays leaves the harbour at 23:15."),
    ("ART-6021", DAILY, 33, "Property", "Cold-storage warehouse planned at Eastgate Quay",
     "A developer has asked for permission to build a cold-storage warehouse at Eastgate Quay. The site would hold "
     "frozen and chilled food for shops and restaurants. The council will decide in the new year."),
    ("ART-6022", COURIER, 48, "Culture", "Port Ilvane museum reopens after repairs",
     "The Port Ilvane maritime museum has reopened after eight months of roof repairs. The collection of ship models "
     "is back on show. Entry is free on the first Sunday of each month."),
    ("ART-6023", DAILY, 61, "Markets", "Seed-oil prices ease as the harvest comes in",
     "Prices for seed oil fell this month as larger harvests came in across the region. Traders expect prices to stay "
     "low until the spring. Food makers say the fall may lower shop prices."),
    ("ART-6024", COURIER, 120, "Local", "Tallowby market to move to Sundays",
     "Tallowby's weekly market will move from Saturday to Sunday from next month. Traders voted for the change after "
     "a survey of shoppers. Parking near the square will be free on market days."),
    ("ART-6025", DAILY, 188, "Banking", "Aldoria Commerce Bank opens a representative office in Port Ilvane",
     "Aldoria Commerce Bank has opened a representative office in Port Ilvane. The office will help Aldoria firms "
     "that trade with Meridia. It will not take deposits."),
]


def build_news(today: date) -> dict:
    out = {}
    for aid, outlet, ago, section, title, body in ARTICLES:
        out[aid] = {"article_id": aid, "outlet": outlet, "date": d_ago(today, ago), "section": section, "title": title,
                    "body": body}
    return out
