import json, csv, re, html, glob

TYPE_TO_GOOGLE = {
    "necklace": "Apparel & Accessories > Jewelry > Necklaces",
    "bracelets": "Apparel & Accessories > Jewelry > Bracelets",
    "bracelet": "Apparel & Accessories > Jewelry > Bracelets",
    "bangles": "Apparel & Accessories > Jewelry > Bracelets",
    "rings": "Apparel & Accessories > Jewelry > Rings",
    "ring": "Apparel & Accessories > Jewelry > Rings",
    "earrings": "Apparel & Accessories > Jewelry > Earrings",
    "earring": "Apparel & Accessories > Jewelry > Earrings",
    "anklets": "Apparel & Accessories > Jewelry > Anklets",
    "anklet": "Apparel & Accessories > Jewelry > Anklets",
    "eyewear": "Apparel & Accessories > Clothing Accessories > Sunglasses",
    "sunglasses": "Apparel & Accessories > Clothing Accessories > Sunglasses",
    "scarves": "Apparel & Accessories > Clothing Accessories > Scarves & Shawls",
    "scarf": "Apparel & Accessories > Clothing Accessories > Scarves & Shawls",
    "bags": "Apparel & Accessories > Handbags, Wallets & Cases > Handbags",
    "beach bags": "Apparel & Accessories > Handbags, Wallets & Cases > Handbags",
    "hair accessories": "Apparel & Accessories > Clothing Accessories > Hair Accessories",
    "sets": "Apparel & Accessories > Jewelry > Jewelry Sets",
    "set": "Apparel & Accessories > Jewelry > Jewelry Sets",
}

def strip_html(s):
    s = re.sub(r"<br\s*/?>", " ", s or "")
    s = re.sub(r"</p>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:5000]

rows = []
seen = set()
for f in sorted(glob.glob("/home/claude/feed/page*.json")):
    data = json.load(open(f))
    for p in data["data"]["products"]["nodes"]:
        if p["id"] in seen:
            continue
        seen.add(p["id"])
        url = p.get("onlineStoreUrl") or f"https://alphenik.com/products/{p['handle']}"
        if not p.get("onlineStoreUrl"):
            continue  # not published to Online Store
        desc = strip_html(p.get("descriptionHtml"))
        if not desc:
            desc = f"{p['title']} by Alphenik. Free next-day delivery across the UAE. Pay in 4 with Tabby."
        imgs = [i["url"] for i in p.get("images", {}).get("nodes", [])]
        feat = (p.get("featuredImage") or {}).get("url") or (imgs[0] if imgs else "")
        if not feat:
            continue
        ptype = (p.get("productType") or "").strip()
        gcat = TYPE_TO_GOOGLE.get(ptype.lower(), "Apparel & Accessories > Jewelry")
        tags = [t.lower() for t in p.get("tags", [])]
        material = "18K gold plated" if ("18k-gold" in tags or "18k" in p["title"].lower()) else ("Stainless steel" if "stainless-steel" in tags else "")
        variants = p["variants"]["nodes"]
        multi = len(variants) > 1
        for v in variants:
            vid = v["id"].split("/")[-1]
            pid = p["id"].split("/")[-1]
            qty = v.get("inventoryQuantity") or 0
            availability = "in_stock" if qty > 0 else "out_of_stock"
            price = f"{float(v['price']):.2f} AED"
            sale = ""
            cap = v.get("compareAtPrice")
            if cap and float(cap) > float(v["price"]):
                price = f"{float(cap):.2f} AED"
                sale = f"{float(v['price']):.2f} AED"
            title = p["title"] if (not multi or v["title"] == "Default Title") else f"{p['title']} — {v['title']}"
            link = url if not multi else f"{url}?variant={vid}"
            img = (v.get("image") or {}).get("url") or feat
            add_imgs = ",".join([i for i in imgs if i != img][:5])
            rows.append({
                "id": vid,
                "item_group_id": pid,
                "title": title[:150],
                "description": desc,
                "link": link,
                "image_link": img,
                "additional_image_link": add_imgs,
                "availability": availability,
                "price": price,
                "sale_price": sale,
                "brand": "Alphenik",
                "condition": "new",
                "gtin": v.get("barcode") or "",
                "mpn": v.get("sku") or "",
                "product_type": ptype,
                "google_product_category": gcat,
                "material": material,
                "gender": "female",
                "age_group": "adult",
                "shipping": "AE::Next-day delivery:0.00 AED",
                "seller_name": "Alphenik",
                "seller_url": "https://alphenik.com",
                "store_country": "AE",
                "target_countries": "AE",
            })

fields = list(rows[0].keys())
# 18K-only feed = the main URL used by ChatGPT Ads (Oct 6: narrowed from full catalogue at Mo's request)
gold = [r for r in rows if r["material"] == "18K gold plated"]
def write(path, data, delim=","):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=delim, quoting=csv.QUOTE_ALL if delim == "," else csv.QUOTE_MINIMAL)
        w.writeheader(); w.writerows(data)
write("/home/claude/feed/alphenik_chatgpt_feed.csv", gold)
write("/home/claude/feed/alphenik_chatgpt_feed.tsv", gold, "\t")
write("/home/claude/feed/alphenik_chatgpt_feed_full.csv", rows)
instock = sum(1 for r in gold if r["availability"] == "in_stock")
print(f"products={len(seen)} full_rows={len(rows)} gold_rows={len(gold)} gold_in_stock={instock} gold_out_of_stock={len(gold)-instock}")
