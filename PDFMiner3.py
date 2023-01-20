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
from reportlab.lib.units import mm
import time

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

startpage = 30
endpage = 666

pageText = []
pageOrigin = []
pageNo = []
limit = 0.95
with open('./サンプル計算書(1).pdf', 'rb') as fp:
    interpreter = PDFPageInterpreter(resourceManager, device)
    pageI = 0

    for page in PDFPage.get_pages(fp):
        pageI += 1
        if pageI < startpage:continue
        if pageI > endpage:break
        print(pageI)
        pageFlag = False
        kFlag = False
        mFlag = False

        text = []
        origin = []
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

in_path = "サンプル計算書(1).pdf"
out_path = "サンプル計算書(1)のコピー.pdf"

# 保存先PDFデータを作成
cc = canvas.Canvas(out_path)
cc.setLineWidth(1)
# PDFを読み込む
pdf = PdfReader(in_path, decompress=False)

for pageI in range(len(pageNo)):
    pageN = pageNo[pageI]
    page = pdf.pages[pageN - 1]
    origins = pageOrigin[pageI]
    # PDFデータへのページデータの展開
    pp = pagexobj(page) #ページデータをXobjへの変換
    rl_obj = makerl(cc, pp) # ReportLabオブジェクトへの変換  
    cc.doForm(rl_obj) # 展開
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