from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tkinter as tk
from tkinter import filedialog
import io
import os

basedir = os.path.dirname(__file__)

def create_watermark(text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    font_path = os.path.join(basedir, 'ipaexg.ttf')
    pdfmetrics.registerFont(TTFont('IPAexGothic', font_path))
    can.setFont('IPAexGothic', 12)  
    can.drawString(400, 50, text)  # 位置設定する
    # Examples:
    # can.setFont('IPAexGothic', 10)  # For Amazon kindle book
    # can.drawString(410, 755, text)  # For Amazon kindle book
    # can.setFont('IPAexGothic', 8)   # For Amazon
    # can.drawString(435, 753, text)  # For Amazon
    can.save()
    packet.seek(0)
    return PdfReader(packet)

def merge_pdfs(pdf_list, output, watermark_text):
    pdf_writer = PdfWriter()
    watermark = create_watermark(watermark_text)

    for pdf in pdf_list:
        pdf_reader = PdfReader(pdf)
        num_pages = len(pdf_reader.pages)

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            if watermark_text:
                page.merge_page(watermark.pages[0])
            pdf_writer.add_page(page)

    with open(output, 'wb') as out:
        pdf_writer.write(out)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    pdf_files = filedialog.askopenfilenames(
        title="PDFファイルを選択してください",
        filetypes=(("PDF files", "*.pdf"),)
    )

    if not pdf_files:
        print("ファイル選択できませんでした。")
        exit()

    output_pdf = filedialog.asksaveasfilename(
        title="保存先を選択してください",
        filetypes=(("PDF files", "*.pdf"),),
        defaultextension=".pdf"
    )

    watermark_text = '株式会社GA technologies'

    merge_pdfs(pdf_files, output_pdf, watermark_text)
