import io
import os
import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tkinter as tk
from tkinter import filedialog, ttk

TEMPLATES = {
    "amazon": "Amazon（紙の書籍）",
    "kindle": "Amazon（Kindle）",
}


def get_working_dir():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the location of the bundle
        executable_dir = os.path.dirname(sys.executable)
    else:
        # If the application is run as a script, the location of the script
        executable_dir = os.path.dirname(os.path.abspath(__file__))
    return executable_dir


def create_watermark(text, template):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    basedir = os.path.dirname(__file__)
    font_path = os.path.join(basedir, 'ipaexg.ttf')
    pdfmetrics.registerFont(TTFont('IPAexGothic', font_path))
    if template == TEMPLATES['kindle']:
        can.setFont('IPAexGothic', 10)
        can.drawString(410, 755, text)
    elif template == TEMPLATES['amazon']:
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


def select_files(file_listbox: tk.Listbox):
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for path in file_paths:
        file_listbox.insert(tk.END, path)


def process_files(listbox: tk.Listbox, watermark: tk.StringVar, template: tk.StringVar, message: tk.StringVar):
    selected_indexes: tuple[int] = listbox.curselection()
    if not selected_indexes:
        messagebox.showwarning("No selection", "宛名を追加するページを最低1つ選択してください")

    pdf_writer = PdfWriter()
    watermark_pdf = create_watermark(watermark.get(), template.get())
    for i in range(listbox.size()):
        file_path: str = listbox.get(i)
        pdf_reader = PdfReader(file_path)

        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            if i in selected_indexes:
                page.merge_page(watermark_pdf.pages[0])
            pdf_writer.add_page(page)

    timestamp = int(time.time())
    output_path = Path(get_working_dir()) / f"receipt_{timestamp}.pdf"
    with open(output_path, 'wb') as out:
        pdf_writer.write(out)
    message.set(f"以下に保存されました：{output_path}")
    os.startfile(output_path)


def move_up(listbox: tk.Listbox):
    selected_indices = listbox.curselection()
    for index in selected_indices:
        if index > 0:
            file = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index - 1, file)
            listbox.select_set(index - 1)


def move_down(listbox: tk.Listbox):
    selected_indices = listbox.curselection()
    for index in reversed(selected_indices):
        if index < listbox.size() - 1:
            file = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index + 1, file)
            listbox.select_set(index + 1)


def get_selected_files(listbox: tk.Listbox) -> list[str]:
    selected_indexes: tuple[int] = listbox.curselection()
    selected_files = []
    for i in range(listbox.size()):
        if i in selected_indexes:
            selected_files.append(listbox.get(i))
    return selected_files


def on_select(event: tk.Event, label: tk.Label):
    selected_indexes: tuple[int] = event.widget.curselection()
    selected_files = [event.widget.get(i) for i in selected_indexes]
    label.config(text=f"宛名が付加されるファイル:\n{'\n'.join(selected_files)}")


if __name__ == '__main__':
    root = tk.Tk()
    root.title("領収書宛名追加くん")

    # 宛名の設定部分
    atena_frame = tk.Frame(root)
    atena_frame.pack(pady=10)
    label = tk.Label(atena_frame, text="宛名：")
    label.pack(pady=10, side=tk.LEFT)
    watermark = tk.StringVar(atena_frame, value="株式会社GA technologies")
    entry = tk.Entry(atena_frame, textvariable=watermark)
    entry.pack(pady=10, side=tk.RIGHT)

    # 宛名位置テンプレート選択
    template_frame = tk.Frame(root)
    template_frame.pack(pady=0)
    label = tk.Label(template_frame, text="宛名の位置のテンプレート：")
    label.pack(pady=10, side=tk.LEFT)

    template = tk.StringVar(template_frame)
    template.set(TEMPLATES["amazon"])
    template_dropdown = ttk.Combobox(template_frame, textvariable=template, values=list(TEMPLATES.values()))
    template_dropdown.pack(pady=10, side=tk.RIGHT)

    # ファイル選択
    files_frame = tk.Frame(root)
    files_frame.pack(pady=10)

    select_button = tk.Button(files_frame, text="PDFファイルを選択", command=lambda: select_files(file_listbox))
    select_button.pack()

    file_listbox = tk.Listbox(files_frame, selectmode=tk.MULTIPLE, width=50, height=10)
    file_listbox.pack(pady=10, side=tk.LEFT)

    button_frame = tk.Frame(files_frame)
    button_frame.pack(side=tk.RIGHT, fill=tk.Y)

    up_button = tk.Button(button_frame, text="↑", command=lambda: move_up(file_listbox))
    up_button.pack(fill=tk.X)

    down_button = tk.Button(button_frame, text="↓", command=lambda: move_down(file_listbox))
    down_button.pack(fill=tk.X)

    # ファイルを選ぶよう促す部分
    frame = tk.Frame(root)
    frame.pack(pady=0)
    label = tk.Label(frame, text="ファイル追加後、宛名を追加するページを選択してください")
    label.pack(pady=5)
    file_listbox.bind("<<ListboxSelect>>", lambda event: on_select(event, label))

    # 実行ボタン & 実行後のメッセージ
    execute_frame = tk.Frame(root)
    execute_frame.pack(pady=10)
    message = tk.StringVar(execute_frame)

    process_button = tk.Button(execute_frame, text="宛名追加 & pdf結合",
                               command=lambda: process_files(file_listbox, watermark, template, message))
    process_button.pack(pady=10)

    message_label = tk.Label(execute_frame, textvariable=message)
    message_label.pack(pady=5)

    root.mainloop()
