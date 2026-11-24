"""Customer care, version 1: guest feedback for the period (260 comments).

The theme each comment was made from is kept in its own record set (feedback_themes) and no operation serves it.
"""

from __future__ import annotations

import random
from datetime import date

from .seed_base import days_in, period_of, yymm
from .seed_stores import RESTAURANT_IDS

ITEMS = ["garlic bread", "the wings", "one of the two pizzas", "the dips", "the lava cake", "the drinks", "the wedges",
         "the cheesy bread", "the doughnuts", "the iced latte"]
PIZZA = ["margherita", "pepperoni", "chicken tikka", "veggie supreme", "barbecue chicken", "four cheese"]
TEXTS = {
    "late": ["Order arrived {m} minutes after the time the app showed.",
             "Waited {m} minutes longer than promised and nobody called to say it was late.",
             "The tracker said out for delivery for {m} minutes. Far too slow.",
             "Delivery was {m} minutes late on a weeknight. Used to be much faster.",
             "Ordered for a family dinner, it came {m} minutes late and the kids had gone to bed.",
             "Third time this month the delivery is late, {m} minutes this time.",
             "Promised 30 minutes, took over an hour.",
             "Driver could not find the building and the order was {m} minutes late.",
             "Late again. {m} minutes past the promised time.",
             "The app kept adding ten more minutes. In the end {m} minutes late."],
    "wrong": ["{i} was missing from the bag.", "I ordered a {p} and got a {q}.",
              "Asked for no onions and it came covered in onions.", "{i} missing, and I was still charged for it.",
              "Wrong pizza in the box. Ordered {p}, received {q}.", "Half the order was missing: {i}.",
              "They forgot {i}. Had to call twice to get it sent.", "Got someone else's order completely.",
              "The extra cheese I paid for was not on the pizza.", "Missing {i} for the second order in a row."],
    "cold": ["Pizza arrived cold and the cheese had gone hard.", "Food was lukewarm at best when it reached us.",
             "Cold pizza, soggy box.", "The wings were cold in the middle.",
             "By the time it arrived everything was cold, although the driver was on time.",
             "Collected in store and it was already cold on the rack.", "Lava cake was cold and not molten at all.",
             "The order was sitting on the counter when I arrived to collect, and it was cold."],
    "app": ["Payment was taken twice in the app for one order.", "The app crashed at checkout three times.",
            "Promo code would not apply although it was valid.", "App said the restaurant was closed when it was open.",
            "Could not change the delivery address after ordering.", "Charged, but the order never showed in the app.",
            "The loyalty points from my last order are missing."],
    "praise": ["Fastest delivery I have had, and the driver was polite.",
               "The crew at the counter were friendly and remade my order without any fuss.",
               "Great pizza, hot and exactly as ordered.",
               "The manager called to apologise and sorted it out straight away. Thank you.",
               "Always consistent at this branch.", "Staff were very helpful with a big office order.",
               "Really good doughnuts and quick service."],
    "other": ["The dining area tables were not clean.", "Parking outside the branch is impossible in the evening.",
              "Portion of wedges seems smaller than before.", "Too much sauce on the pizza this time.",
              "Music in the restaurant was too loud.", "The crust was thinner than usual.", "Prices have gone up again.",
              "No napkins or chilli flakes in the bag.", "The box was crushed on one side.",
              "Queue at the counter was long and only one till was open."],
    "harm": ["My son was sick during the night after eating the chicken wings from this order.",
             "I found a piece of hard plastic in the pizza and cut my lip on it.",
             "Two of us had stomach pain and vomiting the next morning after the barbecue chicken pizza.",
             "My daughter has a sesame allergy and reacted after the wrap; nobody told us the sauce had changed.",
             "I burned my hand because the lava cake container split when I opened it.",
             "Felt ill within a few hours of eating the garlic dip.",
             "My husband slipped on the wet floor by the counter and hurt his wrist."],
}
# theme, number of comments, the restaurant that gets about a third of them extra
PLAN = [("late", 78, "R-047"), ("wrong", 52, "R-014"), ("cold", 41, "R-031"), ("app", 24, None), ("praise", 30, None),
        ("other", 28, None), ("harm", 7, None)]
CHANNELS = ["call centre", "app review", "survey", "web form"]
THEME_TOTALS = {theme: n for theme, n, _ in PLAN}


def build_care(today: date) -> dict:
    period = period_of(today)
    rng = random.Random(f"feedback-{period}")
    made = []
    for theme, n, hot in PLAN:
        pool = TEXTS[theme]
        for k in range(n):
            site = hot if (hot and rng.random() < 0.34) else rng.choice(RESTAURANT_IDS)
            p, q = rng.sample(PIZZA, 2)
            text = pool[k % len(pool)].format(m=rng.choice([15, 20, 25, 30, 35, 40, 45, 50, 60]), i=rng.choice(ITEMS), p=p, q=q)
            rating = {"praise": rng.choice([4, 5]), "harm": 1}.get(theme, rng.choice([1, 2, 2, 3]))
            made.append((theme, site, rng.choice(CHANNELS), rating, text))
    rng.shuffle(made)
    days = sorted(rng.randint(1, days_in(period)) for _ in made)
    feedback, themes = {}, {}
    for n, ((theme, site, channel, rating, text), day) in enumerate(zip(made, days), start=1):
        ref = f"GF-{yymm(period)}-{n:04d}"
        feedback[ref] = {"reference": ref, "date": f"{period}-{day:02d}", "site_id": site, "channel": channel,
                         "rating": rating, "comment": text}
        themes[ref] = theme
    return {"guest_feedback": feedback, "feedback_themes": themes, "feedback_analyses": {}}
