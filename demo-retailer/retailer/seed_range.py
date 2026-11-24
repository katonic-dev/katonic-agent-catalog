"""Version 1.3: the sixty lines of Rowanmere Market that the catalogue, stock, pricing and loyalty systems share.

One row for each line: what it is, what it sells for, what it costs, and who supplies it. Seven of the lines are
the grocery, chilled, frozen and personal care items the online shop's orders already name, with the same ids and
prices. Everything here is invented.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import VAT_RATE, money

NOTICE = "Rowanmere Group is invented, and so is this document. It is not the document of any real retailer."

CATEGORIES = ["ambient_grocery", "chilled_food", "frozen_food", "bakery", "fresh_produce", "drinks", "household",
              "personal_care"]

STORE_IDS = ["S-101", "S-102", "S-103", "S-104", "S-105", "S-106", "S-107", "S-108"]
# what each store takes of a line, in seventieths: the four supermarkets take most
SHARES = {"S-101": 14, "S-102": 12, "S-103": 4, "S-104": 12, "S-105": 5, "S-106": 5, "S-107": 13, "S-108": 5}

# Suppliers of the Market's lines. Three of them also supply the restaurants and are in the purchasing system.
MARKET_SUPPLIERS = {
    "SUP-301": ("Ilvane Valley Dairy Ltd", 3, True),
    "SUP-303": ("Tallowby Flour Mills Ltd", 5, True),
    "SUP-304": ("Orchard Gate Fresh Produce Ltd", 2, True),
    "SUP-311": ("Marrowby Provisions Ltd", 7, False),
    "SUP-312": ("Fenwillow Chilled Foods Ltd", 3, False),
    "SUP-313": ("Pellowick Frozen Foods Ltd", 6, False),
    "SUP-314": ("Thrushcombe Bakery Ltd", 1, False),
    "SUP-315": ("Sedgeholt Growers Ltd", 2, False),
    "SUP-316": ("Windlebury Drinks Ltd", 7, False),
    "SUP-317": ("Drennock Home and Care Ltd", 10, False),
}

NONE = "No allergens"
# sku, name, brand, category, price, cost, net quantity, pack size, allergen statement, country of origin, supplier,
# units in a case, units sold in a week by the eight stores together
_P = [
    ("AG-4401", "Olive oil, 1 litre bottle", "Marrowby", "ambient_grocery", 11.50, 7.10, "1 litre", 1, NONE, "Tessaly", "SUP-311", 6, 210),
    ("AG-4402", "Coffee beans, 1 kg", "Marrowby", "ambient_grocery", 18.40, 11.20, "1 kg", 1, NONE, "Aldoria", "SUP-311", 6, 140),
    ("AG-4403", "Pasta sauce, six jars", "Rowanmere", "ambient_grocery", 13.20, 7.90, "6 x 340 g", 6, "Contains: celery", "Meridia", "SUP-311", 4, 140),
    ("AG-4405", "Spaghetti, 500 g", "Rowanmere", "ambient_grocery", 1.49, 0.85, "500 g", 1, "Contains: wheat", "Tessaly", "SUP-311", 20, 700),
    ("AG-4406", "Chopped tomatoes, four tins", "Rowanmere", "ambient_grocery", 3.49, 2.05, "4 x 400 g", 4, NONE, "Tessaly", "SUP-311", 6, 420),
    ("AG-4407", "Basmati rice, 1 kg", "Marrowby", "ambient_grocery", 3.25, 2.28, "900 g", 1, NONE, "Brevnia", "SUP-311", 10, 280),
    ("AG-4408", "Plain flour, 1.5 kg", "Tallowby Mills", "ambient_grocery", 1.95, 1.10, "1.5 kg", 1, "Contains: wheat", "Meridia", "SUP-303", 10, 350),
    ("AG-4409", "Strong white bread flour, 1.5 kg", "Tallowby Mills", "ambient_grocery", 2.45, 1.40, "1.5 kg", 1, "Contains: wheat", "Meridia", "SUP-303", 10, 210),
    ("AG-4410", "Pizza flour, 1 kg", "Tallowby Mills", "ambient_grocery", 2.29, 1.30, "1 kg", 1, "Contains: wheat", "Meridia", "SUP-303", 10, 140),
    ("AG-4411", "Oat granola, 500 g", "Rowanmere", "ambient_grocery", 3.99, 2.30, "500 g", 1, "Contains: oats, almonds (nuts)", "Meridia", "SUP-311", 8, 210),
    ("AG-4412", "Peanut butter, crunchy, 340 g", "Marrowby", "ambient_grocery", 2.99, 1.75, "340 g", 1, "Contains: peanuts. May contain: other nuts, sesame", "Quenmark", "SUP-311", 12, 210),
    ("AG-4413", "Vegetable stock cubes, pack of 12", "Marrowby", "ambient_grocery", 1.79, 0.95, "120 g", 12, "Contains: celery", "Meridia", "SUP-311", 24, 280),
    ("CH-5501", "Chilled ready meals, pack of four", "Fenwillow", "chilled_food", 19.80, 12.40, "4 x 400 g", 4, "Contains: milk, wheat", "Meridia", "SUP-312", 4, 140),
    ("CH-5502", "Salted butter, 250 g", "Ilvane Valley", "chilled_food", 2.49, 1.40, "250 g", 1, "Contains: milk", "Meridia", "SUP-301", 20, 840),
    ("CH-5503", "Unsalted butter, 250 g", "Ilvane Valley", "chilled_food", 2.49, 1.40, "250 g", 1, "Contains: milk", "Meridia", "SUP-301", 20, 280),
    ("CH-5504", "Mozzarella, 125 g ball", "Ilvane Valley", "chilled_food", 1.29, 0.72, "125 g", 1, "Contains: milk", "Meridia", "SUP-301", 12, 350),
    ("CH-5505", "Grated mozzarella, 200 g", "Ilvane Valley", "chilled_food", 2.75, 1.55, "200 g", 1, "Contains: milk", "Meridia", "SUP-301", 12, 420),
    ("CH-5506", "Natural yoghurt, 500 g", "Fenwillow", "chilled_food", 1.85, 1.05, "500 g", 1, "Contains: milk", "Meridia", "SUP-312", 6, 490),
    ("CH-5507", "Free-range eggs, box of six", "Fenwillow", "chilled_food", 2.35, 1.40, "6 eggs", 6, "Contains: egg", "Meridia", "SUP-312", 15, 560),
    ("CH-5508", "Fresh tomato soup, 600 g", "Fenwillow", "chilled_food", 2.95, 1.70, "600 g", 1, "Contains: celery, milk", "Meridia", "SUP-312", 6, 210),
    ("FZ-5601", "Frozen fish fillets, 1 kg", "Pellowick", "frozen_food", 14.90, 9.60, "1 kg", 1, "Contains: fish", "Quenmark", "SUP-313", 6, 140),
    ("FZ-5602", "Garden peas, 900 g", "Pellowick", "frozen_food", 4.20, 2.55, "900 g", 1, NONE, "Meridia", "SUP-313", 10, 280),
    ("FZ-5603", "Vegetable lasagne, 400 g", "Pellowick", "frozen_food", 3.75, 2.20, "400 g", 1, "Contains: milk, wheat, celery", "Meridia", "SUP-313", 8, 140),
    ("FZ-5604", "Vanilla ice cream, 1 litre", "Pellowick", "frozen_food", 3.95, 2.30, "1 litre", 1, "Contains: milk", "Meridia", "SUP-313", 6, 140),
    ("FZ-5605", "Oven chips, 1.5 kg", "Pellowick", "frozen_food", 2.95, 2.09, "1.5 kg", 1, NONE, "Meridia", "SUP-313", 8, 350),
    ("FZ-5606", "Frozen berry mix, 500 g", "Pellowick", "frozen_food", 4.49, 2.60, "500 g", 1, NONE, "Rovaland", "SUP-313", 10, 140),
    ("BK-5701", "White sliced loaf, 800 g", "Thrushcombe", "bakery", 1.59, 1.12, "800 g", 1, "Contains: wheat", "Meridia", "SUP-314", 10, 910),
    ("BK-5702", "Wholemeal loaf, 800 g", "Thrushcombe", "bakery", 1.75, 1.00, "800 g", 1, "Contains: wheat", "Meridia", "SUP-314", 10, 280),
    ("BK-5703", "Butter croissants, pack of four", "Thrushcombe", "bakery", 2.65, 1.50, "4 x 55 g", 4, "Contains: wheat, milk, egg", "Meridia", "SUP-314", 8, 280),
    ("BK-5704", "Seeded rolls, pack of six", "Thrushcombe", "bakery", 2.15, 1.20, "6 x 60 g", 6, "Contains: wheat, sesame", "Meridia", "SUP-314", 8, 210),
    ("BK-5705", "Fruit scones, pack of four", "Thrushcombe", "bakery", 2.25, 1.25, "4 x 70 g", 4, "Contains: wheat, milk", "Meridia", "SUP-314", 8, 210),
    ("BK-5706", "Almond pastries, pack of two", "Thrushcombe", "bakery", 2.85, 1.60, "2 x 85 g", 2, "Contains: wheat, milk, egg, almonds (nuts)", "Meridia", "SUP-314", 8, 140),
    ("FP-5801", "Green peppers, pack of three", "Orchard Gate", "fresh_produce", 1.95, 1.10, "3 peppers", 3, NONE, "Meridia", "SUP-304", 12, 630),
    ("FP-5802", "White onions, 1 kg", "Orchard Gate", "fresh_produce", 1.35, 0.75, "1 kg", 1, NONE, "Meridia", "SUP-304", 8, 560),
    ("FP-5803", "Red onions, 750 g", "Orchard Gate", "fresh_produce", 1.45, 0.80, "750 g", 1, NONE, "Meridia", "SUP-304", 8, 280),
    ("FP-5804", "Bananas, bunch of five", "Sedgeholt", "fresh_produce", 1.15, 0.70, "5 bananas", 5, NONE, "Brevnia", "SUP-315", 12, 840),
    ("FP-5805", "Carrots, 1 kg", "Sedgeholt", "fresh_produce", 0.95, 0.52, "1 kg", 1, NONE, "Meridia", "SUP-315", 10, 630),
    ("FP-5806", "Baby spinach, 200 g", "Sedgeholt", "fresh_produce", 1.65, 0.92, "200 g", 1, NONE, "Meridia", "SUP-315", 8, 210),
    ("FP-5807", "Vine tomatoes, 500 g", "Sedgeholt", "fresh_produce", 2.25, 1.28, "500 g", 1, NONE, "Tessaly", "SUP-315", 8, 420),
    ("DR-5901", "Orange juice, 1 litre", "Windlebury", "drinks", 2.69, 1.40, "1 litre", 1, NONE, "Aldoria", "SUP-316", 8, 560),
    ("DR-5902", "Sparkling water, six bottles", "Windlebury", "drinks", 2.95, 1.60, "6 x 500 ml", 6, NONE, "Meridia", "SUP-316", 4, 350),
    ("DR-5903", "Cola, six cans", "Rowanmere", "drinks", 3.45, 2.40, "6 x 330 ml", 6, NONE, "Meridia", "SUP-316", 4, 420),
    ("DR-5904", "Breakfast tea, 80 bags", "Windlebury", "drinks", 3.15, 1.75, "250 g", 80, NONE, "Brevnia", "SUP-316", 12, 140),
    ("DR-5905", "Red wine, 75 cl", "Windlebury", "drinks", 9.95, 5.90, "75 cl", 1, "Contains: sulphites", "Tessaly", "SUP-316", 6, 210),
    ("DR-5906", "White wine, 75 cl", "Windlebury", "drinks", 9.45, 5.60, "75 cl", 1, "Contains: sulphites", "Tessaly", "SUP-316", 6, 210),
    ("DR-5907", "Lager, four cans", "Windlebury", "drinks", 5.95, 3.50, "4 x 440 ml", 4, "Contains: barley", "Meridia", "SUP-316", 6, 280),
    ("DR-5908", "Drinking chocolate, 400 g", "Windlebury", "drinks", 3.59, 2.05, "400 g", 1, "Contains: milk", "Meridia", "SUP-316", 6, 140),
    ("HH-6101", "Washing-up liquid, 500 ml", "Drennock", "household", 1.65, 0.90, "500 ml", 1, "Not a food", "Meridia", "SUP-317", 12, 280),
    ("HH-6102", "Laundry liquid, 1.5 litre", "Drennock", "household", 8.99, 5.20, "1.5 litre", 1, "Not a food", "Meridia", "SUP-317", 4, 210),
    ("HH-6103", "Kitchen towel, two rolls", "Drennock", "household", 2.19, 1.30, "2 rolls", 2, "Not a food", "Quenmark", "SUP-317", 10, 350),
    ("HH-6104", "Toilet tissue, nine rolls", "Drennock", "household", 4.95, 2.90, "9 rolls", 9, "Not a food", "Quenmark", "SUP-317", 5, 420),
    ("HH-6105", "Batteries AA, pack of eight", "Drennock", "household", 6.95, 3.90, "8 batteries", 8, "Not a food", "Rovaland", "SUP-317", 12, 70),
    ("HH-6106", "Bin liners, roll of 20", "Drennock", "household", 1.95, 1.05, "20 liners", 20, "Not a food", "Meridia", "SUP-317", 12, 140),
    ("HH-6107", "Dishwasher tablets, pack of 30", "Drennock", "household", 5.49, 3.10, "540 g", 30, "Not a food", "Quenmark", "SUP-317", 6, 140),
    ("PC-6601", "Electric toothbrush heads, pack of eight", "Sablewood", "personal_care", 22.00, 12.80, "8 heads", 8, "Not a food", "Rovaland", "SUP-317", 6, 70),
    ("PC-6602", "Moisturising cream, 200 ml", "Sablewood", "personal_care", 16.50, 9.40, "200 ml", 1, "Not a food", "Meridia", "SUP-317", 6, 70),
    ("PC-6603", "Shampoo, 400 ml", "Sablewood", "personal_care", 3.85, 2.10, "350 ml", 1, "Not a food", "Meridia", "SUP-317", 6, 140),
    ("PC-6604", "Razor blades, pack of four", "Sablewood", "personal_care", 9.99, 5.00, "4 blades", 4, "Not a food", "Rovaland", "SUP-317", 10, 70),
    ("PC-6605", "Hand soap, 250 ml", "Sablewood", "personal_care", 1.89, 1.00, "250 ml", 1, "Not a food", "Meridia", "SUP-317", 12, 210),
    ("PC-6606", "Toothpaste, 100 ml", "Sablewood", "personal_care", 2.45, 1.35, "100 ml", 1, "Not a food", "Meridia", "SUP-317", 12, 70),
]
AGE_RESTRICTED = {"DR-5905", "DR-5906", "DR-5907"}

PRODUCTS = {
    p[0]: {"sku": p[0], "name": p[1], "brand": p[2], "category": p[3], "price": p[4], "cost": p[5], "net_quantity": p[6],
           "pack_size": p[7], "allergen_statement": p[8], "country_of_origin": p[9], "supplier_id": p[10],
           "supplier_name": MARKET_SUPPLIERS[p[10]][0], "case_size": p[11], "weekly_units": p[12],
           "age_restricted": p[0] in AGE_RESTRICTED}
    for p in _P
}
SKUS = list(PRODUCTS)
assert len(SKUS) == 60 and all(p["weekly_units"] % 70 == 0 for p in PRODUCTS.values())


def ex_tax(price: float) -> float:
    return price / (1 + VAT_RATE)


def margin_percent(price: float, cost: float) -> float:
    """What is left of the price without tax once the cost is taken off, as a percent of the price without tax."""
    net = ex_tax(price)
    return round((net - cost) / net * 100 + 1e-9, 1)


def unit_profit(price: float, cost: float) -> float:
    return money(ex_tax(price) - cost)


def week_endings(today: date) -> list[str]:
    """The thirteen full weeks before the retailer date, oldest first. A week ends on a Sunday."""
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7 or 7)
    return [(last_sunday - timedelta(weeks=n)).isoformat() for n in range(12, -1, -1)]


def split(total: int) -> dict:
    """One number shared out over the eight stores. What is left over after whole seventieths goes to S-101."""
    out = {s: total * SHARES[s] // 70 for s in STORE_IDS}
    out["S-101"] += total - sum(out.values())
    return out
