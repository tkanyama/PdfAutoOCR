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
# from pdfminer.layout import LAParams, LTTextContainer,LTChar
from pdfminer.layout import LAParams, LTTextContainer, LTContainer, LTTextBox, LTTextLine, LTChar

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

def isint(s):  # 整数を表しているかどうかを判定
    try:
        int(s)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False
    else:
        return True

# def find_textboxes(layout_obj):
#     if isinstance(layout_obj, LTTextBox):
#         return [layout_obj]
#     if isinstance(layout_obj, LTContainer):
#         boxes = []
#         for child in layout_obj:
#             boxes.extend(find_textboxes(child))
#         return boxes
#     return []

# def find_textlines(layout_obj):
#     if isinstance(layout_obj, LTTextLine):
#         return [layout_obj]
#     if isinstance(layout_obj, LTTextBox):
#         lines = []
#         for child in layout_obj:
#             lines.extend(find_textlines(child))
#         return lines
#     return []

# def find_characters(layout_obj):
#     if isinstance(layout_obj, LTChar):
#         return [layout_obj]
#     if isinstance(layout_obj, LTTextLine):
#         characters = []
#         for child in layout_obj:
#             characters.extend(find_characters(child))
#         return characters
#     return []

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

startpage = 242
# endpage = PageMax
# endpage = 182
endpage = 246

pageText = []
pageOrigin = []
pageCoefN = []
pageCoef = []
pageCoefOrigin = []
pageNo = []
limit1 = 0.95
limit2 = 0.40

with open(pdf_file, 'rb') as fp:
    interpreter = PDFPageInterpreter(resourceManager, device)
    pageI = 0
            
    for page in PDFPage.get_pages(fp):
        pageI += 1
        CoefN = []
        Coef = []
        CoefOrigin = []

        text = []
        origin = []
        print("page={}:".format(pageI), end="")
        if pageI == 1 :
            # print(pageI)
            pageFlag = True
            # kFlag = True
            # mFlag = True
        else:
            if pageI < startpage:continue
            if pageI > endpage:break
            # print(pageI)
            pageFlag = False
            # kFlag = False
            # mFlag = False

            interpreter.process_page(page)
            layout = device.get_result()
            # boxes = find_textboxes(layout)
            # for box in boxes:
            #     print(box.get_text())

            QDL_Flag = False
            検定表_Flag = False
            柱_Flag = False
            梁_Flag = False
            壁_Flag = False
            検定比図_Flag = False
            mode = ""
            for lt in layout:
                # LTTextContainerの場合だけ標準出力
                if isinstance(lt, LTTextContainer):
                    texts = lt.get_text()
                    # print(texts)
                    # if "QDL" in texts:
                    #     QDL_Flag = True
                    # if "検定表" in texts :
                    #     検定表_Flag = True
                    if "柱の断面検定表"in texts :
                        柱_Flag = True
                    if  "梁の断面検定表"in texts:
                        梁_Flag = True
                    if "壁の断面検定表"in texts :
                        壁_Flag = True
                    if "検定比図"in texts:
                        検定比図_Flag = True
                
            if 検定比図_Flag:
                mode = "検定比図"
            if 柱_Flag :
                mode = "柱の検定表"
            if 梁_Flag :
                mode = "梁の検定表"
            if 壁_Flag :
                mode = "壁の検定表"
        
            if mode == "" :
                print("Pass")
                # pageCoefN.append(CoefN)
                # pageCoef.append(Coef)
                # pageCoefOrigin.append(CoefOrigin)
                continue
            else:
                print(mode)

            
            if mode == "検定比図" or mode == "柱の検定表" or mode == "梁の検定表": 
                # kFlag = False
                # mFlag = False     
                
                for lt in layout:
                    # LTTextContainerの場合だけ標準出力
                    if isinstance(lt, LTTextContainer):
                        
                        words = lt.get_text()
                        datas = lt.get_text().splitlines()
                        data2 = [] 
                        if mode == "検定比図":
                            for data in datas:                          
                                data2.append(data.split())

                        elif mode == "柱の検定表":        
                            if "検定比" in words:
                                for data in datas:
                                    data2.append(data.split())
                                    
                        else:        
                            if "検定比" in words:
                                for data in datas:
                                    if "検定比" in data:
                                        data2.append(data.split())
                                    else:
                                        data2.append([""])

                        words = lt.get_text().split()
                        x0 = lt.x0
                        x1 = lt.x1
                        y0 = lt.y0
                        y1 = lt.y1
                        width = lt.width
                        height = lt.height


                        flag = False
                        i = 0
                        n1 = 0
                        for data in data2:
                            if not("QAL" in data or "QAS" in data):
                                n1 += 1
                        # n1 = len(data2)
                        n2 = 0
                        for d1 in data2:
                            if len(d1) > n2 : n2 = len(d1)

                        for d1 in data2:
                            if not("QAL" in d1 or "QAS" in d1):
                                i += 1
                            j = 0
                            
                            for d2 in d1:
                                j += 1
                                if j > n2 : j=n2
                                t = d2.replace("(","").replace(")","")
                                if isfloat(t) or isint(t):
                                    a = float(t)
                                    if a >= limit1 and a < 1.0 :
                                        xx0 = x0 + (j-1)*width/n2
                                        if mode == "柱の検定表" and j == 1 : 
                                            xx0 += 5.0
                                        yy0 = y1 - height * i / n1
                                        height2 = height / n1
                                        if height2 < 7.0 : height2 = 7.0
                                        width2 =  width/n2
                                        text.append(d2)
                                        origin.append([xx0, yy0, width2, height2])
                                        flag = True
                                        pageFlag = True
                                        CoefN.append(False)
                                        Coef = [[0.0]]
                                        CoefOrigin = [[0.0,0.0]]

                        if flag :
                            # print("-------")
                            # print(datas)
                            print("-------")
                            print('{}, x0={:.2f}, x1={:.2f}, y0={:.2f}, y1={:.2f}, width={:.2f}, height={:.2f}'.format(
                                lt.get_text().strip(), lt.x0, lt.x1, lt.y0, lt.y1, lt.width, lt.height))
                            print("-------")
                
            elif mode == "壁の検定表":
                # print("壁")
                QGL_Mode = False
                for lt in layout:
                    # LTTextContainerの場合だけ標準出力
                    if isinstance(lt, LTTextContainer):
                        data0 = lt.get_text()
                        # print(data0)
                        if QGL_Mode == False:
                            if "QDL" in data0:

                                datas = data0.splitlines()
                                
                                QDL_x0 = lt.x0
                                QDL_x1 = lt.x1
                                QDL_y0 = lt.y0
                                QDL_y1 = lt.y1
                                QDL_width = lt.width
                                QDL_height = lt.height
                                QGL_Mode = True
                        else:
                            datas = data0.splitlines()
                            x0 = lt.x0
                            x1 = lt.x1
                            y0 = lt.y0
                            y1 = lt.y1
                            width = lt.width
                            height = lt.height

                            if len(datas) == 4 and y0 == QDL_y0 and y1 == QDL_y1:
                                x = []
                                QGL_Mode = False
                                for data in datas:
                                    t = data.split()[0]
                                    t = t.replace("(","").replace(")","")
                                    if isint(t) or isfloat(t):
                                        a = float(t)
                                        x.append(a)
                                
                                c = []
                                if x[1] != 0:
                                    c.append(abs(x[0]/x[1]))
                                else:
                                    c.append(0.0)

                                if x[3] != 0:
                                    c.append(abs(x[2]/x[3]))
                                else:
                                    c.append(0.0)

                                i = 0
                                for c1 in c:
                                    i += 1
                                    if c1 >= limit2 and c1 < 1.0 :
                                        xx0 = QDL_x0
                                        yy0 = QDL_y1 - QDL_height * i / 2
                                        height2 = QDL_height / 2
                                        if height2 < 7.0 : height2 = 7.0
                                        width2 = x1 - QDL_x0
                                        text.append(c1)
                                        origin.append([xx0, yy0, width2, height2])
                                        pageFlag = True
                                        CoefN.append(True)
                                        Coef.append(c1)
                                        CoefOrigin.append([ xx0 + width2 , yy0 + height2 ])

                            # flag = False
                            # i=0
                            # n1 = len(data2)
                            # n2 = 0
                            # for d1 in data2:
                            #     if len(d1) > n2 : n2 = len(d1)

                            # for d1 in data2:
                            #     i += 1
                            #     j = 0
                                
                            #     for d2 in d1:
                            #         # if "QDL" in d2:
                            #         #     print(d2)

                            #         # if "検定比" in d2:
                            #         #     kFlag = True
                            #         # if "柱"in d2 or "梁"in d2 or "壁"in d2 or "検定比図"in d2:
                            #         #     mFlag = True
                                    

                            #         j += 1
                            #         t = d2.replace("(","").replace(")","")
                            #         if isfloat(t):
                            #             a = float(t)
                            #             if a >= limit and a < 1.0 :
                            #                 xx0 = x0 + (j-1)*width/n2
                            #                 yy0 = y1 - height * i / n1
                            #                 height2 = height / n1
                            #                 if height2 < 7.0 : height2 = 7.0
                            #                 width2 =  width/n2
                            #                 text.append(d2)
                            #                 origin.append([xx0, yy0, width2, height2])
                            #                 flag = True
                            #                 pageFlag = True

                            # if flag :
                            #     print("-------")
                            #     print(datas)
                            #     print("-------")
                            #     print('{}, x0={:.2f}, x1={:.2f}, y0={:.2f}, y1={:.2f}, width={:.2f}, height={:.2f}'.format(
                            #         lt.get_text().strip(), lt.x0, lt.x1, lt.y0, lt.y1, lt.width, lt.height))
                            #     print("-------")

        # pageCoefN.append(CoefN)
        # pageCoef.append(Coef)
        # pageCoefOrigin.append([])
                

        if pageFlag : # and kFlag and mFlag:
            pageNo.append(pageI)
            pageText.append(text)
            pageOrigin.append(origin)

            if CoefN:
                pageCoefN.append(CoefN)
                pageCoef.append(Coef)
                pageCoefOrigin.append(CoefOrigin)


device.close()
print(pageText)

in_path = pdf_file
out_path = pdf_out_file

# 保存先PDFデータを作成
cc = canvas.Canvas(out_path)
cc.setLineWidth(1)
# PDFを読み込む
pdf = PdfReader(in_path, decompress=False)

i = 0
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
        cc.drawString(20 * mm,  pageSizeY - 40 * mm, "検定比（{}以上）の検索結果".format(limit1))
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

        
        CoefN2 = pageCoefN[pageI]
        if CoefN2:
            Coef2 = pageCoef[pageI]
            origin2 = pageCoefOrigin[pageI]
            j = 0
            for c1 in Coef2:
                j += 1
                origin3 = origin2[j-1]
                cc.setFillColor("red")
                font_name = "ipaexg"
                cc.setFont(font_name, 8)
                t2 = "C={:.2f}".format(c1)
                cc.drawString(origin3[0],  origin3[1], t2)

    # ページデータの確定
    cc.showPage()

# PDFの保存
cc.save()

t1 = time.time() - time_sta
print("time = {} sec".format(t1))