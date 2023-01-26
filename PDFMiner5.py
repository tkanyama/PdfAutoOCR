
# pip install pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
# from pdfminer.layout import LAParams, LTTextContainer
from pdfminer.layout import LAParams, LTTextContainer, LTContainer, LTTextBox, LTTextLine, LTChar

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

import numpy as np

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
# PDFから単語を取得するためのデバイス
device = PDFPageAggregator(resourceManager, laparams=LAParams())
# PDFから１文字ずつを取得するためのデバイス
device2 = PDFPageAggregator(resourceManager)

startpage = 552     # 検索を開始する最初のページ
# endpage = PageMax   # 検索を終了する最後のページ
endpage = 557

pageResultData = []
# pageText = []
pageNo = []
limit1 = 0.70
limit2 = 0.40

with open(pdf_file, 'rb') as fp:
    interpreter = PDFPageInterpreter(resourceManager, device)
    interpreter2 = PDFPageInterpreter(resourceManager, device2)
    pageI = 0
            
    for page in PDFPage.get_pages(fp):
        pageI += 1

        # text = []
        ResultData = []
        mode = ""
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
#
#   このページに「柱の断面検定表」、「梁の断面検定表」、「壁の断面検定表」、「検定比図」の
#   文字が含まれている場合のみ数値の検索を行う。
#
            QDL_Flag = False
            検定表_Flag = False
            柱_Flag = False
            梁_Flag = False
            壁_Flag = False
            杭_Flag = False
            検定比図_Flag = False
            mode = ""
            for lt in layout:
                # LTTextContainerの場合だけ標準出力　断面算定表(杭基礎)
                if isinstance(lt, LTTextContainer):
                    texts = lt.get_text()
                    if "柱の断面検定表"in texts :
                        柱_Flag = True
                        break
                    if  "梁の断面検定表"in texts:
                        梁_Flag = True
                        break
                    if "壁の断面検定表"in texts :
                        壁_Flag = True
                        break
                    if "断面算定表"in texts and "杭基礎"in texts:
                        杭_Flag = True
                        break
                    if "検定比図"in texts:
                        検定比図_Flag = True
                        break
                
            if 検定比図_Flag:
                mode = "検定比図"
            if 柱_Flag :
                mode = "柱の検定表"
            if 梁_Flag :
                mode = "梁の検定表"
            if 壁_Flag :
                mode = "壁の検定表"
            if 杭_Flag :
                mode = "杭の検定表"
        
            if mode == "" :     # 該当しない場合はこのページの処理は飛ばす。
                print("No Data")
                continue
            else:
                print(mode)

            
            if mode == "検定比図" or mode == "柱の検定表" or mode == "梁の検定表" :
                
                for lt in layout:
                    # LTTextContainerの場合だけ標準出力
                    if isinstance(lt, LTTextContainer):
                        
                        words = lt.get_text()
                        datas = lt.get_text().splitlines()
                        data2 = [] 
                        if mode == "検定比図" :
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

                        # words = lt.get_text().split()
                        x0 = lt.x0
                        x1 = lt.x1
                        y0 = lt.y0
                        y1 = lt.y1
                        width = lt.width
                        height = lt.height

                        flag = False

                        val = 0
                        for d1 in data2:
                            
                            for d2 in d1:
                                t = d2.replace("(","").replace(")","")
                                if isfloat(t) or isint(t):
                                    a = float(t)
                                    if a >= limit1 and a < 1.0 :
                                        ResultData.append([a,[x0, y0, width, height],False])
                                        flag = True
                                        pageFlag = True
                                        val = a

                        if flag : # 数値を検出した場合にPrint
                            print('val={:.2f}'.format(val))
                            
                
            elif mode == "壁の検定表":
                # print("壁")
                QGL_Mode = False
                for lt in layout:
                    # LTTextContainerの場合だけ標準出力
                    if isinstance(lt, LTTextContainer):
                        data0 = lt.get_text()
                        # print(data0)
                        flag = False
                        val = 0
                        if QGL_Mode == False:
                            if "QDL" in data0 or "QAL" in data0 or "QDS" in data0 or "QAS" in data0:

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
                                        # ResultData.append([a,[x0, y0, x1, y1],False])
                                        pageFlag = True
                                        flag = True
                                        val = c1
                        
                        if flag :   # 数値を検出した場合にPrint
                            print('val={:.2f}'.format(val))

            if mode == "杭の検定表":
                pageFlaf = False


        if pageFlag : 
            pageNo.append(pageI)
            
            # 表紙および壁以外のページの場合、数値の正確な座標を特定するために、１文字ずつの確認を行う

            ResultData2 = []
                
            if mode != "壁の検定表" and pageI > 1:
            #
            #   mode == "検定比図" or mode == "柱の検定表" or mode == "梁の検定表"
            #
                # １文字ずつ検出するためのインタープリター
                interpreter2.process_page(page)
                # １文字ずつのレイアウトデータを取得
                layout2 = device2.get_result()

                CharData = []
                for lt in layout2:
                    if isinstance(lt, LTChar):  # レイアウトデータうち、LTCharのみを取得
                        char1 = lt.get_text()   # レイアウトデータに含まれる全文字を取得
                        # cfalg = False

                        # 全文字データから０から９までの文字とピリオド、空白文字、カッコ文字のみを抽出
                        if isint(char1) or char1 == "." or char1 == " "  or char1 == "(" or char1 == ")":
                            CharData.append([char1, lt.x0, lt.x1, lt.y0, lt.y1])
                        
                # 数値の間出結果（ResultData）を一つずつ座標検査を行う。
                for R1 in ResultData:
                    val = R1[0]     # 検出数値
                    xx0 = R1[1][0]
                    yy0 = R1[1][1]
                    ww1 = R1[1][2]
                    xx1 = xx0 + ww1
                    hh1 = R1[1][3]
                    yy1 = yy0 + hh1
                    flag = R1[2]
                    R2 = []

                    # 文字データのうち、上記の xx0,yy0,xx1,yy1 の座標内にある文字のみを抽出し、CharData2を作成
                    # その際、CharData2をY座標の高さ順に並び替えるためのリスト「CY」を作成
                    CharData2=[]
                    CY = []
                    for cdata in CharData:
                        char2 = cdata[0]
                        x0 = cdata[1]
                        x1 = cdata[2]
                        y0 = cdata[3]
                        y1 = cdata[4]
                        if x0 >= xx0-1.0 and x1 <= xx1+1.0 and y0 >= yy0-1.0 and y1 <= yy1+1.0:
                            CharData2.append(cdata)
                            CY.append(y0)
                    
                    # リスト「CY」から降順の並び替えインデックッスを取得
                    y=np.argsort(np.array(CY))[::-1]

                    if len(CharData2) > 0:  # リストが空でない場合に処理を行う
                        CharData3 = []
                        # インデックスを用いて並べ替えた「CharData3」を作成
                        for i in range(len(y)):
                            CharData3.append(CharData2[y[i]])

                        # 同じ高さのY座標毎にデータをまとめる２次元のリストを作成
                        CharData4 = []
                        i = 0
                        for f in CharData3:
                            if i==0 :   # 最初の文字のY座標を基準値に採用し、仮のリストを初期化
                                Fline = []
                                Fline.append(f)
                                gy = f[3]
                            else:
                                if f[3]== gy:   # 同じY座標の場合は、リストに文字を追加
                                    Fline.append(f)
                                else:           # Y座標が異なる場合は、リストを「CharData4」を保存し、仮のリストを初期化
                                    if len(Fline) >= 4:
                                        CharData4.append(Fline)
                                    gy = f[3]
                                    Fline = []
                                    Fline.append(f)
                            i += 1
                        # 仮のリストが残っている場合は、リストを「CharData4」を保存
                        if len(Fline) >= 4:
                            CharData4.append(Fline)

                        xd = 3      #  X座標の左右に加える余白のサイズ（ポイント）を設定
                            
                        # 次にX座標の順番にデータを並び替える（昇順）
                        t1 = []
                        for F1 in CharData4:    # Y座標が同じデータを抜き出す。                        
                            CX = []         # 各データのX座標のデータリストを作成
                            for F2 in F1:
                                CX.append(F2[1])
                            
                            # リスト「CX」から降順の並び替えインデックッスを取得
                            x=np.argsort(np.array(CX))
                            
                            # インデックスを用いて並べ替えた「F3」を作成
                            F3 = []
                            for i in range(len(x)):
                                F3.append(F1[x[i]])
                            
                            # データリストのスペースの位置を抽出
                            sp = []
                            n1 = 0
                            for ff in F3:
                                if ff[0] == " ":
                                    sp.append(n1)
                                n1 += 1
                            
                            # 同じ行にスペースを挟んで複数の数値がある場合にそれらを分けてリストF5を作成
                            F5 = []
                            if len(sp) > 0 :
                                F4 = []
                                n1 = 0
                                for i in range(len(F3)):
                                    if i < sp[n1] or i == len(F3)-1:
                                        if F3[i][0] != " ":
                                            F4.append(F3[i])
                                    else:
                                        if len(F4)>0:
                                            F5.append(F4)
                                        F4 = []
                                        n1 += 1
                                if len(F4)>0 :
                                    F5.append(F4)
                            else:
                                F5.append(F3)
                            
                            # リストF5から該当する検出数値「val」があるかどうかを
                            for FF in F5:
                                if len(FF) > 0:
                                    t2 = ""
                                    xxx0 = 100000.0
                                    yyy0 = 100000.0
                                    xxx1 = -100000.0
                                    yyy1 = -100000.0
                                    for f4 in FF:
                                        t2 += f4[0]
                                        if f4[1] < xxx0: xxx0 = f4[1]
                                        if f4[2] > xxx1: xxx1 = f4[2]
                                        if f4[3] < yyy0: yyy0 = f4[3]
                                        if f4[4] > yyy1: yyy1 = f4[4]

                                    #  X座標の左右に加える余白を追加
                                    xxx0 -= xd
                                    xxx1 += xd

                                    ww1 = xxx1-xxx0
                                    hh1 = yyy1-yyy0
                                    t1.append(t2)
                                    # print(t2)

                                    if isfloat(t2):     # t2が数値の場合のみを処理
                                        if val == float(t2.replace("(","").replace(")","").replace(" ","")):
                                            #  検出数値「val」と一致する場合にデータを追加
                                            ResultData2.append([val ,[xxx0,yyy0,ww1,hh1],flag])
                                            break   #数値が見つかったのでループを抜け出す

                # 数値検出結果をページ毎のデータに追加
                pageResultData.append(ResultData2)

            else:
            #
            #   mode == "壁の検定表" 
            #
                # "壁の検定表"の場合はそのまま数値検出結果をページ毎のデータに追加
                pageResultData.append(ResultData)

# 使用したデバイスをクローズ
device.close()
device2.close()

#============================================================================================
#
#   数値検出結果を用いて各ページに四角形を描画する
#

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

    if pageN == 1:  # 表紙に「"検定比（0.##以上）の検索結果」の文字を印字
        cc.setFillColor("red")
        font_name = "ipaexg"
        cc.setFont(font_name, 20)
        cc.drawString(20 * mm,  pageSizeY - 40 * mm, "検定比（{}以上）の検索結果".format(limit1))

    else:   # ２ページ目以降は以下の処理
        pn = len(ResultData)

        # ページの左肩に検出個数を印字
        cc.setFillColor("red")
        font_name = "ipaexg"
        cc.setFont(font_name, 12)
        t2 = "検索個数 = {}".format(pn)
        cc.drawString(20 * mm,  pageSizeY - 15 * mm, t2)

        # 該当する座標に四角形を描画
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

            if flag:    # "壁の検定表"の場合は、四角形の右肩に数値を印字
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