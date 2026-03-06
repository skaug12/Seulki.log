#!/usr/bin/env python3
"""Analyze and summarize all imweb product JSON files."""

import json
from collections import OrderedDict

FILES = [
    "/Users/sklee/hfk-sklee/archive/data/imweb_products_20260122_170736.json",
    "/Users/sklee/hfk-sklee/archive/data/imweb_products_20260122_170906.json",
    "/Users/sklee/hfk-sklee/archive/data/imweb_products_20260122_171019.json",
    "/Users/sklee/hfk-sklee/archive/data/imweb_products_20260122_171322.json",
]

def load_and_deduplicate():
    """Load all files and deduplicate by 'no' field, keeping first occurrence."""
    seen = OrderedDict()  # no -> product dict
    file_stats = []

    for filepath in FILES:
        filename = filepath.split("/")[-1]
        with open(filepath, "r", encoding="utf-8") as f:
            products = json.load(f)

        new_count = 0
        dup_count = 0
        for prod in products:
            no = prod["no"]
            if no not in seen:
                seen[no] = prod
                new_count += 1
            else:
                dup_count += 1

        file_stats.append((filename, len(products), new_count, dup_count))

    return seen, file_stats


def format_categories(cats):
    """Extract category names from categories structure."""
    if not cats:
        return "(none)"
    if isinstance(cats, list):
        names = []
        for c in cats:
            if isinstance(c, dict):
                name = c.get("category_name") or c.get("name") or str(c)
                names.append(name)
            else:
                names.append(str(c))
        return " > ".join(names) if names else "(none)"
    if isinstance(cats, dict):
        return str(cats)
    return str(cats)


def format_price(price_val):
    """Format price value."""
    if price_val is None:
        return "N/A"
    if isinstance(price_val, (int, float)):
        return f"{int(price_val):,}원"
    return str(price_val)


def main():
    seen, file_stats = load_and_deduplicate()

    # --- File loading stats ---
    print("=" * 90)
    print("FILE LOADING SUMMARY")
    print("=" * 90)
    total_raw = 0
    for filename, total, new, dup in file_stats:
        total_raw += total
        print(f"  {filename}: {total:>4} products | {new:>3} new | {dup:>3} duplicates")
    print(f"  {'':->70}")
    print(f"  Total raw records: {total_raw}  |  Unique products: {len(seen)}")
    print()

    # Sort by "no" ascending
    sorted_products = sorted(seen.values(), key=lambda p: p["no"])

    # --- Schema: print all top-level keys of the first product ---
    print("=" * 90)
    print("SCHEMA (top-level keys of first product)")
    print("=" * 90)
    first = sorted_products[0]
    for i, key in enumerate(first.keys()):
        val = first[key]
        val_type = type(val).__name__
        val_preview = ""
        if isinstance(val, str):
            val_preview = f' = "{val[:60]}{"..." if len(val) > 60 else ""}"'
        elif isinstance(val, (int, float)):
            val_preview = f" = {val}"
        elif isinstance(val, list):
            val_preview = f" (len={len(val)})"
        elif isinstance(val, dict):
            val_preview = f" (keys={list(val.keys())[:5]})"
        elif val is None:
            val_preview = " = None"
        print(f"  {i+1:>2}. {key:<35} [{val_type}]{val_preview}")
    print()

    # --- Product summaries ---
    print("=" * 90)
    print(f"ALL UNIQUE PRODUCTS (sorted by no, ascending)  --  Total: {len(sorted_products)}")
    print("=" * 90)

    for idx, prod in enumerate(sorted_products, 1):
        no = prod.get("no", "?")
        name = prod.get("name", "(unnamed)")
        categories = prod.get("categories", [])
        prod_status = prod.get("prod_status", "?")
        price = prod.get("price", None)

        has_prod_code = "prod_code" in prod
        prod_code_val = prod.get("prod_code", None)
        custom_prod_code = prod.get("custom_prod_code", None)

        content_plain = prod.get("content_plain", "")
        content_snippet = ""
        if content_plain:
            content_snippet = content_plain[:50].replace("\n", " ").strip()
            if len(content_plain) > 50:
                content_snippet += "..."

        cat_str = format_categories(categories)

        print(f"\n[{idx:>3}] no={no}")
        print(f"      name:          {name}")
        print(f"      categories:    {cat_str}")
        print(f"      prod_status:   {prod_status}")
        print(f"      price:         {format_price(price)}")
        if has_prod_code:
            print(f"      prod_code:     {prod_code_val}")
        else:
            print(f"      prod_code:     (field absent)")
        print(f"      custom_prod_code: {custom_prod_code if custom_prod_code else '(empty)'}")
        if content_snippet:
            print(f"      content_plain: {content_snippet}")
        else:
            print(f"      content_plain: (empty)")

    # --- Final count ---
    print()
    print("=" * 90)
    print(f"TOTAL UNIQUE PRODUCTS: {len(sorted_products)}")
    print("=" * 90)


if __name__ == "__main__":
    main()
