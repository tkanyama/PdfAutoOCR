# import io
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.converter import PDFPageAggregator
# from pdfminer.pdfpage import PDFPage
# from pdfminer.layout import LAParams

# resourceManager = PDFResourceManager()
# # 引数にLAParamsを追加
# device = PDFPageAggregator(resourceManager, laparams=LAParams())

# with open('./page179.pdf', 'rb') as fp:
#     interpreter = PDFPageInterpreter(resourceManager, device)
#     for page in PDFPage.get_pages(fp):
#         interpreter.process_page(page)
#         layout = device.get_result()
#         for lt in layout:
#             print('{}, x0={:.2f}, x1={:.2f}, y0={:.2f}, y1={:.2f}, width={:.2f}, height={:.2f}'.format(
#                     lt.get_text().strip(), lt.x0, lt.x1, lt.y0, lt.y1, lt.width, lt.height))
# device.close()

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams, LTTextContainer,LTChar

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
import time
import PyPDF2.papersizes
from PyPDF2 import PdfReader as PR2
import copy

def isfloat(s):  # 浮動小数点数値を表しているかどうかを判定
    try:
        float(s)  # 文字列を実際にfloat関数で変換してみる
    except ValueError:
        return False
    else:
        return True

time_sta = time.time()

resourceManager = PDFResourceManager()
device = PDFPageAggregator(resourceManager, laparams=LAParams())

GEN_SHIN_GOTHIC_MEDIUM_TTF = "/Library/Fonts/GenShinGothic-Monospace-Medium.ttf"
IPAEXG_TTF = "/Library/Fonts/GenShinGothic-Monospace-Medium.ttf"

# フォント登録
pdfmetrics.registerFont(TTFont('GenShinGothic', GEN_SHIN_GOTHIC_MEDIUM_TTF))
pdfmetrics.registerFont(TTFont('ipaexg', IPAEXG_TTF))
print(pdfmetrics.getRegisteredFontNames())

# font_size = 20
# c.setFont('GenShinGothic', font_size)

# PRG2: 対象PDFファイル設定
pdf_file = './サンプル計算書(1).pdf'
pdf_out_file = 'サンプル計算書(1)のコピー.pdf'

with open(pdf_file, "rb") as input:
    reader = PR2(input)
    PageMax = len(reader.pages)
    PaperSize = []
    for page in reader.pages:
        p_size = page.mediabox
        x0 = page.mediabox.lower_left[0]
        y0 = page.mediabox.lower_left[1]
        x1 = page.mediabox.upper_right[0]
        y1 = page.mediabox.upper_right[1]
        PaperSize.append([x1 - x0 , y1 - y0])

    # pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    # for i in range(pdf_reader.getNumPages()):
    #     # 同じページのオブジェクトを２つ用意
    #     p1 = pdf_reader.getPage(i)
    #     p2 = copy.copy(p1)
    #     # 原稿の左下と右上の座標を取得（用紙サイズ）
    #     x0 = p1.mediaBox.getLowerLeft_x()
    #     y0 = p1.mediaBox.getLowerLeft_y()
    #     x1 = p1.mediaBox.getUpperRight_x()
    #     y1 = p1.mediaBox.getUpperRight_y()
    #     for page in range(PageMax):
    #         p = reader.getPage(page+1)
    #         p_size = p.mediaBox
    #         p_width = p_size.getWidth()
    #         p_height = p_size.getHeight()
    #         print(f'\nページ{page+1}')
    #         print('RectangleObject: ', p_size)
    #         print('幅　: ', p_width, 'pt')
    #         print('高さ: ', p_height, 'pt')

startpage = 30
endpage = PageMax
# endpage = 200

pageText = []
pageOrigin = []
pageNo = []
limit = 0.95

with open(pdf_file, 'rb') as fp:
    interpreter = PDFPageInterpreter(resourceManager, device)
    pageI = 0

    for page in PDFPage.get_pages(fp):
        pageI += 1
            
        text = []
        origin = []
        if pageI == 1 :
            print(pageI)
            pageFlag = True
            kFlag = True
            mFlag = True
        else:
            if pageI < startpage:continue
            if pageI > endpage:break
            print(pageI)
            pageFlag = False
            kFlag = False
            mFlag = False

            interpreter.process_page(page)
            layout = device.get_result()
            for lt in layout:
                # LTTextContainerの場合だけ標準出力
                if isinstance(lt, LTTextContainer):
                    datas = lt.get_text().splitlines()
                    data2 = []
                    for data in datas:
                        data2.append(data.split())

                    words = lt.get_text().split()
                    x0 = lt.x0
                    x1 = lt.x1
                    y0 = lt.y0
                    y1 = lt.y1
                    width = lt.width
                    height = lt.height
                    
                    flag = False
                    i=0
                    n1 = len(data2)
                    n2 = 0
                    for d1 in data2:
                        if len(d1) > n2 : n2 = len(d1)

                    for d1 in data2:
                        i += 1
                        j = 0
                        
                        for d2 in d1:
                            if "検定比" in d2:
                                kFlag = True
                            if "柱"in d2 or "梁"in d2 or "壁"in d2 or "検定比図"in d2:
                                mFlag = True
                            

                            j += 1
                            t = d2.replace("(","").replace(")","")
                            if isfloat(t):
                                a = float(t)
                                if a >= limit and a < 1.0 :
                                    xx0 = x0 + (j-1)*width/n2
                                    yy0 = y1 - height * i / n1
                                    height2 = height / n1
                                    if height2 < 7.0 : height2 = 7.0
                                    width2 =  width/n2
                                    text.append(d2)
                                    origin.append([xx0, yy0, width2, height2])
                                    flag = True
                                    pageFlag = True

                    # i = 0
                    # n = len(words)
                    
                    # for word in words:
                    #     i += 1
                    #     t = word.replace("(","").replace(")","")
                    #     if isfloat(t):
                    #         a = float(t)
                    #         if a >= limit and a < 1.0 :
                    #             xx0 = x0
                    #             yy0 = y1 - height * i / n
                    #             height2 = height / n
                    #             if height2 < 7:height2=7
                    #             width2 = width
                    #             text.append(word)
                    #             origin.append([xx0, yy0, width2, height2])
                    #             flag = True
                    #             pageFlag = True
                                
                        
                    if flag :
                        print("-------")
                        print(datas)
                        print("-------")
                        print('{}, x0={:.2f}, x1={:.2f}, y0={:.2f}, y1={:.2f}, width={:.2f}, height={:.2f}'.format(
                            lt.get_text().strip(), lt.x0, lt.x1, lt.y0, lt.y1, lt.width, lt.height))
                        print("-------")

                    # # t = t.replace("\n",",")
                    #     print(t)
                    #     print('{}, x0={:.2f}, x1={:.2f}, y0={:.2f}, y1={:.2f}, width={:.2f}, height={:.2f}'.format(
                    #             lt.get_text().strip(), lt.x0, lt.x1, lt.y0, lt.y1, lt.width, lt.height))
                        
                        # text.append(words2)
                        # origin.append([lt.x0, lt.x1, lt.y0, lt.y1, lt.width, lt.height])
        if pageFlag and kFlag and mFlag:
            pageNo.append(pageI)
            pageText.append(text)
            pageOrigin.append(origin)

device.close()
print(pageText)

in_path = pdf_file
out_path = pdf_out_file

# 保存先PDFデータを作成
cc = canvas.Canvas(out_path)
cc.setLineWidth(1)
# PDFを読み込む
pdf = PdfReader(in_path, decompress=False)

for pageI in range(len(pageNo)):
    pageN = pageNo[pageI]
    pageSizeX = float(PaperSize[pageN-1][0])
    pageSizeY = float(PaperSize[pageN-1][1])
    page = pdf.pages[pageN - 1]
    origins = pageOrigin[pageI]
    # PDFデータへのページデータの展開
    pp = pagexobj(page) #ページデータをXobjへの変換
    rl_obj = makerl(cc, pp) # ReportLabオブジェクトへの変換  
    cc.doForm(rl_obj) # 展開

    if pageN == 1:
        cc.setFillColor("red")
        font_name = "ipaexg"
        cc.setFont(font_name, 24)
        cc.drawString(20 * mm,  pageSizeY - 40 * mm, "検定比m（{}以上の検索結果".format)
    else:
        pn = len(origins)
        cc.setFillColor("red")
        font_name = "ipaexg"
        cc.setFont(font_name, 16)
        t2 = "検索個数 = {}".format(pn)
        cc.drawString(20 * mm,  pageSizeY - 15 * mm, t2)
        for origin in origins:
            x0 = origin[0]
            y0 = origin[1]
            width = origin[2]
            height = origin[3]

            # 長方形の描画
            cc.setFillColor("white", 0.5)
            cc.setStrokeColorRGB(1.0, 0, 0)
            cc.rect(x0, y0, width, height, fill=0)
    
    # ページデータの確定
    cc.showPage()

# PDFの保存
cc.save()

t1 = time.time() - time_sta
print("time = {} sec".format(t1))