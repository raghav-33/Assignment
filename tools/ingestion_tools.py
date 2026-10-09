import json
from pathlib import Path
import pandas as pd
from langchain_core.tools import tool
from src.config import DATA_DIR


def find_file(file_name: str) -> Path:
    """Find a file in the given path or the project's data folder."""
    file_path = Path(file_name)

    if file_path.is_file():
        return file_path

    file_path = DATA_DIR / file_name
    if file_path.is_file():
        return file_path

    raise FileNotFoundError(f"File not found: {file_name}")

# Reading CSV
@tool
def read_csv(file_path: str = "inventory.csv", **kwargs) -> list[dict]:
    """Read a CSV file and return its rows as dictionaries."""
    file_path_obj = find_file(file_path)

    if file_path_obj.suffix.lower() != ".csv":
        raise ValueError("Please provide a CSV file.")

    data = pd.read_csv(file_path_obj)
    data = data.astype(object).where(pd.notna(data), None)

    return data.to_dict(orient="records")

# Reading Excel
@tool
def read_excel(
    file_path: str = "vendor_products.xlsx", sheet_name=0, **kwargs
) -> list[dict]:
    """Read an Excel sheet and return its rows as dictionaries."""
    file_path_obj = find_file(file_path)

    if file_path_obj.suffix.lower() not in [".xlsx", ".xls"]:
        raise ValueError("Please provide an Excel file.")

    data = pd.read_excel(file_path_obj, sheet_name=sheet_name)
    data = data.astype(object).where(pd.notna(data), None)

    return data.to_dict(orient="records")

# Reading Json File
@tool
def read_json(file_path: str = "orders.json", **kwargs):
    """Read a JSON file and return its contents."""
    file_path_obj = find_file(file_path)

    if file_path_obj.suffix.lower() != ".json":
        raise ValueError("Please provide a JSON file.")

    with open(file_path_obj, "r", encoding="utf-8") as file:
        return json.load(file)

# Filters Record

def filter_records(
    records: list = None,
    field: str = "stock",
    operator: str = "<=",
    value=10,
    **kwargs,
) -> list[dict]:
    """Filter records based on comparison conditions."""
    if not records or not isinstance(records, list):
        return []

    filtered = []
    for row in records:
        if not isinstance(row, dict):
            continue

        row_val = row.get(field)
        if row_val is None:
            continue

        try:
            if operator == "==" and str(row_val).lower() == str(value).lower():
                filtered.append(row)
            elif (
                operator == "!=" and str(row_val).lower() != str(value).lower()
            ):
                filtered.append(row)
            elif operator == "<" and float(row_val) < float(value):
                filtered.append(row)
            elif operator == "<=" and float(row_val) <= float(value):
                filtered.append(row)
            elif operator == ">" and float(row_val) > float(value):
                filtered.append(row)
            elif operator == ">=" and float(row_val) >= float(value):
                filtered.append(row)
            elif (
                operator == "contains"
                and str(value).lower() in str(row_val).lower()
            ):
                filtered.append(row)
        except (ValueError, TypeError):
            continue

    return filtered