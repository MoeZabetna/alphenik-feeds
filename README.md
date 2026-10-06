# Alphenik product feeds

Live product feed for ChatGPT Ads / ChatGPT Shopping (Google Shopping feed format, AED, UAE).

- CSV (18K gold plated jewellery only, 128 items — used by ChatGPT Ads): https://raw.githubusercontent.com/MoeZabetna/alphenik-feeds/main/alphenik_chatgpt_feed.csv
- TSV (same 18K set): https://raw.githubusercontent.com/MoeZabetna/alphenik-feeds/main/alphenik_chatgpt_feed.tsv
- Full catalogue (403 variants): https://raw.githubusercontent.com/MoeZabetna/alphenik-feeds/main/alphenik_chatgpt_feed_full.csv

Regenerated daily at 06:00 Asia/Dubai from the Shopify Admin API (`build_feed.py`).
Only products published to the Online Store with a featured image are included; one row per variant.
