from langchain_core.tools import tool

@tool
def check_threshold(
    records: list = None,
    metric_field: str = "stock",
    threshold: float = 10.0,
    direction: str = "below",
    **kwargs,
) -> list[dict]:
    """Find records whose numeric value is above or below a threshold."""

    if not records or type(records) is not list:
        return []

    matching_records = []
    for record in records:
        if type(record) is not dict:
            continue
        metric_value = record.get(metric_field)

        if metric_value is None:
            continue
        
        try:
            metric_value = float(metric_value)
            threshold_value = float(threshold)

            if direction == "below" and metric_value < threshold_value:
                matching_records.append(record)

            elif direction == "above" and metric_value > threshold_value:
                matching_records.append(record)

        except (ValueError, TypeError):
            continue

    return matching_records

@tool
def compare_prices(
    records: list = None,
    benchmark_field: str = "target_price",
    vendor_price_field: str = "vendor_price",
    **kwargs,
) -> list[dict]:
    """Compare vendor prices with target prices."""

    if not records or type(records) is not list:
        return []

    price_comparison_results = []

    for record in records:
        if type(record) is not dict:
            continue

        try:
            target_price = float(record.get(benchmark_field, 0))
            vendor_price = float(record.get(vendor_price_field, 0))

            price_difference = round(vendor_price - target_price, 2)

            percentage_difference = (
                round((price_difference / target_price) * 100, 2)
                if target_price > 0 else 0.0
            )

            comparison_record = {
                **record,
                "price_variance": price_difference,
                "variance_pct": percentage_difference,
                "is_overpriced": vendor_price > target_price,
            }

            price_comparison_results.append(comparison_record)

        except (ValueError, TypeError):
            continue

    return price_comparison_results

@tool
def validate_catalog_data(
    records: list = None,
    required_fields: list = None,
    **kwargs,
) -> dict:
    """Find catalog records with missing fields or duplicate IDs."""

    if not records or type(records) is not list:
        return {
            "total_checked": 0,
            "invalid_count": 0,
            "invalid_records": [],
            "duplicate_ids": [],
        }

    required_field_names = required_fields or [
        "sku", "name", "price", "category"
    ]

    invalid_records = []
    existing_ids = set()
    duplicate_ids = []

    for row_number, record in enumerate(records):
        if type(record) is not dict:
            continue

        missing_fields = []

        for field_name in required_field_names:
            field_value = record.get(field_name)

            if field_value is None or str(field_value).strip() == "":
                missing_fields.append(field_name)

        product_id = (
            record.get("sku")
            or record.get("id")
            or f"row_{row_number}"
        )

        if product_id in existing_ids:
            duplicate_ids.append(product_id)
        else:
            existing_ids.add(product_id)

        if missing_fields:
            invalid_records.append({
                "record_id": product_id,
                "missing_fields": missing_fields,
            })

    return {
        "total_checked": len(records),
        "invalid_count": len(invalid_records),
        "invalid_records": invalid_records,
        "duplicate_ids": duplicate_ids,
    }

@tool
def detect_log_anomalies(
    records: list = None,
    status_field: str = "status",
    error_values: list = None,
    **kwargs,
) -> list[dict]:
    """Find execution logs containing failure-related status messages."""

    if not records or type(records) is not list:
        return []

    error_keywords = [
        keyword.lower()
        for keyword in (
            error_values or [
                "error", "failed", "timeout", "exception", "fatal"
            ]
        )
    ]

    failed_log_records = []

    for log_record in records:
        if type(log_record) is not dict:
            continue

        status_value = str(
            log_record.get(status_field, "")
        ).strip().lower()

        for error_keyword in error_keywords:
            if error_keyword in status_value:
                failed_log_records.append(log_record)
                break

    return failed_log_records