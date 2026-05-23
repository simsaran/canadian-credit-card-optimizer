import csv
import random
from datetime import date, timedelta

random.seed(42)

# ── CLASSIFICATION TAXONOMY ───────────────────────────────────────────────────
PRODUCT_CATEGORIES = [
    "Dairy and Eggs",
    "Meat and Poultry",
    "Seafood",
    "Bakery and Snacks",
    "Fruits and Vegetables",
    "Beverages",
    "Prepared and Packaged Foods",
    "Dietary Supplements",
    "Pharmaceuticals",
    "Medical Devices",
    "Cosmetics and Personal Care",
    "Infant Formula and Baby Food",
]

ROOT_CAUSES = [
    "Undeclared allergen",
    "Microbiological contamination",
    "Labelling error",
    "Foreign material",
    "Chemical contamination",
    "Process deviation",
    "Packaging failure",
    "Mislabelling of ingredients",
    "Undeclared sulphites",
    "Undeclared gluten",
]

# Realistic weights per product category
CATEGORY_ROOT_CAUSE_WEIGHTS = {
    "Dairy and Eggs": [15, 25, 15, 5, 5, 15, 10, 5, 5, 0],
    "Meat and Poultry": [10, 35, 10, 10, 5, 20, 5, 5, 0, 0],
    "Seafood": [5, 30, 15, 10, 10, 15, 10, 5, 0, 0],
    "Bakery and Snacks": [30, 5, 20, 10, 5, 10, 10, 5, 5, 0],
    "Fruits and Vegetables": [5, 20, 15, 15, 15, 15, 10, 5, 0, 0],
    "Beverages": [10, 10, 20, 5, 10, 15, 20, 5, 5, 0],
    "Prepared and Packaged Foods": [25, 15, 20, 10, 5, 10, 10, 5, 0, 0],
    "Dietary Supplements": [10, 5, 25, 5, 15, 20, 5, 10, 5, 0],
    "Pharmaceuticals": [5, 10, 25, 5, 20, 20, 5, 5, 5, 0],
    "Medical Devices": [0, 5, 20, 20, 10, 25, 15, 5, 0, 0],
    "Cosmetics and Personal Care": [5, 15, 25, 10, 20, 15, 5, 5, 0, 0],
    "Infant Formula and Baby Food": [15, 20, 20, 5, 10, 15, 10, 5, 0, 0],
}

RECALL_CLASSES = {
    "Class I":   ("Serious health risk or death", 3, 0.35),
    "Class II":  ("Temporary adverse health consequences unlikely to be serious", 2, 0.45),
    "Class III": ("Unlikely to cause adverse health consequences", 1, 0.20),
}

PROVINCES = [
    "Ontario", "Quebec", "British Columbia", "Alberta",
    "Saskatchewan", "Manitoba", "Nova Scotia",
    "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island",
    "Northwest Territories", "Yukon", "Nunavut", "National",
]

PROVINCE_WEIGHTS = [30, 22, 15, 12, 4, 4, 3, 3, 2, 1, 1, 1, 1, 1]

COMPANIES = {
    "Dairy and Eggs": ["Saputo Inc.", "Lactalis Canada", "Gay Lea Foods", "Parmalat Canada", "Organic Meadow"],
    "Meat and Poultry": ["Maple Leaf Foods", "Olymel", "HFS Canada", "Better Beef", "Sun Rise Poultry"],
    "Seafood": ["High Liner Foods", "Ocean Choice International", "Clearwater Seafoods", "Pacific Seafood", "True North Salmon"],
    "Bakery and Snacks": ["Canada Bread", "Dare Foods", "Voortman Cookies", "Leclerc Group", "Frito-Lay Canada"],
    "Fruits and Vegetables": ["Naturipe", "Sun Belle Inc.", "Pacific Coast Fruit", "Lakeside Produce", "Mucci Farms"],
    "Beverages": ["Sleeman Breweries", "Lassonde Industries", "Cott Beverages", "Andrew Peller", "Clearly Canadian"],
    "Prepared and Packaged Foods": ["McCain Foods", "Bonduelle Americas", "Cavendish Farms", "Conagra Brands Canada", "General Mills Canada"],
    "Dietary Supplements": ["Jamieson Wellness", "Atrium Innovations", "Naturo Sciences", "CanPrev Natural Health", "Organika"],
    "Pharmaceuticals": ["Apotex Inc.", "Teva Canada", "Pharmavite", "Paladin Labs", "Pendopharm"],
    "Medical Devices": ["Medtronic Canada", "Becton Dickinson Canada", "Cardinal Health Canada", "Stryker Canada", "Baxter Canada"],
    "Cosmetics and Personal Care": ["Coty Canada", "L'Oreal Canada", "Reckitt Canada", "Procter and Gamble Canada", "Unilever Canada"],
    "Infant Formula and Baby Food": ["Mead Johnson Canada", "Nestle Canada", "Abbott Nutrition Canada", "Gerber Canada", "Heinz Canada"],
}

DESCRIPTION_TEMPLATES = {
    "Undeclared allergen": [
        "{company} is recalling {product} due to undeclared {allergen}. People with an allergy to {allergen} should not consume this product.",
        "Recall of {product} by {company} because the product may contain undeclared {allergen} which is not declared on the label.",
        "{company} is conducting a voluntary recall of {product} due to the possible presence of undeclared {allergen}.",
    ],
    "Microbiological contamination": [
        "{company} is recalling {product} due to possible {pathogen} contamination.",
        "Recall of {product} because of potential contamination with {pathogen}. Consumers should not consume this product.",
        "{company} is recalling certain lots of {product} due to possible {pathogen} contamination detected during routine testing.",
    ],
    "Labelling error": [
        "{company} is recalling {product} due to a labelling error. The label does not accurately reflect the contents of the package.",
        "Recall of {product} by {company} because the product label contains incorrect information regarding {label_issue}.",
        "{company} is recalling {product} because the product was labelled with incorrect {label_issue} information.",
    ],
    "Foreign material": [
        "{company} is recalling {product} due to the possible presence of {foreign_material}.",
        "Recall of {product} because the product may contain pieces of {foreign_material} which were not intended to be in the product.",
        "{company} is recalling {product} after foreign material ({foreign_material}) was found during production.",
    ],
    "Chemical contamination": [
        "{company} is recalling {product} due to elevated levels of {chemical}.",
        "Recall of {product} by {company} because the product may contain {chemical} at levels that exceed Health Canada guidelines.",
        "{company} is recalling {product} due to the presence of {chemical} contamination.",
    ],
    "Process deviation": [
        "{company} is recalling {product} because the product was not processed in accordance with approved manufacturing procedures.",
        "Recall of {product} due to a process deviation during manufacturing that may affect product safety.",
        "{company} is recalling {product} because a deviation from standard manufacturing practice occurred during production.",
    ],
    "Packaging failure": [
        "{company} is recalling {product} due to a packaging defect that may compromise product integrity.",
        "Recall of {product} because of a seal failure that may allow contamination of the product.",
        "{company} is recalling {product} because the packaging may be compromised, potentially affecting product safety.",
    ],
    "Mislabelling of ingredients": [
        "{company} is recalling {product} because the ingredient list on the label does not accurately reflect the product formulation.",
        "Recall of {product} due to incorrect ingredient declaration on the label.",
        "{company} is recalling {product} because the product contains ingredients not listed on the label.",
    ],
    "Undeclared sulphites": [
        "{company} is recalling {product} due to undeclared sulphites. People with sensitivity to sulphites should not consume this product.",
        "Recall of {product} because the product may contain undeclared sulphites which are not declared on the label.",
        "{company} is conducting a voluntary recall of {product} due to possible undeclared sulphites.",
    ],
    "Undeclared gluten": [
        "{company} is recalling {product} due to undeclared gluten. People with celiac disease or gluten sensitivity should not consume this product.",
        "Recall of {product} because the product may contain undeclared gluten not declared on the label.",
        "{company} is recalling {product} due to the possible presence of undeclared gluten.",
    ],
}

ALLERGENS = ["peanuts", "tree nuts", "milk", "eggs", "wheat", "soy", "sesame", "mustard", "fish", "shellfish"]
PATHOGENS = ["Listeria monocytogenes", "Salmonella", "E. coli O157:H7", "Staphylococcus aureus", "Clostridium perfringens"]
LABEL_ISSUES = ["expiry date", "net weight", "nutritional information", "serving size", "storage instructions"]
FOREIGN_MATERIALS = ["metal fragments", "plastic pieces", "glass shards", "rubber pieces", "wood splinters"]
CHEMICALS = ["pesticide residues", "lead", "cadmium", "benzene", "mineral oil"]

PRODUCTS = {
    "Dairy and Eggs": ["Cheddar Cheese", "Greek Yogurt", "Whole Milk", "Cream Cheese", "Butter", "Brie", "Egg Product", "Sour Cream"],
    "Meat and Poultry": ["Ground Beef", "Chicken Breast", "Sliced Ham", "Turkey Cold Cuts", "Beef Patties", "Pork Sausage", "Chicken Wings"],
    "Seafood": ["Atlantic Salmon", "Shrimp", "Tuna", "Cod Fillets", "Smoked Salmon", "Crab Cakes", "Fish and Chips"],
    "Bakery and Snacks": ["Whole Wheat Bread", "Granola Bars", "Crackers", "Muffins", "Cookies", "Pretzels", "Potato Chips"],
    "Fruits and Vegetables": ["Romaine Lettuce", "Spinach", "Strawberries", "Cherry Tomatoes", "Bean Sprouts", "Cucumber", "Bagged Salad"],
    "Beverages": ["Apple Juice", "Orange Juice", "Kombucha", "Sparkling Water", "Energy Drink", "Smoothie", "Craft Beer"],
    "Prepared and Packaged Foods": ["Frozen Lasagna", "Chicken Soup", "Mac and Cheese", "Frozen Pizza", "Ready Meal", "Pasta Sauce", "Hummus"],
    "Dietary Supplements": ["Vitamin D Capsules", "Fish Oil", "Probiotic", "Multivitamin", "Protein Powder", "Magnesium", "Collagen"],
    "Pharmaceuticals": ["Ibuprofen Tablets", "Acetaminophen", "Antibiotic Capsules", "Antacid", "Cough Syrup", "Eye Drops", "Nasal Spray"],
    "Medical Devices": ["Blood Glucose Monitor", "Insulin Pump", "Surgical Mask", "Thermometer", "Blood Pressure Cuff", "Infusion Pump"],
    "Cosmetics and Personal Care": ["Face Cream", "Shampoo", "Sunscreen", "Lip Balm", "Body Lotion", "Mascara", "Hair Dye"],
    "Infant Formula and Baby Food": ["Infant Formula", "Baby Cereal", "Pureed Vegetables", "Teething Biscuits", "Baby Yogurt", "Fruit Puree"],
}

# ── GENERATE RECALLS ──────────────────────────────────────────────────────────
start_date = date(2023, 1, 1)
end_date   = date(2026, 4, 30)
total_days = (end_date - start_date).days

recalls = []
recall_id = 1

# Weighted category distribution — more recalls in food categories
CAT_WEIGHTS = [12, 14, 8, 10, 9, 6, 11, 5, 8, 4, 6, 7]

for i in range(847):
    # Pick product category
    cat = random.choices(PRODUCT_CATEGORIES, weights=CAT_WEIGHTS)[0]

    # Pick root cause based on category weights
    rc_weights = CATEGORY_ROOT_CAUSE_WEIGHTS[cat]
    root_cause = random.choices(ROOT_CAUSES, weights=rc_weights)[0]

    # Pick recall class
    rc_label = random.choices(
        list(RECALL_CLASSES.keys()),
        weights=[c[2] for c in RECALL_CLASSES.values()]
    )[0]
    rc_description, severity_score, _ = RECALL_CLASSES[rc_label]

    # Pick date — weight recent months heavier to show trend
    day_offset = int(random.triangular(0, total_days, total_days * 0.7))
    recall_date = start_date + timedelta(days=min(day_offset, total_days))
    month_str = recall_date.strftime("%Y-%m")

    # Pick province
    province = random.choices(PROVINCES, weights=PROVINCE_WEIGHTS)[0]

    # Pick company and product
    company = random.choice(COMPANIES[cat])
    product = random.choice(PRODUCTS[cat])
    product_full = f"{company} {product}"

    # Generate description
    templates = DESCRIPTION_TEMPLATES[root_cause]
    template = random.choice(templates)

    allergen = random.choice(ALLERGENS)
    pathogen = random.choice(PATHOGENS)
    label_issue = random.choice(LABEL_ISSUES)
    foreign_material = random.choice(FOREIGN_MATERIALS)
    chemical = random.choice(CHEMICALS)

    description = template.format(
        company=company,
        product=product,
        allergen=allergen,
        pathogen=pathogen,
        label_issue=label_issue,
        foreign_material=foreign_material,
        chemical=chemical,
    )

    # Risk score: severity x frequency proxy x root cause weight
    rc_risk_weight = {
        "Undeclared allergen": 9,
        "Microbiological contamination": 10,
        "Chemical contamination": 8,
        "Foreign material": 7,
        "Process deviation": 6,
        "Packaging failure": 5,
        "Labelling error": 4,
        "Mislabelling of ingredients": 4,
        "Undeclared sulphites": 6,
        "Undeclared gluten": 6,
    }
    risk_score = round((severity_score * rc_risk_weight[root_cause]) / 10, 1)

    recalls.append({
        "Recall ID": f"RC-{str(recall_id).zfill(4)}",
        "Date": recall_date.strftime("%Y-%m-%d"),
        "Month": month_str,
        "Year": recall_date.year,
        "Product Category": cat,
        "Company": company,
        "Product Name": product_full,
        "Root Cause": root_cause,
        "Recall Class": rc_label,
        "Class Description": rc_description,
        "Severity Score (1-3)": severity_score,
        "Root Cause Risk Weight (1-10)": rc_risk_weight[root_cause],
        "Composite Risk Score": risk_score,
        "Province": province,
        "Recall Description": description,
    })
    recall_id += 1

# Sort by date
recalls.sort(key=lambda x: x["Date"])

with open('/home/claude/recall-intelligence/recall-dataset.csv','w',newline='',encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=recalls[0].keys())
    writer.writeheader()
    writer.writerows(recalls)

print(f"Dataset created: {len(recalls)} recalls")
print(f"Date range: {recalls[0]['Date']} to {recalls[-1]['Date']}")

# Verify distribution
from collections import Counter
cat_counts = Counter(r["Product Category"] for r in recalls)
rc_counts = Counter(r["Root Cause"] for r in recalls)
class_counts = Counter(r["Recall Class"] for r in recalls)

print("\nCategory distribution:")
for cat,count in cat_counts.most_common():
    print(f"  {cat}: {count}")
print("\nRoot cause distribution:")
for rc,count in rc_counts.most_common():
    print(f"  {rc}: {count}")
print("\nRecall class distribution:")
for cls,count in class_counts.most_common():
    print(f"  {cls}: {count}")
