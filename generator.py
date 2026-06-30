# blog/generator.py — Auto-generates a beautiful affiliate blog page
# Deploys to GitHub Pages for free hosting

import os, json, re
from datetime import datetime
from pathlib import Path

BLOG_OUTPUT_DIR = "blog/posts"
os.makedirs(BLOG_OUTPUT_DIR, exist_ok=True)


def generate_blog_html(niche: str, products: list[dict]) -> str:
    """
    Generate a complete, beautiful HTML blog post for a niche.
    Each product has: image, name, price, discount, review, buy button.
    """

    today       = datetime.now().strftime("%B %d, %Y")
    slug        = niche.lower().replace(" ", "-")
    page_title  = f"Top {len(products)} {niche} Deals Under ₹999 — Best Picks {datetime.now().year}"
    description = (f"Find the best {niche} deals with up to 90% off on Flipkart. "
                   f"Handpicked top {len(products)} products with reviews and direct buy links.")

    # Generate product cards HTML
    product_cards = ""
    for i, p in enumerate(products, 1):
        name         = p.get("name", "")[:80]
        price        = p.get("price", 0)
        orig_price   = p.get("original_price", price)
        discount     = p.get("discount_pct", 0)
        rating       = p.get("rating", 0)
        reviews      = p.get("review_count", 0)
        image_url    = p.get("image_url", "")
        affiliate_url = p.get("affiliate_url", p.get("flipkart_url", "#"))
        content      = p.get("content", {})
        summary      = content.get("summary", f"Great {niche} deal at amazing price!")
        keywords     = content.get("keywords", [])

        # Star rating HTML
        full_stars  = int(rating)
        empty_stars = 5 - full_stars
        stars_html  = "★" * full_stars + "☆" * empty_stars

        # Savings amount
        savings = int(orig_price - price)

        # Badge color based on discount
        if discount >= 80:
            badge_color = "#e53935"
        elif discount >= 60:
            badge_color = "#f57c00"
        else:
            badge_color = "#388e3c"

        product_cards += f"""
        <div class="product-card" id="product-{i}">
            <div class="product-rank">#{i}</div>
            <div class="product-image-wrap">
                <img src="{image_url}"
                     alt="{name}"
                     class="product-image"
                     loading="lazy"
                     onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'"/>
                <div class="discount-badge" style="background:{badge_color}">
                    {int(discount)}% OFF
                </div>
            </div>
            <div class="product-info">
                <h2 class="product-name">{name}</h2>
                <p class="product-summary">{summary}</p>

                <div class="price-row">
                    <span class="current-price">₹{int(price):,}</span>
                    <span class="original-price">₹{int(orig_price):,}</span>
                    <span class="savings">You save ₹{savings:,}!</span>
                </div>

                {"<div class='rating-row'><span class='stars'>" + stars_html + "</span><span class='review-count'>(" + str(reviews) + " reviews)</span></div>" if rating > 0 else ""}

                {"<div class='keywords'>" + " ".join(f"<span class='tag'>#{k}</span>" for k in keywords[:4]) + "</div>" if keywords else ""}

                <a href="{affiliate_url}"
                   class="buy-button"
                   target="_blank"
                   rel="noopener noreferrer"
                   onclick="trackClick('{slug}', {i}, '{name[:30]}')">
                    🛒 Buy Now at ₹{int(price):,}
                </a>

                <p class="disclaimer">
                    ⚡ Limited time offer · Price may change · Opens on Flipkart
                </p>
            </div>
        </div>
        """

    # Build table of contents
    toc_items = ""
    for i, p in enumerate(products, 1):
        name = p.get("name", "")[:50]
        toc_items += f'<li><a href="#product-{i}">#{i} {name}</a></li>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{page_title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Inter', sans-serif;
            background: #f8f9fa;
            color: #1a1a2e;
            line-height: 1.6;
        }}

        /* Header */
        .site-header {{
            background: linear-gradient(135deg, #e91e63, #c2185b);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .site-header .logo {{
            font-size: 14px;
            opacity: 0.85;
            margin-bottom: 8px;
        }}
        .site-header h1 {{
            font-size: clamp(20px, 4vw, 32px);
            font-weight: 700;
            line-height: 1.3;
        }}
        .site-header .subtitle {{
            margin-top: 8px;
            font-size: 14px;
            opacity: 0.9;
        }}
        .updated-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
        }}

        /* Container */
        .container {{
            max-width: 860px;
            margin: 0 auto;
            padding: 20px 16px;
        }}

        /* Intro */
        .intro-box {{
            background: white;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 24px;
            border-left: 4px solid #e91e63;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .intro-box h2 {{
            font-size: 18px;
            margin-bottom: 10px;
            color: #e91e63;
        }}
        .intro-box p {{
            font-size: 14px;
            color: #555;
        }}

        /* TOC */
        .toc {{
            background: white;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 28px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .toc h3 {{
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #333;
        }}
        .toc ol {{
            padding-left: 20px;
        }}
        .toc li {{
            margin-bottom: 6px;
        }}
        .toc a {{
            color: #e91e63;
            text-decoration: none;
            font-size: 13px;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}

        /* Product Card */
        .product-card {{
            background: white;
            border-radius: 16px;
            margin-bottom: 28px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            overflow: hidden;
            position: relative;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .product-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}

        .product-rank {{
            position: absolute;
            top: 12px;
            left: 12px;
            background: #1a1a2e;
            color: white;
            font-weight: 700;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 20px;
            z-index: 2;
        }}

        .product-image-wrap {{
            position: relative;
            background: #f5f5f5;
            text-align: center;
            padding: 20px;
        }}
        .product-image {{
            width: 100%;
            max-width: 280px;
            height: 240px;
            object-fit: contain;
            border-radius: 8px;
        }}
        .discount-badge {{
            position: absolute;
            top: 12px;
            right: 12px;
            color: white;
            font-weight: 700;
            font-size: 13px;
            padding: 6px 12px;
            border-radius: 20px;
        }}

        .product-info {{
            padding: 20px 24px 24px;
        }}
        .product-name {{
            font-size: 17px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        .product-summary {{
            font-size: 13px;
            color: #666;
            margin-bottom: 14px;
            line-height: 1.5;
        }}

        .price-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}
        .current-price {{
            font-size: 24px;
            font-weight: 700;
            color: #e91e63;
        }}
        .original-price {{
            font-size: 15px;
            color: #999;
            text-decoration: line-through;
        }}
        .savings {{
            font-size: 12px;
            background: #e8f5e9;
            color: #2e7d32;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 500;
        }}

        .rating-row {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 12px;
        }}
        .stars {{
            color: #f59e0b;
            font-size: 15px;
            letter-spacing: 1px;
        }}
        .review-count {{
            font-size: 12px;
            color: #888;
        }}

        .keywords {{
            margin-bottom: 16px;
        }}
        .tag {{
            display: inline-block;
            background: #fce4ec;
            color: #c2185b;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 10px;
            margin: 2px;
        }}

        .buy-button {{
            display: block;
            background: linear-gradient(135deg, #e91e63, #c2185b);
            color: white !important;
            text-decoration: none;
            text-align: center;
            padding: 14px 24px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            margin-top: 16px;
            transition: opacity 0.2s;
        }}
        .buy-button:hover {{
            opacity: 0.9;
        }}

        .disclaimer {{
            font-size: 11px;
            color: #aaa;
            text-align: center;
            margin-top: 10px;
        }}

        /* Footer */
        .site-footer {{
            background: #1a1a2e;
            color: #aaa;
            text-align: center;
            padding: 24px 16px;
            font-size: 12px;
            margin-top: 40px;
        }}
        .site-footer a {{ color: #e91e63; text-decoration: none; }}

        /* Responsive */
        @media (min-width: 600px) {{
            .product-card {{
                display: grid;
                grid-template-columns: 280px 1fr;
            }}
            .product-image-wrap {{
                border-right: 1px solid #f0f0f0;
            }}
        }}
    </style>
</head>
<body>

<header class="site-header">
    <div class="logo">🛍️ DealPicks Blog</div>
    <h1>Top {len(products)} {niche} Deals<br>You Can't Miss in {datetime.now().year}</h1>
    <p class="subtitle">Handpicked deals with up to 93% OFF · Updated daily</p>
    <div class="updated-badge">📅 Updated: {today}</div>
</header>

<div class="container">

    <div class="intro-box">
        <h2>Why Trust Our Picks?</h2>
        <p>
            We analyse hundreds of {niche.lower()} listings on Flipkart every day,
            scoring each product on discount percentage, customer ratings, and review count.
            Only the top {len(products)} make it to this list. Every link is an affiliate link —
            meaning we earn a small commission at <strong>no extra cost to you</strong>.
            Prices shown are accurate at time of publishing.
        </p>
    </div>

    <div class="toc">
        <h3>📋 Quick Navigation</h3>
        <ol>
            {toc_items}
        </ol>
    </div>

    {product_cards}

    <div class="intro-box" style="margin-top:32px">
        <h2>💡 Buying Tips</h2>
        <p>
            ✅ Check size/colour options before buying &nbsp;·&nbsp;
            ✅ Read the top 3 customer reviews &nbsp;·&nbsp;
            ✅ Look for "Flipkart Assured" badge for faster delivery &nbsp;·&nbsp;
            ✅ Prices may change — grab deals while they last!
        </p>
    </div>

</div>

<footer class="site-footer">
    <p>© {datetime.now().year} DealPicks Blog · Affiliate Disclosure: We earn commission on purchases.</p>
    <p style="margin-top:6px">
        <a href="#">Home</a> · <a href="#">Privacy Policy</a> · <a href="#">Contact</a>
    </p>
</footer>

<script>
function trackClick(niche, rank, name) {{
    console.log('Click:', niche, rank, name);
    // Add Google Analytics / Facebook Pixel here if needed
}}
// Smooth scroll for TOC links
document.querySelectorAll('a[href^="#"]').forEach(a => {{
    a.addEventListener('click', e => {{
        e.preventDefault();
        document.querySelector(a.getAttribute('href'))
                ?.scrollIntoView({{ behavior: 'smooth' }});
    }});
}});
</script>
</body>
</html>"""

    return html


def save_blog(niche: str, products: list[dict]) -> str:
    """Generate and save blog HTML. Returns file path."""
    html     = generate_blog_html(niche, products)
    slug     = niche.lower().replace(" ", "-")
    filename = f"{slug}.html"
    filepath = os.path.join(BLOG_OUTPUT_DIR, filename)

    os.makedirs(BLOG_OUTPUT_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Blog saved: {filepath}")
    return filepath


def generate_index(all_niches: list[dict]) -> str:
    """Generate an index page listing all blog posts."""
    cards = ""
    for n in all_niches:
        cards += f"""
        <a href="posts/{n['slug']}.html" class="niche-card">
            <div class="niche-emoji">{n.get('emoji','🛍️')}</div>
            <div class="niche-title">{n['niche']}</div>
            <div class="niche-count">{n['count']} deals</div>
        </a>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DealPicks — Best Affiliate Deals on Flipkart</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* {{ box-sizing:border-box; margin:0; padding:0 }}
body {{ font-family:'Inter',sans-serif; background:#f8f9fa; color:#1a1a2e }}
.header {{ background:linear-gradient(135deg,#e91e63,#c2185b); color:white; text-align:center; padding:40px 20px }}
.header h1 {{ font-size:28px; font-weight:700 }}
.header p {{ margin-top:8px; opacity:.9; font-size:14px }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:16px; max-width:900px; margin:32px auto; padding:0 16px }}
.niche-card {{ background:white; border-radius:12px; padding:20px; text-align:center; text-decoration:none; color:#1a1a2e; box-shadow:0 2px 8px rgba(0,0,0,.08); transition:transform .2s }}
.niche-card:hover {{ transform:translateY(-3px) }}
.niche-emoji {{ font-size:32px; margin-bottom:8px }}
.niche-title {{ font-weight:600; font-size:14px }}
.niche-count {{ font-size:12px; color:#e91e63; margin-top:4px }}
.footer {{ text-align:center; padding:24px; font-size:12px; color:#aaa; margin-top:20px }}
</style>
</head>
<body>
<div class="header">
    <h1>🛍️ DealPicks</h1>
    <p>Best deals on Flipkart — updated daily</p>
</div>
<div class="grid">{cards}</div>
<div class="footer">© {datetime.now().year} DealPicks · Affiliate Disclosure</div>
</body>
</html>"""

    index_path = "blog/index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Index saved: {index_path}")
    return index_path


# ── Quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Sample products to test blog generation
    sample_products = [
        {
            "name": "Ark Jewel Combo 9 Pair Stunning White Gold Plated Pearl Alloy Hoop Earring",
            "price": 123,
            "original_price": 999,
            "discount_pct": 87,
            "rating": 4.2,
            "review_count": 1250,
            "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/earring/r/c/1/na-pi031926-2-ark-jewel-original-imahhpym6fw9c7gb.jpeg",
            "flipkart_url": "https://www.flipkart.com/ark-jewel-combo",
            "affiliate_url": "https://fkrt.co/lX8YuS",
            "content": {
                "summary": "Stunning 9-pair gold plated earring combo set",
                "keywords": ["gold earrings", "combo set", "affordable", "trendy"],
                "cta": "Shop Now →",
            }
        },
        {
            "name": "Bohemian Sunflower Hook Earrings For Women And Girls",
            "price": 265,
            "original_price": 1501,
            "discount_pct": 82,
            "rating": 4.0,
            "review_count": 890,
            "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/earring/r/c/1/na-pi031926-2-ark-jewel-original-imahhpym6fw9c7gb.jpeg",
            "flipkart_url": "https://www.flipkart.com/bohemian-earrings",
            "affiliate_url": "https://fkrt.co/sample2",
            "content": {
                "summary": "Trendy bohemian sunflower design earrings",
                "keywords": ["bohemian", "sunflower", "hook earrings", "women"],
                "cta": "Buy Now →",
            }
        },
    ]

    filepath = save_blog("Earrings", sample_products)
    print(f"\nBlog generated! Open this file in your browser:")
    print(f"  {os.path.abspath(filepath)}")