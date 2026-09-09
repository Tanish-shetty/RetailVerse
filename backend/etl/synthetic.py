"""Generate reproducible demonstration data. Never represents actual retail activity."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def generate(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    products = [("Everyday Tea", "Beverages", 140), ("Filter Coffee", "Beverages", 260),
                ("Whole Milk", "Dairy", 60), ("Cultured Yogurt", "Dairy", 45),
                ("Oat Biscuits", "Snacks", 35), ("Salted Crisps", "Snacks", 25),
                ("Laundry Liquid", "Home Care", 220), ("Dishwash Gel", "Home Care", 90),
                ("Bath Soap", "Personal Care", 55), ("Herbal Shampoo", "Personal Care", 180)]
    locations = [("Mumbai", "Maharashtra", "West"), ("Ahmedabad", "Gujarat", "West"),
                 ("Delhi", "Delhi", "North"), ("Bengaluru", "Karnataka", "South"),
                 ("Kolkata", "West Bengal", "East")]
    rows = []
    for day in pd.date_range("2023-01-01", "2025-12-31"):
        demand = 20 * (1 + .18 * np.sin(day.dayofyear / 365 * 2 * np.pi))
        for _ in range(rng.poisson(demand)):
            p, loc = int(rng.integers(10)), int(rng.integers(5))
            name, category, price = products[p]
            city, state, region = locations[loc]
            discount = float(rng.choice([0, .1, .2], p=[.7, .2, .1]))
            rows.append(dict(line_id=f"L{len(rows):07d}", transaction_id=f"T{len(rows)//2:07d}",
                date=day.date().isoformat(), customer_id=f"C{int(rng.integers(1,601)):04d}",
                product_id=f"P{p:02d}", product_name=name, brand=f"Demo Brand {p//2+1}", category=category,
                location_id=f"S{loc}", store=f"Demo Store {loc+1}", city=city, state=state, region=region,
                promotion_id=f"D{int(discount*100)}", campaign="No promotion" if not discount else f"Demo {int(discount*100)}%",
                quantity=int(rng.integers(1,8)), unit_price=price, unit_cost=round(price*.64,2),
                discount=discount, source="synthetic"))
    frame = pd.DataFrame(rows)
    # Orders have a single customer/date/location; maintain a real line-grain contract.
    for col in ["date", "customer_id", "location_id", "store", "city", "state", "region"]:
        frame[col] = frame.groupby("transaction_id")[col].transform("first")
    return frame


if __name__ == "__main__":
    target = ROOT / "data/raw/synthetic_sales.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    data = generate()
    data.to_csv(target, index=False)
    print(f"Generated {len(data):,} SYNTHETIC lines: {target}")
