#!/usr/bin/env python3
"""Build Microsoft Word (.docx) of keybook Urdu pages and export to PDF via LibreOffice."""

from __future__ import annotations

import os
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_BREAK, WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

URDU_FONT = "Noto Nastaliq Urdu"
EN_FONT = "Times New Roman"


def _rtl_paragraph(paragraph) -> None:
    p_pr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    p_pr.append(bidi)


def _set_run_fonts(run, font_name: str) -> None:
    run.font.name = font_name
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.get_or_add_rFonts()
    r_fonts.set(qn("w:ascii"), font_name)
    r_fonts.set(qn("w:hAnsi"), font_name)
    r_fonts.set(qn("w:cs"), font_name)


def add_page_break(doc: Document) -> None:
    p = doc.add_paragraph()
    run = p.add_run()
    run.add_break(WD_BREAK.PAGE)


def add_heading_block(doc: Document, lines: list[tuple[str, str]], rtl: bool = True) -> None:
    """lines: list of (text, font) where font is URDU_FONT or EN_FONT."""
    for text, font in lines:
        p = doc.add_paragraph()
        if rtl:
            _rtl_paragraph(p)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        else:
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13 if font == URDU_FONT else 11)
        _set_run_fonts(run, font)
        p.paragraph_format.space_after = Pt(4)


def add_urdu_paragraph(doc: Document, text: str, size: float = 12, justify: bool = True) -> None:
    p = doc.add_paragraph()
    _rtl_paragraph(p)
    p.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY if justify else WD_PARAGRAPH_ALIGNMENT.RIGHT
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    run.font.size = Pt(size)
    _set_run_fonts(run, URDU_FONT)


def add_english_line(doc: Document, text: str, size: float = 10, align_right: bool = True) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT if align_right else WD_PARAGRAPH_ALIGNMENT.LEFT
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.italic = True
    _set_run_fonts(run, EN_FONT)
    p.paragraph_format.space_after = Pt(8)


def build_document() -> Document:
    doc = Document()
    for s in doc.sections:
        s.left_margin = s.right_margin = Pt(54)
        s.top_margin = s.bottom_margin = Pt(54)

    # ----- Page 1 -----
    add_heading_block(
        doc,
        [
            ("صفحہ ۱", URDU_FONT),
            ("دیانت و سچائی — حضور رسول اللہ ﷺ (باکس: ۱)", URDU_FONT),
        ],
    )
    add_english_line(doc, "Trustworthiness of the Holy Rasool ﷺ", size=11)

    p1 = [
        "حضرت محمد ﷺ نے اپنی زندہ مثال سے ثابت کیا کہ وہ سب سے زیادہ سچے اور دیانت دار انسان تھے۔ وہ ایک یتیم تھے، جنہوں نے اپنے چچا کے ساتھ تجارتی سرگرمیاں شروع کر دی تھیں لیکن بہت ہی کم وقت میں تمام لوگوں کے ساتھ دیانتداری اور انصاف پسندانہ برتاؤ کی وجہ سے وہ معروف اور عزت دار ہو گئے۔ ہر کوئی خواہ امیر ہو یا غریب، آپ کو صادق اور امین کے نام سے جانتا تھا۔",
        "جب حضرت محمد ﷺ ابھی جوان تھے تو خانہ کعبہ کو دوبارہ تعمیر کیا گیا۔ مکہ مکرمہ کے مختلف قبائل میں حجر اسود کو خانہ کعبہ میں اس کی جگہ پر رکھنے کا اعزاز حاصل کرنے پر جھگڑا ہوا۔ انہوں نے فیصلہ کیا کہ اگلی صبح خانہ کعبہ میں سب سے پہلے داخل ہونے والا تنازعہ طے کرے گا۔ اس صبح سب سے پہلے حضرت محمد ﷺ داخل ہوئے اور جب لوگوں نے آپ کو دیکھا تو سب بہت خوش ہوئے کہ امین اور صادق آئے ہیں اور فیصلہ کرنے والے وہی ہوں گے۔ اس نے حجر اسود کو ایک کپڑے پر رکھا تاکہ ہر قبیلہ اس کپڑے کو تھامے اور اس پتھر کو اٹھانے میں مدد کر سکے، جسے آپ ﷺ نے اپنی جگہ پر رکھ دیا۔",
        'ایک دفعہ قریش کے سردار بیٹھے رسول اللہ ﷺ کے بارے میں باتیں کر رہے تھے۔ نضر بن حارث جو ان سب میں سب سے زیادہ تجربہ کار تھے، نے کہا: "اے قریش! آپ پر جو آفت آئی ہے اس سے نمٹنے کے لیے آپ کو کوئی منصوبہ نہیں مل سکا۔ محمد ﷺ آپ کی موجودگی میں پلے بڑھے۔ وہ تم میں سب سے زیادہ پسندیدہ، دیانت دار اور دیانت دار تھے۔ اب جب وہ بالغ ہو گئے اور یہ چیزیں آپ کے سامنے پیش کر دیں تو آپ کہتے ہیں کہ وہ جادوگر ہے، کاہن ہے، شاعر ہے، دیوانہ ہے۔ اللہ کی قسم! میں نے اس کا پیغام سنا ہے، وہ ان چیزوں میں سے کوئی نہیں ہے۔ تم پر ایک نئی آفت آئی ہے۔"',
    ]
    for t in p1:
        add_urdu_paragraph(doc, t)
    add_urdu_paragraph(doc, "(ابن ہشام، 1/299)", size=11, justify=False)

    add_page_break(doc)

    # ----- Book page 3 (Koh Safa) -----
    add_heading_block(doc, [("صفحہ ۳", URDU_FONT)])
    add_english_line(doc, "Spark English Keybook Class 8", size=10)

    add_urdu_paragraph(
        doc,
        "رسول اللہ صلی اللہ علیہ وآلہ وسلم نے ایک مرتبہ تمام اہل قریش کو کوہ صفا کے پاس جمع کیا اور ان سے پوچھا:",
        justify=False,
    )
    p2_b1 = (
        "اے قریش! اگر میں یہ کہوں کہ پہاڑوں کے پیچھے سے ایک لشکر تم پر پیش قدمی کر رہا ہے تو کیا تم میری بات مانو گے؟ سب نے ایک آواز میں کہا، "
        '"ہاں، کیونکہ ہم نے آپ کو کبھی جھوٹ بولتے نہیں سنا۔" (صحیح بخاری ۴۳۴۷، ۷۰۲) تمام مکہ والوں نے بغیر کسی استثناء کے آپ کی سچائی اور دیانتداری کی قسم کھائی کیونکہ آپ نے چالیس سال تک ان کے درمیان بے عیب اور انتہائی پرہیزگاری کی زندگی بسر کی۔ پھر بھی ان میں سے اکثر نے آپ کو اللہ کا رسول ماننے سے انکار کر دیا۔'
    )
    p2_b2 = "آپ نے اپنی پوری زندگی ان کے درمیان پاکیزگی اور نیکی کے ساتھ گزاری تھی اور اس کا اعتراف ان کے سخت ترین دشمنوں نے بھی کیا۔ انہوں نے ہمیشہ اسے اپنے درمیان سب سے زیادہ ایماندار اور سچا شخص تسلیم کیا۔"
    add_urdu_paragraph(doc, p2_b1)
    add_urdu_paragraph(doc, p2_b2)

    add_page_break(doc)

    # ----- Book page 11 -----
    add_heading_block(
        doc,
        [
            ("صفحہ ۱۱", URDU_FONT),
            ("باب ۲ — A Great Mountaineer (باکس: ۲)", URDU_FONT),
        ],
    )
    add_english_line(doc, "Spark English Keybook Class 8", size=10)

    naila = [
        "نائلہ کیانی کا معروف کوہ پیما بننے کا سفر عزم، ہمت اور کوہ پیمائی کے جذبے کی ایک شاندار کہانی ہے۔ ہمالیہ میں واقع ایک چھوٹے سے گاؤں میں پیدا ہونے والی نائلہ کی اپنے گھر کے آس پاس کی بلند و بالا چوٹیوں سے محبت چھوٹی عمر سے ہی عیاں تھی۔",
        "بچپن میں، وہ اکثر اپنے والد کے ساتھ، جو کہ ایک مقامی گائیڈ کے طور پر کام کرتے تھے، بیابان میں پیدل سفر کرتے تھے۔ ان تجربات نے پہاڑوں کے ساتھ اس کی محبت کو مزید بڑھا دیا اور اس میں وہ مہارتیں پیدا کیں جو سخت الپائن ماحول میں زندہ رہنے کے لیے درکار تھیں۔",
        "نائلہ کی ابتدائی جوانی اس کے گاؤں سے باہر کی دنیا کو تلاش کرنے کی خواہش سے نشان زد تھی۔ اس نے کوہ پیمائی اور مہم جوئی کے کھیلوں میں ڈگری حاصل کی، اپنے علاقے میں ایسا کرنے والی چند خواتین میں سے ایک بن گئی۔ سماجی دباؤ اور صنفی تعصب کا سامنا کرنے کے باوجود، وہ دنیا کی بلند ترین چوٹیوں کو فتح کرنے کے غیر متزلزل عزم کی وجہ سے غیر متزلزل رہی۔",
        "اس کی کامیابی اس وقت ہوئی جب اس نے اپنی پہلی ۸،۰۰۰ میٹر چوٹی کو کامیابی سے سر کیا۔ یہ کامیابی صرف ایک ذاتی فتح نہیں تھی بلکہ اس کی کمیونٹی میں خواتین کے لیے ایک سنگ میل تھی، جس نے بہت سے دوسرے لوگوں کو اپنے خوابوں کو پورا کرنے کی ترغیب دی۔ نائلہ اپنی حدوں کو آگے بڑھاتی رہی، آہستہ آہستہ مزید مشکل چوٹیوں کو فتح کرتی چلی گئی۔",
        "اس کے سب سے حیران کن کارناموں میں سے ایک ماؤنٹ ایورسٹ کو فتح کرنا تھا، جو کہ زمین کی بلند ترین چوٹی ہے۔ اس کامیابی نے ایک نڈر کوہ پیما کے طور پر اس کی ساکھ کو مستحکم کیا۔ نائلہ کی ماؤنٹ ایورسٹ کی چڑھائی چیلنجوں سے بھری ہوئی تھی۔ اسے موسمی حالات، برفانی تودے، اور انتہائی اونچائی کی بیماری کا سامنا کرنا پڑا، لیکن اس کے غیر متزلزل عزم نے اسے دیکھا۔",
        "نائلہ کیانی کی کہانی نہ صرف ذاتی فتح کی ہے بلکہ کوہ پیمائی کی دنیا میں صنفی دقیانوسی تصورات کو توڑنے کی بھی ہے۔ وہ اپنے علاقے کی نوجوان خواتین کے لیے ایک رول ماڈل بن گئی ہیں، جس نے ثابت کیا کہ جذبے اور استقامت سے کوئی بھی رکاوٹ کو عبور کر سکتا ہے۔",
        "آج، نائلہ خواہشمند کوہ پیماؤں کی حوصلہ افزائی اور رہنمائی کرتی رہتی ہیں، خاص طور پر نوجوان خواتین، انہیں اپنے خوابوں کی پیروی کرنے اور دنیا کی سب سے مضبوط چوٹیوں کو فتح کرنے کی",
    ]
    for t in naila:
        add_urdu_paragraph(doc, t, size=11)

    add_page_break(doc)

    # ----- Book page 12 -----
    add_heading_block(doc, [("صفحہ ۱۲", URDU_FONT), ("(جاری)", URDU_FONT)])
    add_english_line(doc, "Spark English Keybook Class 8", size=10)
    add_urdu_paragraph(
        doc,
        "ترغیب دیتی ہیں۔ اس کی کہانی ان لوگوں کے ناقابل تسخیر جذبے کے ثبوت کے طور پر کھڑی ہے جو خواب دیکھنے اور چوٹی تک پہنچنے کی ہمت کرتے ہیں، چاہے ان کے راستے میں رکاوٹیں کیوں نہ ہوں۔",
        size=11,
    )

    return doc


def export_pdf_with_libreoffice(docx_path: str, out_dir: str, pdf_basename: str) -> str:
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    cmd = [
        "soffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        out_dir,
        os.path.abspath(docx_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"LibreOffice failed: {r.stderr or r.stdout}")
    produced = os.path.join(out_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
    if not os.path.isfile(produced):
        raise FileNotFoundError(f"Expected PDF not found: {produced}")
    final_path = os.path.join(out_dir, pdf_basename)
    if produced != final_path:
        if os.path.isfile(final_path):
            os.remove(final_path)
        os.rename(produced, final_path)
    return final_path


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docx_path = os.path.join(root, "keybook_pages.docx")
    doc = build_document()
    doc.save(docx_path)
    print(docx_path)

    skip_pdf = "--no-pdf" in sys.argv
    if not skip_pdf:
        pdf_path = export_pdf_with_libreoffice(docx_path, root, "keybook_pages_word.pdf")
        print(pdf_path)


if __name__ == "__main__":
    main()
