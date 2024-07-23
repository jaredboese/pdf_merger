from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tkinter as tk
from tkinter import filedialog, ttk
import io
import os

basedir = os.path.dirname(__file__)

def create_watermark(text, template):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    font_path = os.path.join(basedir, 'ipaexg.ttf')
    pdfmetrics.registerFont(TTFont('IPAexGothic', font_path))
    if template == 'kindle':
        can.setFont('IPAexGothic', 10)
        can.drawString(410, 755, text)
    elif template == 'amazon':
        can.setFont('IPAexGothic', 8)
        can.drawString(435, 753, text)
    else:
        can.setFont('IPAexGothic', 12)  
        can.drawString(400, 50, text)

    can.save()
    packet.seek(0)
    return PdfReader(packet)

def merge_pdfs(pdf_list, output, watermark_text, template):
    pdf_writer = PdfWriter()
    watermark = create_watermark(watermark_text, template)

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

def select_template():
    template_root = tk.Tk()
    template_root.withdraw()
    template_root.title("Select Template")

    template_var = tk.StringVar(template_root)
    template_var.set("Select Template")

    templates = ["default", "kindle", "amazon"]

    template_dropdown = ttk.Combobox(template_root, textvariable=template_var, values=templates)
    template_dropdown.pack(pady=20)
    template_dropdown.bind("<<ComboboxSelected>>", lambda event: template_root.quit())

    template_root.deiconify()
    template_root.mainloop()

    return template_var.get()

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

    template = select_template()

    if not template:
        print("テンプレートが選択されませんでした。")
        exit()

    output_pdf = filedialog.asksaveasfilename(
        title="保存先を選択してください",
        filetypes=(("PDF files", "*.pdf"),),
        defaultextension=".pdf"
    )

    watermark_text = '株式会社GA technologies'

    merge_pdfs(pdf_files, output_pdf, watermark_text, template)
