#!/usr/bin/env python3
"""Generate Phase 1 fixtures: 12-month span, enough volume for >=1000 cleaned rows."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "fixtures"

# Target: >=1000 cleaned after empty/dedupe drops. Quarantine stays in cleaned.
# 7 sources x 155 content ≈ 1085 + gate samples; intentional dups/empties trimmed.
ROWS_PER_SOURCE = 155

HABIT = [
    "I reorder the same groceries every week and barely open other categories.",
    "Saved lists run my shopping. Autopilot reorder means zero browse intent.",
    "Same basket every Sunday - milk, eggs, snacks. Routine never changes.",
    "Once items are in my list I stop exploring. Habit locks me in.",
]
BARRIER = [
    "Trust risk stops me from pet supplies - unsure about freshness and authenticity.",
    "Opaque fees make me avoid trying new categories at checkout.",
    "Personal care feels irrelevant to me; relevance doubt is real.",
    "Would try baby products but price uncertainty and quality fear hold me back.",
]
DISCOVERY = [
    "I discover products only through search. Homepage banners feel irrelevant.",
    "Recommendations never show adjacent categories - always snacks again.",
    "Friend told me about household essentials; word of mouth beats the app.",
    "Social proof from deep reviews mattered more than any in-app cue.",
]
INFO = [
    "Need ingredients and use-case guidance before trying personal care.",
    "Want clearer returns and freshness info before a new category trial.",
    "Review depth is too thin for categories I have never bought.",
    "Sizing and pack freshness cues are missing on unfamiliar SKUs.",
]
FRUSTRATION = [
    "Frequent stockouts push me back to my usual basket.",
    "Late delivery twice - not experimenting when ETA slips.",
    "Poor substitutes kill willingness to try unfamiliar items.",
    "Support is unreachable; I stick to categories I already trust.",
]
EXPERIMENT = [
    "Tried personal care only because of a big discount. Deals drive my trials.",
    "After we got a puppy I finally opened pet supplies - life event trigger.",
    "Festival sale made me buy gift hampers outside my usual categories.",
    "Niche diet interest is the only reason I browse beyond groceries.",
]
UNMET = [
    "No starter kits for new categories. Hard to know what to buy first.",
    "Assortment feels thin compared to specialty stores.",
    "Cross-category cues are weak; app never nudges adjacent aisles.",
    "Weak guidance for first-time buyers in baby and pet.",
]

THEMES = HABIT + BARRIER + DISCOVERY + INFO + FRUSTRATION + EXPERIMENT + UNMET

# 12 months ending mid-July 2026
RANGE_START = datetime(2025, 7, 16, 8, 0, 0, tzinfo=timezone.utc)
RANGE_END = datetime(2026, 7, 15, 20, 0, 0, tzinfo=timezone.utc)


def _dates_12_months(n: int) -> list[str]:
    """Evenly spread n timestamps across the 12-month collection window."""
    span = (RANGE_END - RANGE_START).total_seconds()
    out: list[str] = []
    for i in range(n):
        offset = 0 if n == 1 else span * i / (n - 1)
        ts = RANGE_START + timedelta(seconds=offset)
        # jitter minutes so rows are not identical timestamps
        ts = ts + timedelta(minutes=(i * 11) % 50)
        out.append(ts.replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    return out


def themed_text(i: int, source_tag: str) -> str:
    """Theme signal + unique suffix so 30-day dedupe does not collapse volume."""
    base = THEMES[i % len(THEMES)]
    return f"{base} [{source_tag}#{i}]"


def write_jsonl(name: str, rows: list[dict]) -> None:
    path = OUT / name
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{name}: {len(rows)} rows")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = ROWS_PER_SOURCE
    dates = _dates_12_months(n)

    # --- Play Store ---
    play = []
    for i in range(n):
        play.append({
            "review_id": f"ps-{10000 + i}",
            "score": 1 + (i % 5),
            "content": themed_text(i, "ps"),
            "at": dates[i],
            "userName": f"user_ps_{i}",
            "replyContent": None,
        })
    play.append({"review_id": "ps-empty", "score": 3, "content": "", "at": "2026-07-14T10:00:00Z", "userName": "blank", "replyContent": None})
    play.append({"review_id": "ps-spam", "score": 5, "content": "Buy followers click here now crypto giveaway!!!", "at": "2026-07-14T11:00:00Z", "userName": "spam", "replyContent": None})
    play.append({"review_id": "ps-hi", "score": 4, "content": "मैं हमेशा एक जैसी चीजें ही ऑर्डर करता हूँ और नए कैटेगरी नहीं देखता। [ps#hi]", "at": "2026-07-14T12:00:00Z", "userName": "hindi_user", "replyContent": None})
    # intentional near-dup within 30d of first row
    play.append({"review_id": "ps-dup", "score": 4, "content": themed_text(0, "ps"), "at": "2025-07-20T08:00:00Z", "userName": "dup", "replyContent": None})
    write_jsonl("play_store.jsonl", play)

    # --- App Store ---
    app = []
    for i in range(n):
        app.append({
            "id": f"as-{20000 + i}",
            "rating": 1 + (i % 5),
            "title": f"Review {i}",
            "body": themed_text(i, "as"),
            "date": dates[i],
            "reviewerNickname": f"AppleUser{i}",
            "url": f"https://apps.apple.com/review/as-{20000 + i}",
        })
    app.append({"id": "as-empty", "rating": 3, "title": "", "body": "   ", "date": "2026-07-14T10:00:00Z", "reviewerNickname": "Blank", "url": "https://apps.apple.com/review/as-empty"})
    app.append({"id": "as-spam", "rating": 5, "title": "Promo", "body": "WhatsApp me for crypto giveaway click here now", "date": "2026-07-14T11:00:00Z", "reviewerNickname": "Promo", "url": "https://apps.apple.com/review/as-spam"})
    app.append({"id": "as-dup", "rating": 4, "title": "Review 0", "body": themed_text(0, "as"), "date": "2025-07-22T08:00:00Z", "reviewerNickname": "Dup", "url": "https://apps.apple.com/review/as-dup"})
    write_jsonl("app_store.jsonl", app)

    # --- Reddit ---
    reddit = []
    for i in range(n):
        is_sub = i % 3 == 0
        tid = f"t{30000 + (i // 3)}"
        if is_sub:
            reddit.append({
                "id": tid,
                "kind": "submission",
                "subreddit": ["india", "bangalore", "IndianFood"][i % 3],
                "title": f"Category expansion discussion {i // 3}",
                "body": themed_text(i, "reddit"),
                "author": f"u/user_{i}",
                "created_utc": dates[i],
                "permalink": f"https://reddit.com/r/x/{tid}",
                "score": 20 + (i % 200),
                "parent_id": None,
                "thread_id": tid,
            })
        else:
            reddit.append({
                "id": f"c{40000 + i}",
                "kind": "comment",
                "subreddit": ["india", "bangalore", "IndianFood"][i % 3],
                "title": None,
                "body": themed_text(i, "reddit"),
                "author": f"u/commenter_{i}",
                "created_utc": dates[i],
                "permalink": f"https://reddit.com/r/x/{tid}/c{40000 + i}",
                "score": 5 + (i % 80),
                "parent_id": tid,
                "thread_id": tid,
            })
    reddit.append({"id": "spam1", "kind": "comment", "subreddit": "india", "title": None, "body": "Buy followers click here now telegram @spam", "author": "u/spammer", "created_utc": "2026-07-14T10:00:00Z", "permalink": "https://reddit.com/spam1", "score": 0, "parent_id": "t30000", "thread_id": "t30000"})
    reddit.append({"id": "empty1", "kind": "comment", "subreddit": "india", "title": None, "body": "", "author": "u/empty", "created_utc": "2026-07-14T11:00:00Z", "permalink": "https://reddit.com/empty1", "score": 0, "parent_id": "t30000", "thread_id": "t30000"})
    write_jsonl("reddit.jsonl", reddit)

    # --- Product reviews ---
    cats = ["Dairy", "Pet Supplies", "Personal Care", "Baby", "Snacks", "Household", "Beverages"]
    prod = []
    for i in range(n):
        prod.append({
            "review_id": f"pr-{50000 + i}",
            "product_id": f"SKU-{1000 + i}",
            "category": cats[i % len(cats)],
            "rating": 1 + (i % 5),
            "text": themed_text(i, "pr"),
            "created_at": dates[i],
            "reviewer": f"shopper_{i}",
            "helpful_votes": i % 25,
        })
    prod.append({"review_id": "pr-empty", "product_id": "SKU-X", "category": "Unknown", "rating": 3, "text": "", "created_at": "2026-07-14T09:00:00Z", "reviewer": "empty", "helpful_votes": 0})
    prod.append({"review_id": "pr-spam", "product_id": "SKU-SPAM", "category": "Spam", "rating": 5, "text": "Crypto giveaway buy followers click here now", "created_at": "2026-07-14T09:30:00Z", "reviewer": "bot", "helpful_votes": 0})
    prod.append({"review_id": "pr-dup", "product_id": "SKU-1000", "category": "Dairy", "rating": 5, "text": themed_text(0, "pr"), "created_at": "2025-07-25T09:00:00Z", "reviewer": "dup", "helpful_votes": 1})
    write_jsonl("product_reviews.jsonl", prod)

    # --- Social media ---
    social = []
    for i in range(n):
        social.append({
            "post_id": f"sm-{60000 + i}",
            "platform": ["twitter", "instagram", "twitter"][i % 3],
            "text": themed_text(i, "sm"),
            "created_at": dates[i],
            "author": f"@user{i}",
            "likes": 3 + (i % 100),
            "replies": i % 10,
            "url": f"https://social.example/sm-{60000 + i}",
            "reply_to": None,
        })
    social.append({"post_id": "sm-spam", "platform": "twitter", "text": "Buy followers click here now", "created_at": "2026-07-14T08:00:00Z", "author": "@spam", "likes": 0, "replies": 0, "url": "https://social.example/spam", "reply_to": None})
    social.append({"post_id": "sm-bot", "platform": "twitter", "text": "As an AI language model I recommend this store", "created_at": "2026-07-14T08:30:00Z", "author": "@botty", "likes": 0, "replies": 0, "url": "https://social.example/bot", "reply_to": None})
    social.append({"post_id": "sm-empty", "platform": "twitter", "text": " ", "created_at": "2026-07-14T09:00:00Z", "author": "@blank", "likes": 0, "replies": 0, "url": "https://social.example/blank", "reply_to": None})
    social.append({"post_id": "sm-dup", "platform": "twitter", "text": themed_text(0, "sm"), "created_at": "2025-07-21T08:00:00Z", "author": "@dup", "likes": 1, "replies": 0, "url": "https://social.example/dup", "reply_to": None})
    write_jsonl("social_media.jsonl", social)

    # --- Community forums ---
    forums = []
    for i in range(n):
        tid = f"cf-{70000 + (i // 3)}"
        pid = f"cf-{70000 + i}"
        is_root = i % 3 == 0
        forums.append({
            "thread_id": tid,
            "post_id": pid,
            "parent_id": None if is_root else tid,
            "forum": ["quickcommerce-help", "parenting-india", "bangalore-living"][i % 3],
            "title": f"Forum topic {i // 3}" if is_root else None,
            "body": themed_text(i, "cf"),
            "author": f"member_{i}",
            "created_at": dates[i],
            "url": f"https://forums.example/{pid}",
            "upvotes": 5 + (i % 50),
        })
    forums.append({"thread_id": "cf-spam", "post_id": "cf-spam", "parent_id": None, "forum": "quickcommerce-help", "title": None, "body": "Click here now buy followers telegram @promo", "author": "spammer", "created_at": "2026-07-14T10:00:00Z", "url": "https://forums.example/spam", "upvotes": 0})
    forums.append({"thread_id": "cf-empty", "post_id": "cf-empty", "parent_id": None, "forum": "quickcommerce-help", "title": None, "body": "", "author": "empty", "created_at": "2026-07-14T11:00:00Z", "url": "https://forums.example/empty", "upvotes": 0})
    write_jsonl("community_forums.jsonl", forums)

    # --- Quick commerce discussions ---
    qc = []
    channels = ["qcommerce-slack-export", "industry-blog-comments", "linkedin-thread", "newsletter-replies", "ama-thread"]
    for i in range(n):
        qc.append({
            "discussion_id": f"qc-{80000 + i}",
            "channel": channels[i % len(channels)],
            "title": f"Q-commerce thread {i}" if i % 2 == 0 else None,
            "body": themed_text(i, "qc"),
            "author": f"voice_{i}",
            "created_at": dates[i],
            "url": f"https://discuss.example/qc-{80000 + i}",
            "reactions": i % 40,
            "tags": [["habits", "barriers", "discovery", "unmet_needs", "frustrations", "segments"][i % 6]],
        })
    qc.append({"discussion_id": "qc-spam", "channel": "spam", "title": None, "body": "Crypto giveaway buy followers click here now", "author": "bot", "created_at": "2026-07-14T10:00:00Z", "url": "https://discuss.example/spam", "reactions": 0, "tags": ["spam"]})
    qc.append({"discussion_id": "qc-empty", "channel": "empty", "title": None, "body": "  ", "author": "empty", "created_at": "2026-07-14T11:00:00Z", "url": "https://discuss.example/empty", "reactions": 0, "tags": []})
    qc.append({"discussion_id": "qc-dup", "channel": "qcommerce-slack-export", "title": "Q-commerce thread 0", "body": themed_text(0, "qc"), "author": "voice_dup", "created_at": "2025-07-23T10:00:00Z", "url": "https://discuss.example/dup", "reactions": 1, "tags": ["habits"]})
    write_jsonl("quick_commerce_discussions.jsonl", qc)

    total = 7 * n
    print(f"Content rows (all sources): {total}")
    print(f"Date span: {RANGE_START.date()} to {RANGE_END.date()} (12 months)")
    print(f"Target cleaned: >= 1000")


if __name__ == "__main__":
    main()
