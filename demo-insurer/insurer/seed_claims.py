"""Seed data, part 2: loss reports, claims with their documents, checklists, the handling guide and letter templates."""

from __future__ import annotations

from datetime import date

from .seed_policy import d_ago, long_date

CLAIM_TYPES = {
    "motor_own_damage": "Motor: damage to the insured vehicle",
    "motor_theft": "Motor: theft of the insured vehicle",
    "motor_third_party": "Motor: accident involving another party",
    "home_escape_of_water": "Home: escape of water",
    "home_theft": "Home: theft",
    "home_fire": "Home: fire",
}

# For each claim type: the documents the pack must hold, and what each must show to count.
CHECKLISTS = {
    "motor_own_damage": [
        ("claim_form", "Claim form", "Signed and dated by the policyholder."),
        ("driving_licence", "Driving licence of the driver", "Valid on the date of the loss."),
        ("repair_estimate", "Repair estimate", "Names the registration of the insured vehicle."),
        ("photographs", "Photographs of the damage", "Readable."),
    ],
    "motor_theft": [
        ("claim_form", "Claim form", "Signed and dated by the policyholder."),
        ("police_report", "Police report", "Shows the report number and the date it was made."),
        ("vehicle_registration", "Vehicle registration document", "Names the registration of the insured vehicle."),
        ("keys_declaration", "Declaration of the keys held", "Says how many keys exist and where each one is."),
    ],
    "motor_third_party": [
        ("claim_form", "Claim form", "Signed and dated by the policyholder."),
        ("driving_licence", "Driving licence of the driver", "Valid on the date of the loss."),
        ("police_report", "Police report", "Shows the report number and the date it was made."),
        ("third_party_details", "Details of the other party", "Names the other driver and the other vehicle's registration."),
        ("repair_estimate", "Repair estimate", "Names the registration of the insured vehicle."),
        ("photographs", "Photographs of the damage", "Readable."),
    ],
    "home_escape_of_water": [
        ("claim_form", "Claim form", "Signed and dated by the policyholder."),
        ("plumber_report", "Plumber's report", "Says where the water came from and whether it escaped suddenly or over time."),
        ("repair_estimate", "Repair estimate", "Names the insured home."),
        ("photographs", "Photographs of the damage", "Readable."),
    ],
    "home_theft": [
        ("claim_form", "Claim form", "Signed and dated by the policyholder."),
        ("police_report", "Police report", "Shows the report number and the date it was made."),
        ("proof_of_ownership", "Proof of ownership of the items", "A receipt, valuation or photograph for each item claimed."),
    ],
    "home_fire": [
        ("claim_form", "Claim form", "Signed and dated by the policyholder."),
        ("fire_service_report", "Fire service report", "Shows the report number and where the fire started."),
        ("repair_estimate", "Repair estimate", "Names the insured home."),
        ("photographs", "Photographs of the damage", "Readable."),
        ("contents_list", "List of contents damaged", "Each item with its value."),
    ],
}

HANDLING_GUIDE = {
    "guide_id": "TMI-CLM-HG-1", "title": "Claims handling guide", "version": "4",
    "sorting_rules": {
        "how_to_apply": "Apply the rules in order. The first rule that applies gives the track, the team and the severity. "
                        "Give the rule's id with the reason.",
        "rules": [
            {"rule_id": "HG-1", "name": "A person first",
             "applies_when": "The report or the file says a person was injured, or shows that the customer may be vulnerable. "
                             "Signs of a vulnerable customer: aged 75 or over and living alone; forced out of the home by the loss; a recent "
                             "bereavement; a serious illness; the customer says they cannot cope.",
             "track": "person first", "team": "senior adjuster", "severity": "high",
             "what_happens": "A senior adjuster takes the claim the same day and a person calls the customer before anything else is done."},
            {"rule_id": "HG-2", "name": "Complex",
             "applies_when": "The estimate is USD 25,000 or more, or another party is involved, or the policy was not in force on the date of the loss.",
             "track": "complex", "team": "liability team when another party is involved, otherwise senior adjuster",
             "severity": "high when the estimate is USD 25,000 or more, otherwise medium",
             "what_happens": "An adjuster with the authority for the amount takes the claim."},
            {"rule_id": "HG-3", "name": "Fast track",
             "applies_when": "The estimate is under USD 2,500 and every document on the checklist is received and meets what it must show.",
             "track": "fast track", "team": "fast-track team", "severity": "low",
             "what_happens": "A handler settles the claim from the file."},
            {"rule_id": "HG-4", "name": "Standard",
             "applies_when": "No earlier rule applies.",
             "track": "standard", "team": "theft team for a theft of a vehicle, motor team for any other motor claim, property team for a home claim",
             "severity": "medium when the estimate is USD 2,500 or more, otherwise low",
             "what_happens": "A handler in the team takes the claim."},
        ],
    },
    "settlement_authority": {
        "rule_id": "HG-5",
        "text": "A handler approves a settlement up to USD 5,000. A senior adjuster approves a settlement above USD 5,000 and up to USD 25,000. "
                "The claims manager approves a settlement above USD 25,000. Nobody pays a claim that an adjuster has not approved.",
        "levels": [{"up_to": 5000.0, "approver": "handler"}, {"up_to": 25000.0, "approver": "senior adjuster"},
                   {"up_to": None, "approver": "claims manager"}],
    },
    "correspondence_rules": {
        "rule_id": "HG-6",
        "text": "Every letter names the claim by its id. A letter never carries a policy number, a bank account or an identity number. "
                "A letter that declines a claim, in whole or in part, is written only after an adjuster's decision to decline is recorded on the "
                "claim, and it gives the adjuster's reason and the clause exactly as the decision records them. A letter that offers a "
                "settlement is written only after the settlement is approved. A handler reads and sends every letter.",
    },
    "recovery_rule": {
        "rule_id": "HG-7",
        "text": "Where the file names another party whose act may have caused the loss, write the words Recovery possible and name the party "
                "and the document that names them. Where the file names no such party, write No recovery indicated. The recoveries team "
                "decides whether to pursue a recovery. Nobody else contacts the other party or their insurer about it.",
    },
}

LETTER_TEMPLATES = {
    "TPL-ACK": {"template_id": "TPL-ACK", "title": "Acknowledgement of a claim", "use_when": "A claim has been registered.",
                "must_include": ["the claim id", "the date the claim was reported", "what the claim is for, in one sentence",
                                 "the team that is handling it", "that we will write again within 10 working days"],
                "closing_paragraph": "If anything about your claim changes, please tell us and quote your claim id."},
    "TPL-MISSING": {"template_id": "TPL-MISSING", "title": "Request for missing documents",
                    "use_when": "A document on the checklist is missing, cannot be read or does not show what it must show.",
                    "must_include": ["the claim id", "each document needed, by its plain name", "why each one is needed, in a few words",
                                     "that the claim cannot move forward until we have them"],
                    "closing_paragraph": "You can send the documents by post or upload them through your online account. Please quote your claim id."},
    "TPL-DECLINE": {"template_id": "TPL-DECLINE", "title": "Decline of a claim",
                    "use_when": "An adjuster's decision to decline is recorded on the claim.",
                    "must_include": ["the claim id", "that we are not able to pay the claim", "the adjuster's reason",
                                     "the clause of the policy wording, by number and in its own words",
                                     "the paragraph on how to complain, word for word"],
                    "closing_paragraph": "If you think this decision is wrong, you can ask us to look at it again. Write to our Complaints Team "
                                         "within 8 weeks of the date of this letter and quote your claim id. If you are still unhappy after our "
                                         "reply, you can take your complaint to the Meridia Insurance Ombudsman."},
}


def _doc(claim_id, n, doc_type, title, text, received, readable=True, note="", lines=None):
    did = f"DOC-{claim_id[4:]}-{n}"
    doc = {"document_id": did, "claim_id": claim_id, "doc_type": doc_type, "title": title, "received": received,
           "format": "extracted text", "readable": readable, "text": text}
    if note:
        doc["note"] = note
    if lines is not None:
        doc["lines"] = [{"line_id": f"{did}-L{i}", **line} for i, line in enumerate(lines, start=1)]
    return did, doc


def _line(description, category, amount, quantity=None, unit_amount=None):
    row = {"description": description, "category": category, "amount": float(amount)}
    if quantity is not None:
        row["quantity"], row["unit_amount"] = quantity, float(unit_amount)
    return row


def _claim(claim_id, policy_id, claimant, claim_type, loss_ago, reported_ago, estimate, description, today, *, status="new",
           third_party=False, notes=None, decision=None, team=None, driver=None):
    return {"claim_id": claim_id, "policy_id": policy_id, "claimant": claimant, "claim_type": claim_type,
            "claim_type_label": CLAIM_TYPES[claim_type], "status": status, "loss_date": d_ago(today, loss_ago),
            "reported_date": d_ago(today, reported_ago), "estimate": float(estimate), "currency": "USD",
            "third_party_involved": third_party, "description": description, "notes": notes or [], "decision": decision,
            "driver": {"name": driver[0], "date_of_birth": driver[1]} if driver else None,
            "handling_team": team, "team_assigned_by": "Ottilie Marsh, claims handler" if team else None,
            "documents": {}, "triage_drafts": [], "pack_check_drafts": [], "summary_drafts": [], "coverage_check_drafts": [],
            "settlement_drafts": [], "letter_drafts": [], "letters_sent": [], "payments": []}


def build_claims(today: date) -> dict:
    claims = {}

    def add(claim, docs):
        for n, spec in enumerate(docs, start=1):
            doc_type, title, text = spec[:3]
            extra = spec[3] if len(spec) > 3 else {}
            did, doc = _doc(claim["claim_id"], n, doc_type, title, text, claim["reported_date"], **extra)
            claim["documents"][did] = doc
        claims[claim["claim_id"]] = claim
        return claim

    L = lambda ago: long_date(d_ago(today, ago))

    # ---- CLM-4001 motor own damage, complete pack, a line over a limit and a line that is not covered
    add(_claim("CLM-4001", "POL-2001", "Corwin Ashgrove", "motor_own_damage", 9, 6, 2350,
               "Reversing out of the drive at home, the policyholder struck a gate post. The rear bumper and tailgate are dented and "
               "the rear windscreen is cracked. Nobody was hurt and no other vehicle or property of another person was involved.", today, driver=("Corwin Ashgrove", "1982-03-03")),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Corwin Ashgrove\nDriver at the time: Corwin Ashgrove (the policyholder)\nDate of loss: {L(9)}\n"
          "Place: the drive of 14 Larchfield Row, Marlow Reach\nWhat happened: reversing out of the drive I hit the gate post. Rear bumper and "
          f"tailgate dented, rear windscreen cracked.\nAnyone injured: No\nAnother party involved: No\nSigned: C. Ashgrove\nDated: {L(6)}"),
         ("driving_licence", "Driving licence (extract)",
          "DRIVING LICENCE EXTRACT\nName: Corwin Ashgrove\nDate of birth: 3 Mar 1982\nCategories: B\nValid until: 2 Mar 2031"),
         ("repair_estimate", "Repair estimate, Gatewick Body Repairs",
          "GATEWICK BODY REPAIRS, estimate GBR-2281\nVehicle: Tarn Vale 1.6 saloon, registration MR-4417-K\n"
          "1. Rear bumper and tailgate panel repair      1,200.00\n2. Paint and finishing                         450.00\n"
          "3. Rear windscreen replacement                  620.00\n4. Interior valet                                80.00\nTotal 2,350.00 USD",
          {"lines": [_line("Rear bumper and tailgate panel repair", "repair", 1200), _line("Paint and finishing", "repair", 450),
                     _line("Rear windscreen replacement", "windscreen", 620), _line("Interior valet", "cleaning", 80)]}),
         ("photographs", "Photographs of the damage (description)",
          "Four photographs. They show a dented rear bumper and tailgate and a cracked rear windscreen on a saloon with the registration MR-4417-K.")])

    # ---- CLM-4002 home escape of water, the plumber's report is missing and the photographs cannot be read
    add(_claim("CLM-4002", "POL-2002", "Elspeth Marrowdene", "home_escape_of_water", 12, 10, 6400,
               "Water came through the kitchen ceiling. The ceiling, one wall and the kitchen floor are damaged.", today, team="property team"),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Elspeth Marrowdene\nDate of loss: {L(12)}\nPlace: 3 Weavers Yard, Tallowby\n"
          "What happened: I came downstairs and found water coming through the kitchen ceiling. I turned the water off at the main. "
          f"I do not know where it came from.\nAnyone injured: No\nSigned: E. Marrowdene\nDated: {L(10)}"),
         ("repair_estimate", "Repair estimate, Tallowby Building Services",
          "TALLOWBY BUILDING SERVICES, estimate TBS-0907\nProperty: 3 Weavers Yard, Tallowby\n"
          "1. Take down and replace kitchen ceiling      2,900.00\n2. Replaster and redecorate one wall           1,700.00\n"
          "3. Lift and relay kitchen floor                1,800.00\nTotal 6,400.00 USD",
          {"lines": [_line("Take down and replace kitchen ceiling", "repair", 2900), _line("Replaster and redecorate one wall", "repair", 1700),
                     _line("Lift and relay kitchen floor", "repair", 1800)]}),
         ("photographs", "Photographs of the damage", "",
          {"readable": False, "note": "The scan is too dark to read. Nothing can be made out in any of the pictures."})])

    # ---- CLM-4003 motor theft, the loss is two days after the policy period ended
    add(_claim("CLM-4003", "POL-2003", "Dariusz Kellhaven", "motor_theft", 19, 18, 9800,
               "The insured vehicle was taken overnight from the street outside the policyholder's home.", today),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Dariusz Kellhaven\nDate of loss: {L(19)}\nPlace: Saltmarsh Lane, Port Ilvane\n"
          "What happened: I parked the car outside my home in the evening. In the morning it was gone. I have both keys.\n"
          f"Anyone injured: No\nSigned: D. Kellhaven\nDated: {L(18)}"),
         ("police_report", "Police report",
          f"PORT ILVANE POLICE, report number PIP-26-118804\nDate of report: {L(19)}\nReported by: Dariusz Kellhaven\n"
          "Theft of an Orrin Bay 2.0 estate, registration PI-2086-T, from Saltmarsh Lane. No broken glass at the scene. Both keys held by the owner."),
         ("vehicle_registration", "Vehicle registration document (extract)",
          "REGISTRATION EXTRACT\nRegistration: PI-2086-T\nMake and model: Orrin Bay 2.0 estate\nFirst registered: 2019\nKeeper: Dariusz Kellhaven"),
         ("keys_declaration", "Declaration of the keys held",
          "Two keys exist. Both are with me and I have handed both to the handler.\nSigned: D. Kellhaven")])

    # ---- CLM-4004 motor theft with the key left in the vehicle: the wording says nothing about it
    add(_claim("CLM-4004", "POL-2004", "Odalys Fenwright", "motor_theft", 7, 7, 14740,
               "The insured vehicle was driven away from a petrol station forecourt while the policyholder was inside paying. "
               "The key was in the ignition.", today, team="theft team"),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Odalys Fenwright\nDate of loss: {L(7)}\nPlace: Harbour Road petrol station, Port Ilvane\n"
          "What happened: I filled up and went in to pay. I left the key in the ignition. When I came out the car was being driven away.\n"
          f"Anyone injured: No\nSigned: O. Fenwright\nDated: {L(7)}"),
         ("police_report", "Police report",
          f"PORT ILVANE POLICE, report number PIP-26-121377\nDate of report: {L(7)}\nReported by: Odalys Fenwright\n"
          "Theft of a Halden Crest 1.8 hatchback, registration PI-9031-C, from the forecourt of the Harbour Road petrol station. "
          "The owner states the key was in the vehicle. The forecourt camera shows one person entering the vehicle and driving off."),
         ("vehicle_registration", "Vehicle registration document (extract)",
          "REGISTRATION EXTRACT\nRegistration: PI-9031-C\nMake and model: Halden Crest 1.8 hatchback\nFirst registered: 2023\nKeeper: Odalys Fenwright"),
         ("keys_declaration", "Declaration of the keys held",
          "Two keys exist. One is with me. The other was in the vehicle when it was taken.\nSigned: O. Fenwright"),
         ("valuation", "Valuation and hire car invoice",
          "MERIDIA MOTOR VALUERS, valuation MMV-5530\nHalden Crest 1.8 hatchback, 2023, registration PI-9031-C\n"
          f"Market value on {L(7)}: 14,200.00 USD\n\nPORTSIDE CAR HIRE, invoice PCH-7719\nHire car, 12 days at 45.00 a day: 540.00 USD",
          {"lines": [_line("Market value of the insured vehicle at the date of the loss", "vehicle", 14200),
                     _line("Hire car, 12 days at 45.00 a day", "hire_car", 540, quantity=12, unit_amount=45)]})])

    # ---- CLM-4005 motor accident with another party, a passenger hurt, no police report, an estimate for another registration
    add(_claim("CLM-4005", "POL-2005", "Bram Tollermoor", "motor_third_party", 5, 4, 7900,
               "The insured vehicle and another car collided at the junction of Quarry Bank and Mill Road. The policyholder's passenger "
               "was taken to hospital with neck pain. Both vehicles are damaged.", today, driver=("Bram Tollermoor", "1990-08-19"), third_party=True),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Bram Tollermoor\nDriver at the time: Bram Tollermoor (the policyholder)\nDate of loss: {L(5)}\n"
          "Place: junction of Quarry Bank and Mill Road, Marlow Reach\nWhat happened: a car came out of Mill Road and we collided. "
          "My passenger, Petra Tollermoor, was taken to hospital with neck pain.\nAnyone injured: Yes, one passenger\n"
          f"Another party involved: Yes\nSigned: B. Tollermoor\nDated: {L(4)}"),
         ("driving_licence", "Driving licence (extract)",
          "DRIVING LICENCE EXTRACT\nName: Bram Tollermoor\nDate of birth: 19 Aug 1990\nCategories: B\nValid until: 18 Aug 2029"),
         ("third_party_details", "Details of the other party",
          "Other driver: Sorrel Mackinder. Other vehicle: Orrin Bay 1.6 saloon, registration MR-1193-F. Damage to the front left wing and door."),
         ("repair_estimate", "Repair estimate, Quarry Road Motors",
          "QUARRY ROAD MOTORS, estimate QRM-4410\nVehicle: Vesper Lane 1.4 hatchback, registration MR-7702-B\n"
          "1. Front bumper, bonnet and right wing        5,600.00\n2. Headlamp unit and radiator                  2,300.00\nTotal 7,900.00 USD",
          {"lines": [_line("Front bumper, bonnet and right wing", "repair", 5600), _line("Headlamp unit and radiator", "repair", 2300)]}),
         ("photographs", "Photographs of the damage (description)",
          "Six photographs. They show front-end damage to a hatchback with the registration MR-7720-B, and damage to the left side of a saloon.")])

    # ---- CLM-4006 home theft with no forced entry, one item above the single item limit
    add(_claim("CLM-4006", "POL-2006", "Henrietta Quillby", "home_theft", 15, 14, 5500,
               "Items were taken from the home during the afternoon while the policyholder was out. The back door had been left unlocked.", today, team="property team"),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Henrietta Quillby\nDate of loss: {L(15)}\nPlace: 61 Thistledown Close, Tallowby\n"
          "What happened: I went out for the afternoon and left the back door unlocked. When I came back a watch, a laptop and some cash had gone.\n"
          f"Items claimed: watch 4,000.00; laptop 1,300.00; cash 200.00\nSigned: H. Quillby\nDated: {L(14)}"),
         ("police_report", "Police report",
          f"TALLOWBY POLICE, report number TBP-26-044519\nDate of report: {L(15)}\nReported by: Henrietta Quillby\n"
          "Theft from a dwelling at 61 Thistledown Close. Entry was by the back door, which the occupier states was unlocked. "
          "There is no sign of forced entry at any door or window."),
         ("proof_of_ownership", "Receipts",
          "Receipt, Tallowby Jewellers: one wristwatch, 4,000.00 USD. Receipt, Marlow Computers: one laptop, 1,300.00 USD. No receipt for the cash.",
          {"lines": [_line("Wristwatch", "contents_item", 4000), _line("Laptop", "contents_item", 1300), _line("Cash", "contents_item", 200)]})])

    # ---- CLM-4007 home fire, large, an older customer forced out of the home, two documents that disagree
    add(_claim("CLM-4007", "POL-2007", "Aldous Pennicott", "home_fire", 3, 3, 62000,
               "A fire damaged the kitchen and the utility room and left smoke damage through the ground floor. The home cannot be lived in.", today,
               notes=[{"date": d_ago(today, 3), "by": "First contact team",
                       "text": "Mr Pennicott is 81 and lives alone. He is staying with a neighbour and says he does not know how long he can stay there."}]),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Aldous Pennicott\nDate of loss: {L(3)}\nPlace: 9 Ferrymans Walk, Port Ilvane\n"
          "What happened: the fire started at the cooker in the kitchen while I was in the garden. The fire service put it out.\n"
          f"Anyone injured: No\nSigned: A. Pennicott\nDated: {L(3)}"),
         ("fire_service_report", "Fire service report",
          f"PORT ILVANE FIRE SERVICE, report number PIF-26-00713\nDate: {L(3)}\nAddress: 9 Ferrymans Walk\n"
          "Origin of the fire: the tumble dryer in the utility room. The fire spread to the kitchen through the connecting door. "
          "No person injured. The ground floor is not fit to live in until made safe."),
         ("repair_estimate", "Repair estimate, Ilvane Restoration",
          "ILVANE RESTORATION, estimate IR-3306\nProperty: 9 Ferrymans Walk, Port Ilvane\n"
          "1. Strip out and rebuild kitchen and utility room   41,500.00\n2. Electrical rewiring, ground floor                 9,800.00\n"
          "3. Smoke cleaning and redecoration, ground floor    10,700.00\nTotal 62,000.00 USD",
          {"lines": [_line("Strip out and rebuild kitchen and utility room", "repair", 41500),
                     _line("Electrical rewiring, ground floor", "repair", 9800),
                     _line("Smoke cleaning and redecoration, ground floor", "repair", 10700)]}),
         ("photographs", "Photographs of the damage (description)",
          "Nine photographs. They show a burnt-out utility room, a fire-damaged kitchen and smoke marks on the walls of the hall and living room.")])

    # ---- CLM-4008 motor own damage, the driver is not a named driver and the policy has a named drivers endorsement
    add(_claim("CLM-4008", "POL-2008", "Marisol Underhay", "motor_own_damage", 8, 6, 3100,
               "The insured vehicle left the road on a bend and struck a fence. The front bumper, a wing and a headlamp are damaged. "
               "The driver was the policyholder's son. Nobody was hurt.", today, driver=("Leander Underhay", "2007-06-11")),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Marisol Underhay\nDriver at the time: Leander Underhay (the policyholder's son)\nDate of loss: {L(8)}\n"
          "Place: Hollow Lane, near Marlow Reach\nWhat happened: my son took the bend too fast, the car left the road and hit a fence.\n"
          f"Anyone injured: No\nAnother party involved: No\nSigned: M. Underhay\nDated: {L(6)}"),
         ("driving_licence", "Driving licence (extract)",
          "DRIVING LICENCE EXTRACT\nName: Leander Underhay\nDate of birth: 11 Jun 2007\nCategories: B\nValid until: 10 Jun 2035"),
         ("repair_estimate", "Repair estimate, Gatewick Body Repairs",
          "GATEWICK BODY REPAIRS, estimate GBR-2297\nVehicle: Tarn Vale 1.2 hatchback, registration MR-3358-D\n"
          "1. Front bumper and left wing                 2,250.00\n2. Headlamp unit                                 850.00\nTotal 3,100.00 USD",
          {"lines": [_line("Front bumper and left wing", "repair", 2250), _line("Headlamp unit", "repair", 850)]}),
         ("photographs", "Photographs of the damage (description)",
          "Three photographs. They show front-end damage to a hatchback with the registration MR-3358-D.")])

    # ---- CLM-4009 home escape of water, cover accepted by an adjuster, ready for the settlement to be worked out
    add(_claim("CLM-4009", "POL-2009", "Teodor Brackwell", "home_escape_of_water", 30, 29, 8400,
               "A joint on the supply pipe under the hall floor failed. Water damaged the hall floor and the carpet.", today, team="property team", status="in_assessment",
               decision={"decision": "cover_accepted", "decided_by": "Fenella Arkwright", "role": "adjuster", "decided_on": d_ago(today, 20),
                         "reason": "Sudden failure of a joint on a fixed supply pipe, as the plumber's report says.", "clause": "1.3"}),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Teodor Brackwell\nDate of loss: {L(30)}\nPlace: 12 Millpond Court, Tallowby\n"
          f"What happened: the hall floor was suddenly wet. A plumber found a failed joint under the floor.\nSigned: T. Brackwell\nDated: {L(29)}"),
         ("plumber_report", "Plumber's report",
          f"MILLPOND PLUMBING, report MP-1184, {L(29)}\nA compression joint on the 15 mm supply pipe under the hall floor had failed. "
          "The failure was sudden: the pipe and the joint show no corrosion and the timber around it was dry apart from the fresh leak."),
         ("repair_estimate", "Invoices",
          "MILLPOND PLUMBING, invoice MP-1191\n1. Lifting the hall floor to find the leak, and making good     1,900.00\n"
          "2. Repair of the pipe and relaying the hall floor                3,200.00\n\nTALLOWBY FLOORING, invoice TF-2204\n"
          "3. Replacement hall carpet                                         900.00\n4. Underfloor heating, supplied and fitted (new)                2,400.00\n"
          "Total of both invoices 8,400.00 USD\nProperty: 12 Millpond Court, Tallowby",
          {"lines": [_line("Lifting the hall floor to find the leak, and making good", "trace_and_access", 1900),
                     _line("Repair of the pipe and relaying the hall floor", "repair", 3200),
                     _line("Replacement hall carpet", "contents_item", 900),
                     _line("Underfloor heating, supplied and fitted (new)", "improvement", 2400)]}),
         ("photographs", "Photographs of the damage (description)",
          "Five photographs. They show a lifted hall floor, a failed pipe joint and a stained carpet.")])

    # ---- CLM-4010 home escape of water, declined by an adjuster: the home had been unoccupied for 74 days
    add(_claim("CLM-4010", "POL-2010", "Yvaine Corrimond", "home_escape_of_water", 16, 13, 11200,
               "A pipe in the loft burst while the home was empty. Water damaged two bedrooms and the stairs.", today, team="property team", status="decided",
               notes=[{"date": d_ago(today, 9), "by": "Fenella Arkwright",
                       "text": "The policyholder confirms she was working abroad and the home had been empty for 74 days in a row when the pipe burst."}],
               decision={"decision": "declined", "decided_by": "Fenella Arkwright", "role": "adjuster", "decided_on": d_ago(today, 6),
                         "reason": "The home had been unoccupied for 74 days in a row when the loss happened.", "clause": "2.2"}),
        [("claim_form", "Claim form",
          f"CLAIM FORM\nPolicyholder: Yvaine Corrimond\nDate of loss: {L(16)}\nPlace: 2 Heron Wharf, Port Ilvane\n"
          "What happened: a neighbour saw water running under the front door. A pipe in the loft had burst. I was abroad for work.\n"
          f"Signed: Y. Corrimond\nDated: {L(13)}"),
         ("plumber_report", "Plumber's report",
          f"HERON PLUMBING, report HP-0672, {L(14)}\nA 22 mm pipe in the loft had split along its length. The split is fresh. The heating was off."),
         ("repair_estimate", "Repair estimate, Ilvane Restoration",
          "ILVANE RESTORATION, estimate IR-3291\nProperty: 2 Heron Wharf, Port Ilvane\n1. Two bedroom ceilings and walls     7,400.00\n"
          "2. Stair carpet and decoration        3,800.00\nTotal 11,200.00 USD",
          {"lines": [_line("Two bedroom ceilings and walls", "repair", 7400), _line("Stair carpet and decoration", "repair", 3800)]}),
         ("photographs", "Photographs of the damage (description)", "Four photographs. They show water-stained ceilings in two bedrooms and a soaked stair carpet.")])
    return claims


def build_loss_reports(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))

    def report(rid, channel, received_ago, reporter, policy_number_given, text):
        return {"loss_report_id": rid, "status": "new", "channel": channel, "received": d_ago(today, received_ago), "reporter": reporter,
                "policy_number_given": policy_number_given, "text": text, "claim_file_drafts": [], "claim_id": None}

    rows = [
        report("LR-3001", "web form", 0, "Isaura Venn", "POL-2011",
               f"Policy number POL-2011. On {L(1)} at about 18:30, in the car park of the Marlow Reach retail park, I reversed my Halden Crest "
               "(registration MR-6104-H) into a concrete bollard. The rear bumper is cracked and a rear light is broken. I was alone in the car, "
               "nobody was hurt and no other vehicle was involved. I can be reached on the number on my policy."),
        report("LR-3002", "email", 1, "Elric Stannaway", "POL-2021",
               "Dear Thornmere, my policy number is POL-2021. We have had a leak at home, 7 Otterburn Gardens in Tallowby. Water has come "
               "through the ceiling of the dining room from the bathroom above and the ceiling has partly come down. Nobody was hurt. "
               "Please tell me what you need from me. Regards, Elric Stannaway"),
        report("LR-3003", "telephone note", 1, "Ludovic Harrowell", "POL-2013",
               f"Call taken by the first contact team. Mr Harrowell, policy POL-2013, reports that on {L(2)} his Orrin Bay (registration PI-5570-M) "
               "was hit while parked in Tanners Row, Port Ilvane. The driver's door and the front wing are dented. He did not see who did it. "
               "Nobody was hurt."),
        report("LR-3004", "web form", 0, "Ansel Whitlocke", "POL-2014",
               f"Policy POL-2014. On {L(1)} at about 08:10 on the Beacon Hill roundabout in Marlow Reach, a van ran into the back of my "
               "Vesper Lane estate (registration MR-8842-P). My wife, Corisande Whitlocke, was in the passenger seat and was taken to hospital "
               "by ambulance with back pain. The van was a white Orrin Bay van, registration PI-4471-V, driven by a Mr Tobin Halewood. "
               "The rear of my car is badly damaged."),
    ]
    return {r["loss_report_id"]: r for r in rows}
