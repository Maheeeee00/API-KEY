#!/usr/bin/env python3
"""Generate NB SONS organic growth strategy PDF."""

from fpdf import FPDF


class StrategyPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, "NB SONS - Organic Growth Strategy 2026", align="L")
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def cover_page(self):
        self.add_page()
        self.ln(50)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(26, 92, 58)
        self.cell(0, 14, "NB SONS", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_font("Helvetica", "", 13)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, "Pakistan's Best Nutritional Supplement Brand", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(20)
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(30, 30, 30)
        self.cell(0, 12, "Organic Growth Strategy", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_font("Helvetica", "", 12)
        self.multi_cell(0, 7, "Zero-paid-ads roadmap to grow monthly revenue from Rs. 70,000+ to Rs. 200,000-350,000 within 6-12 months.", align="C")
        self.ln(30)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "nbsons.com  |  Facebook: nbsonspvtltd  |  Instagram: @nb.sons", align="C")
        self.ln(6)
        self.cell(0, 8, "June 2026", align="C")

    def slide_title(self, title, subtitle=""):
        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(26, 92, 58)
        self.multi_cell(0, 10, title)
        if subtitle:
            self.ln(2)
            self.set_font("Helvetica", "", 11)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 6, subtitle)
        self.ln(6)
        self.set_draw_color(45, 138, 94)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def section_heading(self, text):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(26, 92, 58)
        self.multi_cell(0, 7, text)
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def bullet_list(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        for item in items:
            x = self.get_x()
            self.cell(6, 6, "-")
            self.multi_cell(0, 6, item)
            self.ln(1)
        self.ln(2)

    def stat_row(self, stats):
        col_w = 46
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(26, 92, 58)
        y = self.get_y()
        for i, (num, label) in enumerate(stats):
            x = 10 + i * col_w
            self.set_xy(x, y)
            self.cell(col_w, 10, num, align="C")
        self.ln(12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(80, 80, 80)
        y = self.get_y()
        for i, (_, label) in enumerate(stats):
            x = 10 + i * col_w
            self.set_xy(x, y)
            self.multi_cell(col_w, 4, label, align="C")
        self.ln(8)

    def simple_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(26, 92, 58)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(245, 250, 247)
            else:
                self.set_fill_color(255, 255, 255)
            max_h = 8
            for i, cell in enumerate(row):
                self.cell(col_widths[i], max_h, cell, border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(4)

    def highlight_box(self, text):
        self.set_fill_color(255, 248, 225)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, text, fill=True)
        self.ln(4)


def build_pdf(output_path):
    pdf = StrategyPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.cover_page()

    # Executive Summary
    pdf.slide_title("Executive Summary", "Where you are today and where you can go - without paid ads")
    pdf.stat_row([
        ("70K+", "Current Monthly Revenue"),
        ("80", "Products on Shopify"),
        ("25+", "Years in Business"),
        ("Rs. 0", "Ad Budget Required"),
    ])
    pdf.highlight_box(
        "Core insight: NB SONS has strong foundations - manufacturing credibility, 80 SKUs, "
        "an active wellness blog, and nationwide distribution. The gap is traffic, conversion, "
        "and repeat purchase. This strategy uses 8 organic growth engines that compound over time."
    )
    pdf.simple_table(
        ["Timeline", "Revenue Target", "Primary Drivers"],
        [
            ["Month 1-3", "Rs. 100K - 130K", "Social, WhatsApp, CRO, reviews"],
            ["Month 4-6", "Rs. 150K - 220K", "SEO, email, referrals, bundles"],
            ["Month 7-12", "Rs. 200K - 350K", "Marketplace, B2B, influencers"],
        ],
        [35, 45, 110],
    )

    # Current State
    pdf.slide_title("Current Business Snapshot", "Strengths to leverage and gaps to close")
    pdf.section_heading("Strengths")
    pdf.bullet_list([
        "Established brand since 2000, Pvt Ltd since 2005, Lahore HQ + Sundar manufacturing",
        "80 products: men's vitality, women's health, maternal, digestive, iron, joint, brain",
        "Price range Rs. 220 to Rs. 4,700 - accessible entry and premium tiers",
        "Active wellness blog with SEO articles on health topics in Pakistan",
        "Free delivery on orders above Rs. 1,999",
        "cGMP manufacturing - strong trust signal",
        "Social presence on Facebook (nbsonspvtltd) and Instagram (@nb.sons)",
    ])
    pdf.section_heading("Growth Gaps")
    pdf.bullet_list([
        "Most bestsellers have 0-2 reviews (hurts conversion by 15-30%)",
        "Social content not systematically driving Shopify traffic",
        "No visible referral or loyalty program",
        "WhatsApp commerce underused - Pakistan's top D2C sales channel",
        "Email list not monetized with automation flows",
        "Seasonal sales only - no evergreen offer stack",
        "Not listed on Daraz or major health marketplaces",
    ])

    # 8 Engines
    pdf.slide_title("The 8-Engine Organic Growth Framework")
    engines = [
        ("1. Social Media Organic", "Reels, carousels, UGC on FB + IG driving link-in-bio traffic"),
        ("2. WhatsApp Commerce", "Catalog, broadcasts, order tracking - highest converting channel"),
        ("3. SEO and Blog", "Rank for supplement keywords in Pakistan - scale existing blog"),
        ("4. Email and SMS", "Welcome series, abandoned cart, post-purchase upsell"),
        ("5. Reviews and Trust", "Systematic review collection and customer stories"),
        ("6. Bundles and AOV", "Raise average order from ~Rs. 875 to Rs. 1,500+"),
        ("7. Referral and Loyalty", "Give Rs. 100, Get Rs. 100 - customers as salespeople"),
        ("8. B2B and Marketplace", "Pharmacies, clinics, Daraz - use nationwide distribution"),
    ]
    for title, desc in engines:
        pdf.section_heading(title)
        pdf.body_text(desc)
    pdf.highlight_box(
        "Formula: Revenue = (Traffic x Conversion x AOV) + (Repeat Customers x Frequency). "
        "Target: 3x traffic, 1.5x conversion, 1.7x AOV = ~7.6x revenue potential over 12 months."
    )

    # Social Media
    pdf.slide_title("Engine 1: Social Media Strategy", "Facebook + Instagram - your free traffic machine")
    pdf.section_heading("Content Mix (Post 1-2x daily on each platform)")
    pdf.bullet_list([
        "Educate (40%): Health tips, ingredient breakdowns, myth vs fact reels",
        "Relate (30%): Customer stories, factory BTS, doctor endorsements",
        "Convert (30%): Product spotlights, bundle offers, story shop links",
    ])
    pdf.simple_table(
        ["Day", "Instagram", "Facebook"],
        [
            ["Mon", "Reel - health tip + product", "Blog share + question"],
            ["Tue", "Carousel - product benefits", "Customer review post"],
            ["Wed", "Story poll", "Live Q&A (15 min)"],
            ["Thu", "Reel - factory/quality BTS", "Bundle offer"],
            ["Fri", "UGC repost", "Wellness blog link"],
            ["Sat", "Story - shop now tags", "Engagement post"],
            ["Sun", "Bestseller spotlight reel", "Testimonial video"],
        ],
        [20, 85, 85],
    )
    pdf.body_text("Goal: 10K+ Instagram and 15K+ Facebook followers in 6 months. Drive 500-1,000 monthly store visits.")

    # WhatsApp
    pdf.slide_title("Engine 2: WhatsApp Business Commerce")
    pdf.section_heading("Setup Checklist")
    pdf.bullet_list([
        "WhatsApp Business app with dedicated NB SONS number",
        "Product catalog with top 20 bestsellers",
        "Quick replies for price, delivery, dosage, COD",
        "Customer labels: New Lead, Ordered, Repeat, VIP",
        "WhatsApp button on every Shopify page + social bio links",
    ])
    pdf.section_heading("Sales Funnel")
    pdf.bullet_list([
        "Attract: Social media -> 'DM us for free health consultation'",
        "Engage: Ask about health concern -> recommend product",
        "Convert: Send catalog + COD confirmation -> Shopify draft order",
        "Retain: Day 7 check-in, Day 30 reorder with 10% loyalty discount",
    ])
    pdf.body_text("Expected: 30-50 WhatsApp orders/month at Rs. 1,200 AOV = Rs. 36K-60K extra revenue within 3 months.")

    # SEO
    pdf.slide_title("Engine 3: SEO and Content Marketing")
    pdf.section_heading("Target Keywords")
    pdf.body_text(
        "iron supplement Pakistan, PCOS supplement, male fertility supplement, "
        "breast milk increase, fiber supplement, magnesium glycinate Pakistan, "
        "digestive syrup, best multivitamin Pakistan, joint pain supplement"
    )
    pdf.section_heading("Action Plan")
    pdf.bullet_list([
        "Publish 2 SEO articles per week linking to products",
        "Fix meta titles on all 80 products with 'Pakistan' keyword",
        "Add FAQ sections on product pages",
        "Internal link blog posts to product pages",
        "Start YouTube channel - repurpose blog as 3-5 min videos",
    ])
    pdf.body_text("Expected by month 6: 2,000-5,000 organic visitors/month = Rs. 54K-135K/month from Google.")

    # Email
    pdf.slide_title("Engine 4: Email and SMS Marketing")
    pdf.section_heading("Automated Flows")
    pdf.bullet_list([
        "Welcome (3 emails): Brand story + 10% off, bestsellers guide, testimonials",
        "Abandoned cart (3 emails): 1hr reminder, 24hr social proof, 72hr free delivery offer",
        "Post-purchase (2 emails): Usage guide on Day 3, reorder offer on Day 21",
        "Weekly broadcast: Tuesday blog + product, Friday flash sale",
    ])
    pdf.body_text("Tools: Shopify Email (free), Klaviyo, or Mailchimp. Email can generate 15-20% of total revenue.")

    # Conversion & Bundles
    pdf.slide_title("Engine 5 and 6: Trust + Bundles")
    pdf.section_heading("Review Generation")
    pdf.bullet_list([
        "Post-delivery WhatsApp: 'Rate us -> Rs. 50 off next order'",
        "Review card with QR code in every package",
        "Target 50+ reviews on top 5 products in 60 days",
        "15% discount for 30-second video testimonials",
    ])
    pdf.section_heading("Recommended Bundles")
    pdf.simple_table(
        ["Bundle", "Products", "Price"],
        [
            ["Men's Vitality Pack", "X-FIT + Repro-M", "Rs. 1,999"],
            ["New Mom Care", "Greelac + Movin + Ferosim", "Rs. 1,799"],
            ["PCOS Wellness Kit", "Myo-Inositol + FEMEEZ + Iron", "Rs. 2,499"],
            ["Digestive Relief", "Fybosim + Eletcid + NB CAL", "Rs. 799"],
            ["Family Starter", "Asco-C + Calin-G + F.LIUM", "Rs. 899"],
        ],
        [55, 85, 50],
    )

    # Referral & B2B
    pdf.slide_title("Engine 7 and 8: Referral + B2B Expansion")
    pdf.section_heading("NB SONS Wellness Circle (Loyalty Program)")
    pdf.bullet_list([
        "Refer a friend: both get Rs. 100 off",
        "Repeat purchase: 10% off 2nd order, 15% off 3rd+",
        "Points: Rs. 10 spent = 1 point, 100 points = Rs. 100 off",
        "Use Shopify app: Smile.io or LoyaltyLion",
    ])
    pdf.section_heading("B2B and Marketplace")
    pdf.bullet_list([
        "Month 3-4: List top 15 products on Daraz.pk",
        "Partner with pharmacies - 20-25% margin for stocking",
        "Sample packs for gynecologists and urologists",
        "Corporate wellness packages for Lahore/Karachi companies",
    ])

    # 90 Day Plan
    pdf.slide_title("90-Day Action Plan")
    pdf.section_heading("Month 1: Foundation (Target: Rs. 95K-110K)")
    pdf.bullet_list([
        "WhatsApp Business + catalog + Shopify button",
        "Daily IG/FB posting schedule",
        "Email automation (welcome + abandoned cart)",
        "Create 5 product bundles",
        "Review collection campaign + SEO meta title fixes",
    ])
    pdf.section_heading("Month 2: Acceleration (Target: Rs. 120K-150K)")
    pdf.bullet_list([
        "8 new blog articles, referral program launch",
        "Weekly WhatsApp broadcasts, first Instagram Live",
        "10 micro-influencer barter partnerships",
        "YouTube channel + 4 videos",
    ])
    pdf.section_heading("Month 3: Scale (Target: Rs. 150K-180K)")
    pdf.bullet_list([
        "Daraz store launch, 20 pharmacy outreach contacts",
        "Loyalty program live, UGC content contest",
        "Urdu Reels series, health blogger guest posts",
    ])

    # Revenue Projection
    pdf.slide_title("Revenue Projection Model")
    pdf.simple_table(
        ["Month", "Orders", "AOV", "Revenue", "Growth"],
        [
            ["Current", "~80", "Rs. 875", "Rs. 70,000", "-"],
            ["Month 1", "~100", "Rs. 950", "Rs. 95,000", "+36%"],
            ["Month 2", "~130", "Rs. 1,000", "Rs. 130,000", "+86%"],
            ["Month 3", "~160", "Rs. 1,050", "Rs. 168,000", "+140%"],
            ["Month 6", "~200", "Rs. 1,100", "Rs. 220,000", "+214%"],
            ["Month 12", "~280", "Rs. 1,250", "Rs. 350,000", "+400%"],
        ],
        [30, 30, 35, 45, 30],
    )
    pdf.body_text("Conservative estimates. Biggest risk is inconsistent execution, not competition.")

    # KPIs
    pdf.slide_title("KPIs to Track Weekly")
    pdf.simple_table(
        ["Metric", "Current", "90-Day Target"],
        [
            ["Monthly Revenue", "Rs. 70,000", "Rs. 150,000+"],
            ["Orders/Month", "~80", "160+"],
            ["Average Order Value", "Rs. 875", "Rs. 1,050+"],
            ["Conversion Rate", "~1.5%", "2.5%+"],
            ["Repeat Purchase Rate", "~10%", "25%+"],
            ["Instagram Followers", "Current", "+2,000"],
            ["Website Sessions", "Low", "5,000/month"],
            ["WhatsApp Inquiries", "Low", "200+/month"],
            ["Product Reviews (Top 5)", "0-2 each", "50+ each"],
        ],
        [70, 55, 65],
    )

    # Quick Wins
    pdf.slide_title("10 Quick Wins - Do This Week (Rs. 0 Cost)")
    pdf.bullet_list([
        "Add WhatsApp chat button to every page on nbsons.com",
        "Update Instagram bio with clear order CTA and free delivery message",
        "Pin top 3 bestsellers on Facebook and Instagram with shop links",
        "Enable abandoned cart emails in Shopify settings",
        "Create Men's Vitality Pack bundle (X-FIT + Repro-M at Rs. 1,999)",
        "WhatsApp last 50 customers for reviews - offer 10% off",
        "Add clickable free delivery banner on homepage",
        "Post 1 Reel today - phone video with product benefits text",
        "Link all blog articles to relevant product pages",
        "Set up Google Search Console and submit sitemap",
    ])
    pdf.highlight_box("Combined impact of these 10 actions: +Rs. 15,000-25,000/month within 30 days.")

    # Closing
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(26, 92, 58)
    pdf.cell(0, 12, "Your Path Forward", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 8, "You don't need ads. You need systems.\n\nWhatsApp + Social + Email + Reviews + Bundles + SEO = compounding growth on your 25-year legacy.", align="C")
    pdf.ln(20)
    pdf.stat_row([
        ("Rs. 70K", "Today"),
        ("Rs. 170K", "90 Days"),
        ("Rs. 350K", "12 Months"),
    ])
    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "nbsons.com  |  @nb.sons  |  Wellness for Life", align="C")

    pdf.output(output_path)
    print(f"PDF saved to {output_path}")


if __name__ == "__main__":
    build_pdf("/workspace/presentations/NB-SONS-Organic-Growth-Strategy.pdf")
