#!/usr/bin/env python3
"""Build sample textbook PDF pages (Urdu RTL) matching Spark English Keybook style."""

from __future__ import annotations

import os

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY

URDU_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoNastaliqUrdu-Regular.ttf"
URDU_FONT = "NotoNastaliqUrdu"


def ur(text: str) -> str:
    """Prepare Urdu for ReportLab (joining + bidirectional display order)."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def register_fonts() -> None:
    if not os.path.isfile(URDU_FONT_PATH):
        raise FileNotFoundError(f"Missing font: {URDU_FONT_PATH}")
    pdfmetrics.registerFont(TTFont(URDU_FONT, URDU_FONT_PATH))


def p_urdu(text: str, size: float = 12, leading: float | None = None, align=TA_RIGHT) -> Paragraph:
    if leading is None:
        leading = size * 1.35
    style = ParagraphStyle(
        name="ur",
        fontName=URDU_FONT,
        fontSize=size,
        leading=leading,
        alignment=align,
        rightIndent=0,
        leftIndent=0,
        wordWrap="RTL",  # type: ignore[arg-type]
    )
    # Escape for ReportLab mini-XML
    safe = ur(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style)


def build_pdf(path: str) -> None:
    register_fonts()
    w, h = A4
    margin_x = 18 * mm
    margin_y = 16 * mm
    bottom_reserve = 28 * mm  # room for drawn footers (not in flow)

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=margin_y,
        bottomMargin=margin_y + bottom_reserve,
    )

    story: list = []

    # ----- Page 1: Trustworthiness -----
    def on_page1(canv, _doc):
        canv.saveState()
        bar_h = 14 * mm
        y0 = h - margin_y - bar_h
        canv.setFillColorRGB(0.83, 0.83, 0.83)
        canv.rect(margin_x, y0, w - 2 * margin_x, bar_h, stroke=0, fill=1)
        box = 10 * mm
        canv.setFillColorRGB(0.29, 0.29, 0.29)
        canv.rect(margin_x, y0, box, bar_h, stroke=0, fill=1)
        canv.setFillColorRGB(1, 1, 1)
        canv.setFont("Helvetica-Bold", 12)
        canv.drawCentredString(margin_x + box / 2, y0 + bar_h / 2 - 4, "1")
        canv.setFillColorRGB(0, 0, 0)
        canv.setFont("Times-Bold", 11)
        title = "Trustworthiness of the Holy Rasool ﷺ"
        tw = canv.stringWidth(title, "Times-Bold", 11)
        canv.drawString((w - tw) / 2, y0 + bar_h / 2 - 4, title)
        canv.restoreState()

    p1_body = [
        "حضرت محمد ﷺ نے اپنی زندہ مثال سے ثابت کیا کہ وہ سب سے زیادہ سچے اور دیانت دار انسان تھے۔ وہ ایک یتیم تھے، جنہوں نے اپنے چچا کے ساتھ تجارتی سرگرمیاں شروع کر دی تھیں لیکن بہت ہی کم وقت میں تمام لوگوں کے ساتھ دیانتداری اور انصاف پسندانہ برتاؤ کی وجہ سے وہ معروف اور عزت دار ہو گئے۔ ہر کوئی خواہ امیر ہو یا غریب، آپ کو صادق اور امین کے نام سے جانتا تھا۔",
        "جب حضرت محمد ﷺ ابھی جوان تھے تو خانہ کعبہ کو دوبارہ تعمیر کیا گیا۔ مکہ مکرمہ کے مختلف قبائل میں حجر اسود کو خانہ کعبہ میں اس کی جگہ پر رکھنے کا اعزاز حاصل کرنے پر جھگڑا ہوا۔ انہوں نے فیصلہ کیا کہ اگلی صبح خانہ کعبہ میں سب سے پہلے داخل ہونے والا تنازعہ طے کرے گا۔ اس صبح سب سے پہلے حضرت محمد ﷺ داخل ہوئے اور جب لوگوں نے آپ کو دیکھا تو سب بہت خوش ہوئے کہ امین اور صادق آئے ہیں اور فیصلہ کرنے والے وہی ہوں گے۔ اس نے حجر اسود کو ایک کپڑے پر رکھا تاکہ ہر قبیلہ اس کپڑے کو تھامے اور اس پتھر کو اٹھانے میں مدد کر سکے، جسے آپ ﷺ نے اپنی جگہ پر رکھ دیا۔",
        "ایک دفعہ قریش کے سردار بیٹھے رسول اللہ ﷺ کے بارے میں باتیں کر رہے تھے۔ نضر بن حارث جو ان سب میں سب سے زیادہ تجربہ کار تھے، نے کہا: \"اے قریش! آپ پر جو آفت آئی ہے اس سے نمٹنے کے لیے آپ کو کوئی منصوبہ نہیں مل سکا۔ محمد ﷺ آپ کی موجودگی میں پلے بڑھے۔ وہ تم میں سب سے زیادہ پسندیدہ، دیانت دار اور دیانت دار تھے۔ اب جب وہ بالغ ہو گئے اور یہ چیزیں آپ کے سامنے پیش کر دیں تو آپ کہتے ہیں کہ وہ جادوگر ہے، کاہن ہے، شاعر ہے، دیوانہ ہے۔ اللہ کی قسم! میں نے اس کا پیغام سنا ہے، وہ ان چیزوں میں سے کوئی نہیں ہے۔ تم پر ایک نئی آفت آئی ہے۔\"",
    ]
    story.append(Spacer(1, 22 * mm))
    for para in p1_body:
        story.append(p_urdu(para, size=12, leading=18, align=TA_JUSTIFY))
        story.append(Spacer(1, 5 * mm))
    story.append(Spacer(1, 8 * mm))
    story.append(p_urdu("(ابن ہشام، 1/299)", size=11, align=TA_RIGHT))

    story.append(PageBreak())

    # ----- Page 2: Safa hadith -----
    p2_intro = "رسول اللہ صلی اللہ علیہ وآلہ وسلم نے ایک مرتبہ تمام اہل قریش کو کوہ صفا کے پاس جمع کیا اور ان سے پوچھا:"
    p2_b1 = (
        "اے قریش! اگر میں یہ کہوں کہ پہاڑوں کے پیچھے سے ایک لشکر تم پر پیش قدمی کر رہا ہے تو کیا تم میری بات مانو گے؟ سب نے ایک آواز میں کہا، "
        "\"ہاں، کیونکہ ہم نے آپ کو کبھی جھوٹ بولتے نہیں سنا۔\" (صحیح بخاری ۴۳۴۷، ۷۰۲) تمام مکہ والوں نے بغیر کسی استثناء کے آپ کی سچائی اور دیانتداری کی قسم کھائی کیونکہ آپ نے چالیس سال تک ان کے درمیان بے عیب اور انتہائی پرہیزگاری کی زندگی بسر کی۔ پھر بھی ان میں سے اکثر نے آپ کو اللہ کا رسول ماننے سے انکار کر دیا۔"
    )
    p2_b2 = (
        "آپ نے اپنی پوری زندگی ان کے درمیان پاکیزگی اور نیکی کے ساتھ گزاری تھی اور اس کا اعتراف ان کے سخت ترین دشمنوں نے بھی کیا۔ انہوں نے ہمیشہ اسے اپنے درمیان سب سے زیادہ ایماندار اور سچا شخص تسلیم کیا۔"
    )

    def on_page2(canv, _doc):
        canv.saveState()
        top = h - margin_y
        # thin decorative bars
        bw = w - 2 * margin_x
        x0 = margin_x
        y1 = top - 6 * mm
        canv.setFillColor(colors.black)
        canv.rect(x0 + 8 * mm, y1, bw - 8 * mm, 2 * mm, stroke=0, fill=1)
        y2 = y1 - 4 * mm
        path = canv.beginPath()
        path.moveTo(x0 + 18 * mm, y2)
        path.lineTo(x0 + bw, y2)
        path.lineTo(x0 + bw, y2 + 5 * mm)
        path.lineTo(x0 + 22 * mm, y2 + 5 * mm)
        path.close()
        canv.drawPath(path, stroke=0, fill=1)
        canv.setFont("Times-Roman", 9)
        canv.drawRightString(w - margin_x, top - 2 * mm, "Spark English Keybook Class 8    3")
        canv.restoreState()

    story.append(Spacer(1, 26 * mm))
    story.append(p_urdu(p2_intro, size=12, leading=20, align=TA_CENTER))
    story.append(Spacer(1, 14 * mm))
    story.append(p_urdu(p2_b1, size=12, leading=18, align=TA_JUSTIFY))
    story.append(Spacer(1, 4 * mm))
    story.append(p_urdu(p2_b2, size=12, leading=18, align=TA_JUSTIFY))

    story.append(PageBreak())

    # ----- Page 3: Naila Kiani (chapter 2) -----
    naila_page11 = [
        "نائلہ کیانی کا معروف کوہ پیما بننے کا سفر عزم، ہمت اور کوہ پیمائی کے جذبے کی ایک شاندار کہانی ہے۔ ہمالیہ میں واقع ایک چھوٹے سے گاؤں میں پیدا ہونے والی نائلہ کی اپنے گھر کے آس پاس کی بلند و بالا چوٹیوں سے محبت چھوٹی عمر سے ہی عیاں تھی۔",
        "بچپن میں، وہ اکثر اپنے والد کے ساتھ، جو کہ ایک مقامی گائیڈ کے طور پر کام کرتے تھے، بیابان میں پیدل سفر کرتے تھے۔ ان تجربات نے پہاڑوں کے ساتھ اس کی محبت کو مزید بڑھا دیا اور اس میں وہ مہارتیں پیدا کیں جو سخت الپائن ماحول میں زندہ رہنے کے لیے درکار تھیں۔",
        "نائلہ کی ابتدائی جوانی اس کے گاؤں سے باہر کی دنیا کو تلاش کرنے کی خواہش سے نشان زد تھی۔ اس نے کوہ پیمائی اور مہم جوئی کے کھیلوں میں ڈگری حاصل کی، اپنے علاقے میں ایسا کرنے والی چند خواتین میں سے ایک بن گئی۔ سماجی دباؤ اور صنفی تعصب کا سامنا کرنے کے باوجود، وہ دنیا کی بلند ترین چوٹیوں کو فتح کرنے کے غیر متزلزل عزم کی وجہ سے غیر متزلزل رہی۔",
        "اس کی کامیابی اس وقت ہوئی جب اس نے اپنی پہلی ۸،۰۰۰ میٹر چوٹی کو کامیابی سے سر کیا۔ یہ کامیابی صرف ایک ذاتی فتح نہیں تھی بلکہ اس کی کمیونٹی میں خواتین کے لیے ایک سنگ میل تھی، جس نے بہت سے دوسرے لوگوں کو اپنے خوابوں کو پورا کرنے کی ترغیب دی۔ نائلہ اپنی حدوں کو آگے بڑھاتی رہی، آہستہ آہستہ مزید مشکل چوٹیوں کو فتح کرتی چلی گئی۔",
        "اس کے سب سے حیران کن کارناموں میں سے ایک ماؤنٹ ایورسٹ کو فتح کرنا تھا، جو کہ زمین کی بلند ترین چوٹی ہے۔ اس کامیابی نے ایک نڈر کوہ پیما کے طور پر اس کی ساکھ کو مستحکم کیا۔ نائلہ کی ماؤنٹ ایورسٹ کی چڑھائی چیلنجوں سے بھری ہوئی تھی۔ اسے موسمی حالات، برفانی تودے، اور انتہائی اونچائی کی بیماری کا سامنا کرنا پڑا، لیکن اس کے غیر متزلزل عزم نے اسے دیکھا۔",
        "نائلہ کیانی کی کہانی نہ صرف ذاتی فتح کی ہے بلکہ کوہ پیمائی کی دنیا میں صنفی دقیانوسی تصورات کو توڑنے کی بھی ہے۔ وہ اپنے علاقے کی نوجوان خواتین کے لیے ایک رول ماڈل بن گئی ہیں، جس نے ثابت کیا کہ جذبے اور استقامت سے کوئی بھی رکاوٹ کو عبور کر سکتا ہے۔",
    ]
    naila_page11_tail = (
        "آج، نائلہ خواہشمند کوہ پیماؤں کی حوصلہ افزائی اور رہنمائی کرتی رہتی ہیں، خاص طور پر نوجوان خواتین، انہیں اپنے خوابوں کی پیروی کرنے اور دنیا کی سب سے مضبوط چوٹیوں کو فتح کرنے کی"
    )
    naila_page12 = (
        "ترغیب دیتی ہیں۔ اس کی کہانی ان لوگوں کے ناقابل تسخیر جذبے کے ثبوت کے طور پر کھڑی ہے جو خواب دیکھنے اور چوٹی تک پہنچنے کی ہمت کرتے ہیں، چاہے ان کے راستے میں رکاوٹیں کیوں نہ ہوں۔"
    )

    def draw_chapter_header(canv, chapter_num: str, title_en: str):
        canv.saveState()
        bar_h = 13 * mm
        y0 = h - margin_y - bar_h
        box_w = 9 * mm
        canv.setFillColorRGB(0.78, 0.78, 0.78)
        canv.rect(margin_x, y0, box_w, bar_h, stroke=0, fill=1)
        canv.setFillColorRGB(0.2, 0.2, 0.2)
        canv.setFont("Helvetica-Bold", 11)
        canv.drawCentredString(margin_x + box_w / 2, y0 + bar_h / 2 - 4, chapter_num)
        # dark banner with chevrons (approximate)
        bx = margin_x + box_w + 2 * mm
        bw = w - margin_x - bx - margin_x
        path = canv.beginPath()
        chev = 4 * mm
        path.moveTo(bx + chev, y0)
        path.lineTo(bx + bw - chev, y0)
        path.lineTo(bx + bw, y0 + bar_h / 2)
        path.lineTo(bx + bw - chev, y0 + bar_h)
        path.lineTo(bx + chev, y0 + bar_h)
        path.lineTo(bx, y0 + bar_h / 2)
        path.close()
        canv.setFillColorRGB(0.22, 0.22, 0.22)
        canv.drawPath(path, stroke=0, fill=1)
        canv.setFillColorRGB(1, 1, 1)
        canv.setFont("Times-Bold", 11)
        tw = canv.stringWidth(title_en, "Times-Bold", 11)
        canv.drawString(bx + (bw - tw) / 2, y0 + bar_h / 2 - 4, title_en)
        canv.restoreState()

    def on_page3(canv, doc):
        draw_chapter_header(canv, "2", "A Great Mountaineer")

    def footer11(canv, _doc):
        canv.saveState()
        fy = margin_y + bottom_reserve - 6 * mm
        canv.setStrokeColor(colors.black)
        canv.line(margin_x, fy + 6 * mm, w - margin_x, fy + 6 * mm)
        canv.setFont("Times-Roman", 9)
        ft = "Spark English Keybook Class 8"
        tw = canv.stringWidth(ft, "Times-Roman", 9)
        canv.drawString((w - tw) / 2 - 8 * mm, fy, ft)
        canv.drawRightString(w - margin_x, fy, "11")
        # thick bar with cutout
        bh = 5 * mm
        canv.setFillColor(colors.black)
        bar_y = margin_y + bottom_reserve - bh - 2 * mm
        canv.rect(margin_x, bar_y, w - 2 * margin_x, bh, stroke=0, fill=1)
        canv.setFillColor(colors.white)
        canv.rect(margin_x + 4 * mm, bar_y + 1 * mm, 14 * mm, bh - 2 * mm, stroke=0, fill=1)
        canv.restoreState()

    story.append(Spacer(1, 14 * mm))
    for para in naila_page11:
        story.append(p_urdu(para, size=10, leading=15, align=TA_JUSTIFY))
        story.append(Spacer(1, 2.5 * mm))
    story.append(p_urdu(naila_page11_tail, size=10, leading=15, align=TA_JUSTIFY))

    story.append(PageBreak())

    # ----- Page 4: continuation (book page 12) -----

    def on_page4(canv, _doc):
        canv.saveState()
        canv.setFillColor(colors.black)
        canv.rect(margin_x, h - margin_y - 8 * mm, w - 2 * margin_x, 8 * mm, stroke=0, fill=1)
        canv.restoreState()

    def footer12(canv, _doc):
        canv.saveState()
        fy = margin_y + bottom_reserve - 8 * mm
        canv.setFont("Times-Roman", 9)
        ft = "Spark English Keybook Class 8"
        canv.drawString((w - canv.stringWidth(ft, "Times-Roman", 9)) / 2 - 8 * mm, fy, ft)
        canv.drawRightString(w - margin_x, fy, "12")
        canv.restoreState()

    story.append(Spacer(1, 22 * mm))
    story.append(p_urdu(naila_page12, size=10, leading=15, align=TA_JUSTIFY))

    page_handlers = [
        (on_page1, None),
        (on_page2, None),
        (on_page3, footer11),
        (on_page4, footer12),
    ]

    def decorate_page(canv, doc, page_index: int):
        if page_index < len(page_handlers):
            hdr, ftr = page_handlers[page_index]
            if hdr:
                hdr(canv, doc)
            if ftr:
                ftr(canv, doc)

    page_index = {"i": 0}

    def on_first(canv, doc):
        decorate_page(canv, doc, 0)
        page_index["i"] = 1

    def on_later(canv, doc):
        decorate_page(canv, doc, page_index["i"])
        page_index["i"] += 1

    doc.build(story, onFirstPage=on_first, onLaterPages=on_later)


def main() -> None:
    out = os.path.join(os.path.dirname(__file__), "..", "keybook_pages.pdf")
    out = os.path.abspath(out)
    build_pdf(out)
    print(out)


if __name__ == "__main__":
    main()
