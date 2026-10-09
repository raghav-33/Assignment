import json
from pathlib import Path
import pandas as pd

from src.config import DATA_DIR


def ensure_data_directory():
    """Create data/ folder if it does not already exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Data directory confirmed at: {DATA_DIR.resolve()}")


def generate_inventory_csv():
    """Generates data/inventory.csv for WF001 (low stock / restock checks)."""
    data = [
        {"sku": "SKU-1001", "name": "Wireless Mouse", "category": "Electronics", "stock": 4, "reorder_level": 15, "unit_cost": 18.50},
        {"sku": "SKU-1002", "name": "Mechanical Keyboard", "category": "Electronics", "stock": 25, "reorder_level": 10, "unit_cost": 55.00},
        {"sku": "SKU-1003", "name": "USB-C Hub", "category": "Accessories", "stock": 7, "reorder_level": 20, "unit_cost": 22.00},
        {"sku": "SKU-1004", "name": "Laptop Stand", "category": "Accessories", "stock": 18, "reorder_level": 10, "unit_cost": 28.00},
        {"sku": "SKU-1005", "name": "HDMI Cable 2m", "category": "Cables", "stock": 2, "reorder_level": 25, "unit_cost": 6.50},
        {"sku": "SKU-1006", "name": "Webcam 1080p", "category": "Electronics", "stock": 35, "reorder_level": 12, "unit_cost": 42.00},
        {"sku": "SKU-1007", "name": "Noise Cancelling Headset", "category": "Audio", "stock": 9, "reorder_level": 15, "unit_cost": 85.00},
        {"sku": "SKU-1008", "name": "Mousepad XL", "category": "Accessories", "stock": 50, "reorder_level": 15, "unit_cost": 9.00},
    ]
    path = DATA_DIR / "inventory.csv"
    pd.DataFrame(data).to_csv(path, index=False)
    print(f"Generated: {path.name} ({len(data)} items)")


def generate_vendor_and_catalog_files():
    """Generates data/catalog.csv and data/vendor_prices.csv for WF002 & WF005."""
    # Catalog dataset (base benchmark prices)
    catalog = [
        {"sku": "SKU-2001", "name": "Ergonomic Office Chair", "category": "Furniture", "price": 180.00, "target_price": 150.00},
        {"sku": "SKU-2002", "name": "Standing Desk 48x30", "category": "Furniture", "price": 320.00, "target_price": 280.00},
        {"sku": "SKU-2003", "name": "Desk Mat Leather", "category": "Accessories", "price": 35.00, "target_price": 25.00},
        {"sku": "SKU-2004", "name": "Monitor Arm Dual", "category": "Accessories", "price": 95.00, "target_price": 75.00},
        {"sku": "SKU-2005", "name": "Desk Lamp LED", "category": "Lighting", "price": 45.00, "target_price": 35.00},
    ]
    catalog_path = DATA_DIR / "catalog.csv"
    pd.DataFrame(catalog).to_csv(catalog_path, index=False)
    print(f"Generated: {catalog_path.name} ({len(catalog)} items)")

    # Vendor prices comparison dataset (with some overpriced quotes)
    vendor_quotes = [
        {"sku": "SKU-2001", "name": "Ergonomic Office Chair", "vendor_name": "Apex Supplies", "target_price": 150.00, "vendor_price": 172.50},
        {"sku": "SKU-2002", "name": "Standing Desk 48x30", "vendor_name": "Apex Supplies", "target_price": 280.00, "vendor_price": 275.00},
        {"sku": "SKU-2003", "name": "Desk Mat Leather", "vendor_name": "Prime Goods", "target_price": 25.00, "vendor_price": 31.00},
        {"sku": "SKU-2004", "name": "Monitor Arm Dual", "vendor_name": "Prime Goods", "target_price": 75.00, "vendor_price": 72.00},
        {"sku": "SKU-2005", "name": "Desk Lamp LED", "vendor_name": "Lumen Corp", "target_price": 35.00, "vendor_price": 44.00},
    ]
    vendor_path = DATA_DIR / "vendor_prices.csv"
    pd.DataFrame(vendor_quotes).to_csv(vendor_path, index=False)
    print(f"Generated: {vendor_path.name} ({len(vendor_quotes)} quotes)")


def generate_vendor_products_excel():
    """Generates data/vendor_products.xlsx for WF003 (Excel reader testing)."""
    excel_data = [
        {"sku": "VP-301", "product_name": "Industrial Router AX", "vendor": "Cisco Dist", "cost": 420.00, "stock": 14, "lead_time_days": 5},
        {"sku": "VP-302", "product_name": "PoE Switch 16-Port", "vendor": "Netgear Direct", "cost": 195.00, "stock": 8, "lead_time_days": 3},
        {"sku": "VP-303", "product_name": "Cat6 Cable 1000ft", "vendor": "Belden Wholesale", "cost": 140.00, "stock": 22, "lead_time_days": 7},
        {"sku": "VP-304", "product_name": "Server Rack 42U", "vendor": "TrippLite Corp", "cost": 890.00, "stock": 3, "lead_time_days": 14},
    ]
    excel_path = DATA_DIR / "vendor_products.xlsx"
    pd.DataFrame(excel_data).to_excel(excel_path, index=False)
    print(f"Generated: {excel_path.name} ({len(excel_data)} products)")


def generate_orders_json():
    """Generates data/orders.json for WF004 and order fulfillment workflows."""
    orders = [
        {
            "order_id": "ORD-5001",
            "customer_id": "CUST-101",
            "order_date": "2026-10-01T10:30:00Z",
            "status": "pending",
            "total_amount": 245.50,
            "items": [
                {"sku": "SKU-1001", "quantity": 2, "price": 18.50},
                {"sku": "SKU-1002", "quantity": 1, "price": 55.00},
            ],
        },
        {
            "order_id": "ORD-5002",
            "customer_id": "CUST-104",
            "order_date": "2026-10-02T14:15:00Z",
            "status": "shipped",
            "total_amount": 95.00,
            "items": [
                {"sku": "SKU-1004", "quantity": 1, "price": 28.00},
            ],
        },
        {
            "order_id": "ORD-5003",
            "customer_id": "CUST-108",
            "order_date": "2026-10-03T09:00:00Z",
            "status": "pending",
            "total_amount": 540.00,
            "items": [
                {"sku": "SKU-1007", "quantity": 4, "price": 85.00},
            ],
        },
        {
            "order_id": "ORD-5004",
            "customer_id": "CUST-112",
            "order_date": "2026-10-04T16:45:00Z",
            "status": "delivered",
            "total_amount": 12.00,
            "items": [
                {"sku": "SKU-1005", "quantity": 2, "price": 6.50},
            ],
        },
    ]
    json_path = DATA_DIR / "orders.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)
    print(f"Generated: {json_path.name} ({len(orders)} orders)")


def generate_keywords_csv():
    """Generates data/keywords.csv for WF006 (marketing/keyword audits)."""
    keywords = [
        {"keyword": "wireless ergonomic mouse", "search_volume": 12500, "cpc": 1.45, "competition": "HIGH", "intent": "commercial"},
        {"keyword": "best mechanical keyboard for coding", "search_volume": 8900, "cpc": 2.10, "competition": "MEDIUM", "intent": "informational"},
        {"keyword": "usb-c docking station dual monitor", "search_volume": 15400, "cpc": 3.20, "competition": "HIGH", "intent": "transactional"},
        {"keyword": "cheap hdmi cable 4k", "search_volume": 6700, "cpc": 0.85, "competition": "LOW", "intent": "transactional"},
        {"keyword": "standing desk converter under 200", "search_volume": 4300, "cpc": 1.95, "competition": "MEDIUM", "intent": "commercial"},
    ]
    path = DATA_DIR / "keywords.csv"
    pd.DataFrame(keywords).to_csv(path, index=False)
    print(f"Generated: {path.name} ({len(keywords)} keywords)")


def generate_employees_json():
    """Generates data/employees.json for WF007 (HR/employee lookups)."""
    employees = [
        {"employee_id": "EMP-01", "name": "Alice Johnson", "department": "Engineering", "role": "Senior Developer", "status": "active"},
        {"employee_id": "EMP-02", "name": "Bob Smith", "department": "Supply Chain", "role": "Logistics Manager", "status": "active"},
        {"employee_id": "EMP-03", "name": "Carol Danvers", "department": "Finance", "role": "Accounts Auditor", "status": "active"},
        {"employee_id": "EMP-04", "name": "David Miller", "department": "Operations", "role": "Inventory Supervisor", "status": "on_leave"},
    ]
    path = DATA_DIR / "employees.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=2)
    print(f"Generated: {path.name} ({len(employees)} employees)")


def generate_execution_logs_csv():
    """Generates data/execution_logs.csv for WF008 & WF010 (log anomaly/error auditing)."""
    logs = [
        {"log_id": "LOG-801", "timestamp": "2026-10-05T08:00:12Z", "service": "PaymentGateway", "status": "SUCCESS", "duration_ms": 120, "message": "Transaction charged"},
        {"log_id": "LOG-802", "timestamp": "2026-10-05T08:05:43Z", "service": "InventorySync", "status": "FAILED", "duration_ms": 5012, "message": "Database connection timeout"},
        {"log_id": "LOG-803", "timestamp": "2026-10-05T08:12:00Z", "service": "EmailNotifier", "status": "SUCCESS", "duration_ms": 85, "message": "Email delivered to user"},
        {"log_id": "LOG-804", "timestamp": "2026-10-05T08:15:22Z", "service": "OrderDispatch", "status": "ERROR", "duration_ms": 340, "message": "Null address attribute encountered"},
        {"log_id": "LOG-805", "timestamp": "2026-10-05T08:20:10Z", "service": "OrderDispatch", "status": "SUCCESS", "duration_ms": 190, "message": "Order pushed to courier"},
        {"log_id": "LOG-806", "timestamp": "2026-10-05T08:25:55Z", "service": "PaymentGateway", "status": "TIMEOUT", "duration_ms": 10004, "message": "Third-party payment webhook timed out"},
    ]
    path = DATA_DIR / "execution_logs.csv"
    pd.DataFrame(logs).to_csv(path, index=False)
    print(f"Generated: {path.name} ({len(logs)} logs)")


def main():
    print("=" * 60)
    print("Generating Mock Datasets for Assessment Workflows...")
    print("=" * 60)
    ensure_data_directory()

    generate_inventory_csv()
    generate_vendor_and_catalog_files()
    generate_vendor_products_excel()
    generate_orders_json()
    generate_keywords_csv()
    generate_employees_json()
    generate_execution_logs_csv()

    print("=" * 60)
    print("All datasets successfully generated in the data/ folder.")
    print("=" * 60)


if __name__ == "__main__":
    main()