from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTContainer, LTTextBox, LTTextLine, LTChar
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

def isfloat(s):  # 浮動小数点数値を表しているかどうかを判定
    try:
        float(s)  # 文字列を実際にfloat関数で変換してみる
    except ValueError:
        return False
    else:
        return True

def pdfminer_config(line_overlap, word_margin, char_margin,line_margin, detect_vertical):
    laparams = LAParams(line_overlap=line_overlap,
                        word_margin=word_margin,
                        char_margin=char_margin,
                        line_margin=line_margin,
                        detect_vertical=detect_vertical)
    resource_manager = PDFResourceManager()
    device = PDFPageAggregator(resource_manager, laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, device)
    return (interpreter, device)

def find_textboxes(layout_obj):
    if isinstance(layout_obj, LTTextBox):
        return [layout_obj]
    if isinstance(layout_obj, LTContainer):
        boxes = []
        for child in layout_obj:
            boxes.extend(find_textboxes(child))
        return boxes
    return []

def find_textlines(layout_obj):
    if isinstance(layout_obj, LTTextLine):
        return [layout_obj]
    if isinstance(layout_obj, LTTextBox):
        lines = []
        for child in layout_obj:
            lines.extend(find_textlines(child))
        return lines
    return []

def find_characters(layout_obj):
    if isinstance(layout_obj, LTChar):
        return [layout_obj]
    if isinstance(layout_obj, LTTextLine):
        characters = []
        for child in layout_obj:
            characters.extend(find_characters(child))
        return characters
    return []

def write_text(text_file, text):
    text_file.write(text)

text_file = open('output.txt', 'w')
with open("./page179.pdf", 'rb') as f:
    interpreter, device = pdfminer_config(line_overlap=0.5, word_margin=0.1, char_margin=2, line_margin=0.5, detect_vertical=True)
    i = 0
    for page in PDFPage.get_pages(f):
        interpreter.process_page(page)  # ページを処理する。
        layout = device.get_result()  # LTPageオブジェクトを取得。
        boxes = find_textboxes(layout)
        for box in boxes:
            t = box.get_text().strip()
            # t = t.replace("・","")
            write_text(text_file, t)
        
        i += 1
        if i>5 :
            break

text_file.close()