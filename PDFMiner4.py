
# pip install pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams, LTTextContainer
# from pdfminer.layout import LAParams, LTTextContainer, LTContainer, LTTextBox, LTTextLine, LTChar

# pip install pdfrw
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

# pip install reportlab
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

# pip install PyPDF2
from PyPDF2 import PdfReader as PR2 # 名前が上とかぶるので別名を使用

import time

#============================================================================
#  浮動小数点数値を表しているかどうかを判定する関数
#============================================================================
def isfloat(s):  
    try:
        float(s)  # 文字列を実際にfloat関数で変換してみる
    except ValueError:
        return False
    else:
        return True

#============================================================================
#  整数を表しているかどうかを判定する関数
#============================================================================
def isint(s):  
    try:
        int(s)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False
    else:
        return True


#============================================================================
#  プログラムの開始
#============================================================================

time_sta = time.time() # 開始時刻の記録


# 源真ゴシック等幅フォント
GEN_SHIN_GOTHIC_MEDIUM_TTF = "/Library/Fonts/GenShinGothic-Monospace-Medium.ttf"
# IPAexゴシックフォント
IPAEXG_TTF = "/Library/Fonts/ipaexg.ttf"

# フォント登録
pdfmetrics.registerFont(TTFont('GenShinGothic', GEN_SHIN_GOTHIC_MEDIUM_TTF))
pdfmetrics.registerFont(TTFont('ipaexg', IPAEXG_TTF))
print(pdfmetrics.getRegisteredFontNames())

# 対象PDFファイル設定
pdf_file = './サンプル計算書(1).pdf'
# 検出結果ファイル設定
pdf_out_file = 'サンプル計算書(1)[検索結果].pdf'

# PyPDF2のツールを使用してPDFのページ情報を読み取る。
with open(pdf_file, "rb") as input:
    reader = PR2(input)
    PageMax = len(reader.pages)     # PDFのページ数
    PaperSize = []
    for page in reader.pages:       # 各ページの用紙サイズの読取り
        p_size = page.mediabox
        x0 = page.mediabox.lower_left[0]
        y0 = page.mediabox.lower_left[1]
        x1 = page.mediabox.upper_right[0]
        y1 = page.mediabox.upper_right[1]
        PaperSize.append([x1 - x0 , y1 - y0])


# PDFMinerのツールの準備
resourceManager = PDFResourceManager()
device = PDFPageAggregator(resourceManager, laparams=LAParams())

startpage = 30      # 検索を開始する最初のページ
endpage = PageMax   # 検索を終了する最後のページ

pageResultData = []
# pageText = []
pageNo = []
limit1 = 0.70
limit2 = 0.40

with open(pdf_file, 'rb') as fp:
    interpreter = PDFPageInterpreter(resourceManager, device)
    pageI = 0
            
    for page in PDFPage.get_pages(fp):
        pageI += 1

        # text = []
        ResultData = []
        print("page={}:".format(pageI), end="")
        if pageI == 1 :
            pageFlag = True
            
        else:
            if pageI < startpage:
                print()
                continue
            if pageI > endpage:
                break
            # print(pageI)
            pageFlag = False

            interpreter.process_page(page)
            layout = device.get_result()

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
                continue
            else:
                print(mode)

            
            if mode == "検定比図" or mode == "柱の検定表" or mode == "梁の検定表": 
                
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
                                        # text.append(d2)
                                        ResultData.append([a,[xx0, yy0, width2, height2],False])
                                        flag = True
                                        pageFlag = True

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
                                        # text.append(c1)
                                        ResultData.append([c1,[xx0, yy0, width2, height2],True])
                                        pageFlag = True

        if pageFlag : 
            pageNo.append(pageI)
            # pageText.append(text)
            pageResultData.append(ResultData)

device.close()
# print(pageText)

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
    ResultData = pageResultData[pageI]
    # PDFデータへのページデータの展開
    pp = pagexobj(page) #ページデータをXobjへの変換
    rl_obj = makerl(cc, pp) # ReportLabオブジェクトへの変換  
    cc.doForm(rl_obj) # 展開

    if pageN == 1:
        cc.setFillColor("red")
        font_name = "ipaexg"
        cc.setFont(font_name, 20)
        cc.drawString(20 * mm,  pageSizeY - 40 * mm, "検定比（{}以上）の検索結果".format(limit1))
    else:
        pn = len(ResultData)
        cc.setFillColor("red")
        font_name = "ipaexg"
        cc.setFont(font_name, 12)
        t2 = "検索個数 = {}".format(pn)
        cc.drawString(20 * mm,  pageSizeY - 15 * mm, t2)
        for R1 in ResultData:
            a = R1[0]
            origin = R1[1]
            flag = R1[2]
            x0 = origin[0]
            y0 = origin[1]
            width = origin[2]
            height = origin[3]

            # 長方形の描画
            cc.setFillColor("white", 0.5)
            cc.setStrokeColorRGB(1.0, 0, 0)
            cc.rect(x0, y0, width, height, fill=0)

            if flag:
                cc.setFillColor("red")
                font_name = "ipaexg"
                cc.setFont(font_name, 7)
                t2 = " {:.2f}".format(a)
                cc.drawString(origin[0]+origin[2], origin[1]+origin[3], t2)

    # ページデータの確定
    cc.showPage()

# PDFの保存
cc.save()

t1 = time.time() - time_sta
print("time = {} sec".format(t1))