"""Catalogue, version 1.3: the online shop's product listings, the suppliers' specifications, the style guide for
descriptions, a dozen new products with their image descriptions, and a month of the shop's search log.

Planted, and written out below: ten listings where one attribute is missing or does not match the supplier's
specification, six new products with no description yet, and twenty search terms that found nothing, in five
groups. Which listings were planted and which group a term belongs to is kept in its own record set
(catalogue_planted) and no operation serves it. The service holds no images: an image appears as a description in words.
"""

from __future__ import annotations

from datetime import date

from .seed_base import d_ago, period_of
from .seed_range import MARKET_SUPPLIERS, NOTICE, PRODUCTS, SKUS

ATTRIBUTES = ["net_quantity", "pack_size", "allergen_statement", "country_of_origin"]
IMAGES_NOTE = ("This service holds no images. Each image of a new product is given as a description in words, written "
               "by the photo studio. Nobody reading it has seen the picture.")

# ---------------------------------------------------------------- the style guide, version 1.3

MIN_WORDS, MAX_WORDS, MIN_TAGS, MAX_TAGS = 40, 80, 3, 6
BANNED_WORDS = ["best", "finest", "perfect", "amazing", "delicious", "healthy", "superfood", "guilt-free", "miracle",
                "world-class"]
ADULT_SENTENCE = "For adults aged 18 or over."
_GUIDE = [
    ("PS-1", "Length", "A description is 40 to 80 words, in two to four plain sentences."),
    ("PS-2", "How it opens", "The first sentence says what the product is. No slogan and no question."),
    ("PS-3", "Words that are not used", "These words are not used in a description: " + ", ".join(BANNED_WORDS) + "."),
    ("PS-4", "Claims", "A description makes no health or medical claim. It makes no claim the supplier's specification "
                       "does not make: the claims field of the specification is the only source for words such as "
                       "free-range, organic or vegan."),
    ("PS-5", "Net quantity and pack size", "The net quantity and the pack size are written exactly as the supplier's "
                                           "specification gives them."),
    ("PS-6", "Allergens", "The allergen statement is copied word for word from the supplier's specification into its own "
                          "field. It is never worked out from the ingredients, from the name or from a picture."),
    ("PS-7", "Country of origin", "The country of origin is written as the supplier's specification gives it."),
    ("PS-8", "Image tags", "Each product has three to six image tags, in lower case. A tag names something the image "
                           "description says is in the picture, and nothing else."),
    ("PS-9", "Age-restricted lines", "The description of an age-restricted line ends with the sentence: " + ADULT_SENTENCE),
    ("PS-10", "When a picture and the specification disagree", "The specification is used. The difference is listed for "
                                                               "the content lead, who asks the supplier."),
]
NOT_DECIDED = ("This guide does not publish a listing. A content lead reads every description and publishes it. The guide "
               "says nothing about a price or a promotion.")


def style_guide_markdown() -> str:
    out = ["# Product Style Guide (invented)", "", NOTICE, "",
           "Version: 1.3. Owner: Head of E-commerce. It covers the descriptions and image tags of Rowanmere Market's online shop.", ""]
    for rule_id, title, text in _GUIDE:
        out += [f"## {rule_id}. {title}", "", text, ""]
    out += ["## What this guide does not decide", "", NOT_DECIDED, ""]
    return "\n".join(out)


STYLE_GUIDE = {
    "document": "Product Style Guide", "version": "1.3", "owner": "Head of E-commerce", "notice": NOTICE,
    "minimum_words": MIN_WORDS, "maximum_words": MAX_WORDS, "minimum_image_tags": MIN_TAGS, "maximum_image_tags": MAX_TAGS,
    "words_not_used": BANNED_WORDS, "closing_sentence_for_age_restricted_lines": ADULT_SENTENCE,
    "rules": [{"rule_id": r, "title": t, "text": x} for r, t, x in _GUIDE],
    "what_the_guide_does_not_decide": NOT_DECIDED, "text": style_guide_markdown(),
}

# ---------------------------------------------------------------- planted: a listing attribute that is missing or does not match

# sku: (attribute, what the listing says; empty means the listing has nothing)
MISMATCHES = {
    "AG-4407": ("net_quantity", "1 kg"),
    "FZ-5602": ("net_quantity", ""),
    "PC-6603": ("net_quantity", "400 ml"),
    "BK-5703": ("allergen_statement", "Contains: wheat, milk"),
    "CH-5506": ("allergen_statement", ""),
    "AG-4412": ("allergen_statement", "Contains: peanuts"),
    "HH-6104": ("pack_size", "12"),
    "DR-5902": ("pack_size", ""),
    "FP-5804": ("country_of_origin", "Aldoria"),
    "AG-4401": ("country_of_origin", ""),
}

# ---------------------------------------------------------------- the dozen new products

AWAITING = ["AG-4411", "BK-5706", "CH-5508", "DR-5906", "FZ-5606", "HH-6107"]
# sku: (listed days ago, image descriptions, claims on the specification)
NEW = {
    "AG-4411": (4, ["Front of pack: a clear bag with a brown paper label. The label reads 'Rowanmere Oat Granola' and '500 g'. "
                    "Oat clusters, whole almonds and sunflower seeds can be seen through the bag.",
                    "Serving picture: a white bowl of granola with milk and sliced banana on a wooden table, with a spoon "
                    "beside it."], []),
    "BK-5706": (3, ["Front of pack: a card tray in clear film holding two pastries topped with flaked almonds and icing "
                    "sugar. The label reads 'Thrushcombe Almond Pastries' and '2 pack'.",
                    "Close view: one pastry cut in half on a plate, showing a pale filling."], []),
    "CH-5508": (5, ["Front of pack: a clear tub with a red sleeve. The sleeve reads 'Fenwillow Fresh Tomato Soup' and "
                    "'600 g'. The soup is orange-red.",
                    "Serving picture: the soup in a blue bowl with a swirl of cream and a basil leaf, and a slice of bread "
                    "on the side."], []),
    "DR-5906": (6, ["Bottle: a clear glass bottle of pale wine with a cream label that reads 'Windlebury White' and '75 cl'. "
                    "It has a screw cap.",
                    "Serving picture: two glasses of white wine on a table outdoors, with a plate of olives."], []),
    "FZ-5606": (2, ["Front of pack: a purple bag with a seal strip. It reads 'Pellowick Frozen Berry Mix' and '450 g'. A "
                    "picture on the bag shows raspberries, blueberries and blackberries.",
                    "Serving picture: the berries in a glass bowl with a spoon of yoghurt."], []),
    "HH-6107": (7, ["Front of pack: a green box that reads 'Drennock Dishwasher Tablets' and '30 tablets'. A picture on "
                    "the box shows a clean drinking glass.",
                    "Close view: one white and blue tablet in a clear wrapper, on a kitchen worktop."], []),
    "AG-4412": (18, ["Front of pack: a glass jar with a yellow lid. The label reads 'Marrowby Crunchy Peanut Butter' and '340 g'.",
                     "Serving picture: peanut butter on a slice of toast, with a knife."], []),
    "AG-4413": (21, ["Front of pack: a small green carton that reads 'Marrowby Vegetable Stock Cubes' and '12 cubes'.",
                     "Close view: three foil-wrapped cubes beside a pan."], []),
    "FZ-5603": (15, ["Front of pack: a card sleeve with a picture of a lasagne in a dish. It reads 'Pellowick Vegetable "
                     "Lasagne' and '400 g'.", "Serving picture: a portion of lasagne on a plate with salad leaves."], []),
    "BK-5704": (24, ["Front of pack: six round rolls topped with seeds in a clear bag. The label reads 'Thrushcombe Seeded "
                     "Rolls' and '6 pack'.", "Close view: one roll cut open, with butter."], []),
    "DR-5908": (12, ["Front of pack: a brown tub that reads 'Windlebury Drinking Chocolate' and '400 g'.",
                     "Serving picture: a mug of hot chocolate on a saucer."], []),
    "PC-6605": (27, ["Front of pack: a clear pump bottle of pale green liquid. The label reads 'Sablewood Hand Soap' and "
                     "'250 ml'.", "Serving picture: the bottle beside a basin."], []),
}
# what a careful reader lists for the content lead under PS-10
IMAGE_DIFFERENCES = {"FZ-5606": "The pack in the first image reads 450 g. The supplier's specification gives 500 g."}
CLAIMS = {"CH-5507": ["free-range"]}

STORAGE = {"ambient_grocery": "Store in a cool, dry place.", "chilled_food": "Keep refrigerated at 5 °C or below.",
           "frozen_food": "Keep frozen at -18 °C or below.", "bakery": "Store in a cool, dry place. Eat within two days of opening.",
           "fresh_produce": "Keep cool. Wash before use.", "drinks": "Store in a cool, dry place.",
           "household": "Keep out of the reach of children.", "personal_care": "Store below 25 °C."}
SHELF_LIFE = {"ambient_grocery": 365, "chilled_food": 14, "frozen_food": 365, "bakery": 5, "fresh_produce": 7, "drinks": 270,
              "household": 730, "personal_care": 730}


def make_spec(sku: str, p: dict, issued_on: str, claims: list) -> dict:
    return {"sku": sku, "specification_ref": f"SPEC-{sku}", "version": "1", "issued_on": issued_on,
            "supplier_id": p["supplier_id"], "supplier_name": p["supplier_name"], "product_name": p["name"],
            "brand": p["brand"], "net_quantity": p["net_quantity"], "pack_size": str(p["pack_size"]),
            "allergen_statement": p["allergen_statement"], "country_of_origin": p["country_of_origin"],
            "storage": STORAGE[p["category"]], "shelf_life_days": SHELF_LIFE[p["category"]],
            "age_restricted": p["age_restricted"], "claims": list(claims)}


def make_listing(sku: str, p: dict, status: str, new: bool, listed_on: str, images: list) -> dict:
    described = status == "live"
    text = (f"{p['name']} from {p['brand']}. {STORAGE[p['category']]}" + (f" {ADULT_SENTENCE}" if p["age_restricted"] else "")
            ) if described else ""
    return {"sku": sku, "name": p["name"], "brand": p["brand"], "category": p["category"], "status": status,
            "new_product": new, "listed_on": listed_on, "age_restricted": p["age_restricted"],
            "attributes": {"net_quantity": p["net_quantity"], "pack_size": str(p["pack_size"]),
                           "allergen_statement": p["allergen_statement"], "country_of_origin": p["country_of_origin"]},
            "description": text, "image_tags": [], "image_descriptions": list(images), "description_drafts": [],
            "published": None}


# ---------------------------------------------------------------- the search log

# the twenty terms that found nothing, by what shoppers seem to have wanted
NO_RESULT_GROUPS = {
    "Gluten-free bread and bakery": [("gluten free bread", 212), ("gluten free rolls", 88), ("gf bread", 64), ("coeliac bread", 31)],
    "Milk made from plants": [("oat milk", 301), ("almond milk", 143), ("soya milk", 96), ("oat drink", 57)],
    "A product the shop sells, spelled another way": [("yogurt", 152), ("mozarella", 118), ("spagetti", 74), ("shampo", 29)],
    "Help with an order, not a product": [("track my order", 187), ("delivery slots", 133), ("opening hours", 108), ("returns label", 69)],
    "Pet food and pet care": [("cat food", 240), ("dog food", 198), ("cat litter", 77), ("dog treats", 52)],
}
_FOUND = [("butter", 640, 3), ("bread", 598, 4), ("milk", 571, 2), ("eggs", 512, 1), ("coffee", 455, 2), ("pasta", 430, 3),
          ("tomatoes", 388, 3), ("wine", 371, 2), ("onions", 344, 2), ("flour", 326, 3), ("toilet roll", 301, 1),
          ("cheese", 296, 2), ("juice", 280, 1), ("rice", 262, 1), ("bananas", 259, 1), ("yoghurt", 244, 1),
          ("frozen peas", 231, 1), ("chips", 219, 1), ("tea bags", 208, 1), ("shampoo", 197, 1), ("olive oil", 193, 1),
          ("soup", 188, 1), ("lager", 174, 1), ("croissants", 166, 1), ("ice cream", 158, 1), ("mozzarella", 149, 2),
          ("spaghetti", 141, 1), ("carrots", 136, 1), ("cola", 129, 1), ("granola", 117, 1), ("peanut butter", 109, 1),
          ("batteries", 96, 1), ("razor blades", 88, 1), ("almond", 81, 2), ("toothpaste", 77, 1), ("fish fillets", 72, 1),
          ("spinach", 66, 1), ("bin bags", 58, 1), ("hand soap", 51, 1), ("ready meals", 47, 2)]


def make_search_log(period: str) -> dict:
    rows = [{"term": t, "searches": n, "results_found": r} for t, n, r in _FOUND]
    rows += [{"term": t, "searches": n, "results_found": 0} for terms in NO_RESULT_GROUPS.values() for t, n in terms]
    rows.sort(key=lambda x: (-x["searches"], x["term"]))
    return {"period": period, "rows": rows}


# ---------------------------------------------------------------- the whole starting set

def build_catalogue(today: date) -> dict:
    issued = d_ago(today, 200)
    listings, specs = {}, {}
    for sku in SKUS:
        p = PRODUCTS[sku]
        new = sku in NEW
        ago, images, _ = NEW.get(sku, (0, [], []))
        listing = make_listing(sku, p, "awaiting_description" if sku in AWAITING else "live", new,
                               d_ago(today, ago) if new else d_ago(today, 400), images)
        if sku in MISMATCHES:
            attribute, says = MISMATCHES[sku]
            listing["attributes"][attribute] = says
        listings[sku] = listing
        specs[sku] = make_spec(sku, p, d_ago(today, 30) if new else issued, CLAIMS.get(sku, []))
    period = period_of(today)
    planted = {
        "mismatches": {sku: {"attribute": a, "kind": "does_not_match" if says else "missing", "listing_value": says,
                             "specification_value": specs[sku][a]} for sku, (a, says) in MISMATCHES.items()},
        "awaiting_description": list(AWAITING), "image_differences": dict(IMAGE_DIFFERENCES),
        "no_result_groups": {name: [t for t, _ in terms] for name, terms in NO_RESULT_GROUPS.items()},
    }
    return {"catalogue_products": listings, "supplier_specs": specs, "search_log": {period: make_search_log(period)},
            "search_analyses": {}, "product_data_checks": {"checks": []}, "catalogue_planted": planted}


# ---------------------------------------------------------------- what arrives

# new-product. Four templates, in turn: name, brand, category, supplier, net quantity, pack size, allergen statement,
# country of origin, age restricted, image descriptions, and the difference a careful reader lists (empty when none).
_SIM_NEW = [
    ("Chickpeas in water, 400 g tin", "Marrowby", "ambient_grocery", "SUP-311", "400 g", "1", "No allergens", "Tessaly", False,
     ["Front of pack: a tin with a yellow label that reads 'Marrowby Chickpeas in Water' and '400 g'.",
      "Serving picture: chickpeas in a salad bowl with chopped parsley and a wedge of lemon."], ""),
    ("Cheese and onion pasty, 180 g", "Thrushcombe", "bakery", "SUP-314", "180 g", "1", "Contains: wheat, milk, egg", "Meridia", False,
     ["Front of pack: one golden pasty with a crimped edge in a clear film. The label reads 'Thrushcombe Cheese and Onion "
      "Pasty' and '180 g'.", "Close view: the pasty cut in half on a board, showing a pale filling."], ""),
    ("Sparkling rosé wine, 75 cl", "Windlebury", "drinks", "SUP-316", "75 cl", "1", "Contains: sulphites", "Tessaly", True,
     ["Bottle: a clear glass bottle of pink sparkling wine with a foil top. The label reads 'Windlebury Sparkling Rosé' and '75 cl'.",
      "Serving picture: two tall glasses of pink sparkling wine on a tray."], ""),
    ("Fruit and nut bar, 40 g", "Marrowby", "ambient_grocery", "SUP-311", "40 g", "1", "Contains: peanuts, almonds (nuts)", "Quenmark", False,
     ["Front of pack: a bar in an orange wrapper that reads 'Marrowby Fruit and Nut Bar' and '45 g'.",
      "Close view: the bar unwrapped, showing raisins and pieces of nut."],
     "The wrapper in the first image reads 45 g. The supplier's specification gives 40 g."),
]


def sim_new_product(data: dict, today: date, kind: int, sku: str) -> tuple[str, str]:
    name, brand, category, supplier_id, net, pack, allergens, origin, adult, images, difference = _SIM_NEW[kind]
    p = {"name": name, "brand": brand, "category": category, "supplier_id": supplier_id,
         "supplier_name": MARKET_SUPPLIERS[supplier_id][0], "net_quantity": net, "pack_size": pack,
         "allergen_statement": allergens, "country_of_origin": origin, "age_restricted": adult}
    data["catalogue_products"][sku] = make_listing(sku, p, "awaiting_description", True, today.isoformat(), images)
    data["supplier_specs"][sku] = make_spec(sku, p, today.isoformat(), [])
    data["catalogue_planted"]["awaiting_description"].append(sku)
    if difference:
        data["catalogue_planted"]["image_differences"][sku] = difference
    return sku, (f"A new product {sku}, {name}, has arrived in the catalogue system from {p['supplier_name']}. It has a "
                 f"supplier's specification and {len(images)} image descriptions, and no description yet. Read it with "
                 "list_new_products and get_supplier_specification, and the style guide with get_product_style_guide.")
