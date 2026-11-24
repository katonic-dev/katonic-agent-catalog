"""Version 1.3: one valid call for each operation of the catalogue, stock, pricing and loyalty systems.

test_operations.py adds them to its table so that every operation of the service is called once, in an order in
which each change comes after the draft it needs. test_version_1_3.py uses the same bodies.
"""

PERIOD = "2026-10"

DESCRIPTION = {
    "description": "Oat granola from Rowanmere in a 500 g bag. Clusters of baked oats are mixed with whole almonds and "
                   "sunflower seeds. Serve it in a bowl with milk or yoghurt, or eat it by the handful. Store the bag in a "
                   "cool, dry place and close it after opening. This text was written from the photo studio's words about "
                   "the pictures.",
    "image_tags": ["granola", "oat clusters", "almonds", "bowl"],
    "net_quantity": "500 g", "pack_size": "1", "allergen_statement": "Contains: oats, almonds (nuts)",
    "country_of_origin": "Meridia", "differences_for_the_content_lead": [], "drafted_by": "a test"}
DATA_CHECK = {"findings": [{"sku": "AG-4407", "attribute": "net_quantity", "kind": "does_not_match", "listing_value": "1 kg",
                            "specification_value": "900 g"},
                           {"sku": "CH-5506", "attribute": "allergen_statement", "kind": "missing", "listing_value": "",
                            "specification_value": "Contains: milk"}], "drafted_by": "a test"}
TERMS = {"groups": [{"name": "Milk made from plants", "what_shoppers_seemed_to_want": "A milk that is not from a cow.",
                     "terms": ["oat milk", "almond milk", "soya milk", "oat drink"]}], "drafted_by": "a test"}
PLAN = {"lines": [{"sku": "CH-5502", "supplier_id": "SUP-301", "cases": 87, "reason": "300 on hand, 2.5 days of cover, 3 days to the next delivery."},
                  {"sku": "CH-5505", "supplier_id": "SUP-301", "cases": 73, "reason": "150 on hand, 2.5 days of cover."},
                  {"sku": "AG-4408", "supplier_id": "SUP-303", "cases": 75, "reason": "200 on hand, 4.0 days of cover."},
                  {"sku": "FP-5801", "supplier_id": "SUP-304", "cases": 75, "reason": "180 on hand, 2.0 days of cover."},
                  {"sku": "FP-5802", "supplier_id": "SUP-304", "cases": 145, "reason": "120 on hand, 1.5 days of cover."}],
        "overstocked": ["DR-5904", "FZ-5604", "HH-6105"], "drafted_by": "a test"}
SHRINK = {"stores_beyond_tolerance": [{"site_id": "S-103", "loss_percent": 2.44}, {"site_id": "S-106", "loss_percent": 2.50}],
          "lines_beyond_tolerance": [{"sku": "DR-5905", "loss_percent": 6.68}, {"sku": "HH-6105", "loss_percent": 5.81},
                                     {"sku": "PC-6604", "loss_percent": 5.48}], "drafted_by": "a test"}
PACK = {"stores": [{"site_id": "S-101", "units_delivered": 240}, {"site_id": "S-104", "units_delivered": 180},
                   {"site_id": "S-105", "units_delivered": 60}, {"site_id": "S-107", "units_delivered": 200}],
        "orders": ["RM-58115", "RM-58121", "RM-58147", "RM-58152", "RM-58160", "RM-58168", "RM-58180"],
        "store_instruction": "Take every unit of Pasta sauce, six jars, batch BT-44031, best before 2027-09-20, off sale now.",
        "customer_notice": "Please do not use Pasta sauce, six jars, from batch BT-44031, best before 2027-09-20.",
        "drafted_by": "a test"}
PRICES = {"recommendations": [
    {"sku": "DR-5901", "action": "decrease", "current_price": 2.69, "proposed_price": 2.49, "reason": "8.0 percent above 2.49."},
    {"sku": "HH-6102", "action": "decrease", "current_price": 8.99, "proposed_price": 8.49, "reason": "5.9 percent above 8.49."},
    {"sku": "FP-5804", "action": "increase", "current_price": 1.15, "proposed_price": 1.25, "reason": "8.0 percent below 1.25."},
    {"sku": "BK-5701", "action": "hold", "current_price": 1.59, "reason": "1.49 would leave 13.6 percent.", "rule": "PR-1"},
    {"sku": "PC-6604", "action": "hold", "current_price": 9.99, "reason": "A move of 15.0 percent.", "rule": "PR-3"},
    {"sku": "CH-5502", "action": "hold", "current_price": 2.49, "reason": "2.5 days of cover.", "rule": "PR-4"},
    {"sku": "HH-6103", "action": "hold", "current_price": 2.19, "reason": "A move of 13.7 percent.", "rule": "PR-3"}],
    "drafted_by": "a test"}
REVIEW = {"units_sold": 640, "units_planned": 600, "displaced": [{"sku": "BK-5705", "units_lost": 160}, {"sku": "BK-5702", "units_lost": 10}],
          "net_effect_on_profit": -262.00, "findings": ["Fruit scones fell from 350 units to 190."], "drafted_by": "a test"}
RANGE_PACK = {"lines_below_thresholds": [{"sku": "HH-6105", "thresholds": ["RT-1"]}, {"sku": "HH-6106", "thresholds": ["RT-1"]}],
              "drafted_by": "a test"}
DEMAND_NOTE = {"from_the_records": [{"sku": "FZ-5603", "statement": "Rose from 140.0 to 210.0 units a week, 50.0 percent."}],
               "from_the_market_notes": [{"note_id": "MN-02", "statement": "The trade paper says frozen ready meals fell 8 percent.",
                                          "in_writing": True}],
               "forecasts": [{"sku": "FZ-5603", "statement": "Forecast: 210 units a week for the next four weeks, the last four weeks' average."}],
               "points_for_the_buyer": ["The records and MN-02 disagree on frozen ready meals."], "drafted_by": "a test"}
SUGGESTIONS = {"suggestions": [{"sku": "AG-4412", "reason": "Viewed 4 times in the last 30 days."},
                               {"sku": "CH-5506", "reason": "Viewed 3 times in the last 30 days."},
                               {"sku": "BK-5705", "reason": "Viewed once in the last 30 days."}],
               "blocked": [{"sku": "DR-5905", "rule": "PZ-2"}, {"sku": "DR-5907", "rule": "PZ-2"}], "drafted_by": "a test"}
BRIEF = {"title": "Winter warmers", "objective": "Sell 40,000 dollars of soup and bakery lines by 2026-12-14.",
         "audience": {"segment": "All members opted in to marketing email", "size": 27300,
                      "consent_basis": "marketing_email_opt_in", "adults_only": False},
         "offer": "20 percent off chilled soup and two bakery lines for two weeks.", "includes_age_restricted_lines": False,
         "channels": ["email", "in_store"], "start_date": "2026-12-01", "end_date": "2026-12-14", "budget": 9500.0,
         "measures_of_success": ["Redemptions: 2,800", "Sales: 40,000.00"],
         "last_year": {"campaign_id": "CP-2505", "what_it_showed": "Sent to 21,400, 2,568 redemptions, sales 37,800.00, cost 9,000.00, 4.2 for each dollar."},
         "rules_and_risks": ["Only members opted in to marketing email are contacted."], "open_points": [], "drafted_by": "a test"}

CALLS_1_3 = {
    # catalogue
    "list_product_listings": ("get", "/catalogue/listings", None),
    "get_product_listing": ("get", "/catalogue/listings/AG-4407", None),
    "get_supplier_specification": ("get", "/catalogue/specifications/AG-4407", None),
    "get_product_style_guide": ("get", "/catalogue/style-guide", None),
    "list_new_products": ("get", "/catalogue/new-products", None),
    "save_product_description": ("post", "/catalogue/listings/AG-4411/description", DESCRIPTION),
    "publish_product_description": ("post", "/catalogue/listings/AG-4411/description/publish", {"published_by": "I. Editor"}),
    "get_product_data_checks": ("get", "/catalogue/data-checks", None),
    "save_product_data_check": ("post", "/catalogue/data-checks", DATA_CHECK),
    "get_search_log": ("get", f"/catalogue/search-log/{PERIOD}", None),
    "get_search_terms_analysis": ("get", f"/catalogue/search-log/{PERIOD}/analysis", None),
    "save_search_terms_analysis": ("post", f"/catalogue/search-log/{PERIOD}/analysis", TERMS),
    # stock
    "list_stock_levels": ("get", "/stock/levels", None),
    "get_line_stock_history": ("get", "/stock/levels/CH-5502", None),
    "get_replenishment_rules": ("get", "/stock/replenishment-rules", None),
    "list_supply_terms": ("get", "/stock/supply-terms", None),
    "get_replenishment_plan": ("get", "/stock/replenishment-plan", None),
    "save_replenishment_plan": ("post", "/stock/replenishment-plan", PLAN),
    "approve_replenishment_plan": ("post", "/stock/replenishment-plan/approve", {"approved_by": "J. Buyer"}),
    "list_stock_counts": ("get", f"/stock/counts/{PERIOD}", None),
    "get_shrink_tolerance": ("get", "/stock/shrink-tolerance", None),
    "get_shrink_analysis": ("get", f"/stock/counts/{PERIOD}/analysis", None),
    "save_shrink_analysis": ("post", f"/stock/counts/{PERIOD}/analysis", SHRINK),
    "list_batches": ("get", "/stock/batches", None),
    "get_batch_trace": ("get", "/stock/batches/BT-44031", None),
    "save_recall_pack": ("post", "/stock/batches/BT-44031/recall-pack", PACK),
    "issue_recall_notice": ("post", "/stock/batches/BT-44031/recall-notice/issue", {"issued_by": "K. Quality"}),
    # pricing
    "list_prices": ("get", "/pricing/prices", None),
    "list_competitor_prices": ("get", "/pricing/competitor-prices", None),
    "get_pricing_rules": ("get", "/pricing/rules", None),
    "get_price_recommendations": ("get", "/pricing/recommendations", None),
    "save_price_recommendations": ("post", "/pricing/recommendations", PRICES),
    "approve_price_changes": ("post", "/pricing/recommendations/approve", {"approved_by": "L. Merchant"}),
    "list_promotions": ("get", "/pricing/promotions", None),
    "get_promotion": ("get", "/pricing/promotions/PM-3102", None),
    "save_promotion_review": ("post", "/pricing/promotions/PM-3102/review", REVIEW),
    "get_range_review_thresholds": ("get", "/pricing/range-review/thresholds", None),
    "get_range_review_data": ("get", "/pricing/range-review/household", None),
    "save_range_review_pack": ("post", "/pricing/range-review/household/pack", RANGE_PACK),
    "list_line_sales_history": ("get", "/pricing/sales-history", None),
    "get_market_notes": ("get", "/pricing/market-notes", None),
    "get_demand_plan_notes": ("get", "/pricing/demand-plan-notes", None),
    "save_demand_plan_note": ("post", "/pricing/demand-plan-notes", DEMAND_NOTE),
    # loyalty
    "list_members": ("get", "/loyalty/members", None),
    "get_member": ("get", "/loyalty/members/LM-2011", None),
    "get_personalisation_rules": ("get", "/loyalty/personalisation-rules", None),
    "save_product_suggestions": ("post", "/loyalty/members/LM-2011/suggestions", SUGGESTIONS),
    "get_loyalty_programme_summary": ("get", "/loyalty/programme", None),
    "list_past_campaigns": ("get", "/loyalty/campaigns", None),
    "get_past_campaign": ("get", "/loyalty/campaigns/CP-2505", None),
    "get_campaign_brief_template": ("get", "/loyalty/brief-template", None),
    "list_campaign_briefs": ("get", "/loyalty/briefs", None),
    "save_campaign_brief": ("post", "/loyalty/briefs", BRIEF),
}
