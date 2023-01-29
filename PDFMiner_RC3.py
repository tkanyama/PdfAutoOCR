
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
import os
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

def MakeChar(page, interpreter, device):

    interpreter.process_page(page)
    # １文字ずつのレイアウトデータを取得
    layout = device.get_result()

    CharData = []
    for lt in layout:
        if isinstance(lt, LTChar):  # レイアウトデータうち、LTCharのみを取得
            char1 = lt.get_text()   # レイアウトデータに含まれる全文字を取得
            # if lt.x0 >= page_xmax/2.0:  # ページの右半分の文字だけを取得
            CharData.append([char1, lt.x0, lt.x1, lt.y0, lt.y1])

    # その際、CharData2をY座標の高さ順に並び替えるためのリスト「CY」を作成
    CharData2=[]
    CY = []
    for cdata in CharData:
        char2 = cdata[0]
        x0 = cdata[1]
        x1 = cdata[2]
        y0 = cdata[3]
        y1 = cdata[4]
        
        CharData2.append(cdata)
        CY.append(int(y0))
    
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
                gy = int(f[3])
            else:
                if int(f[3])== gy:   # 同じY座標の場合は、リストに文字を追加
                    Fline.append(f)
                else:           # Y座標が異なる場合は、リストを「CharData4」を保存し、仮のリストを初期化
                    if len(Fline) >= 4:
                        CharData4.append(Fline)
                    gy = int(f[3])
                    Fline = []
                    Fline.append(f)
            i += 1
        # 仮のリストが残っている場合は、リストを「CharData4」を保存
        if len(Fline) >= 4:
            CharData4.append(Fline)

        # 次にX座標の順番にデータを並び替える（昇順）
        t1 = []
        CharData5 = []
        for F1 in CharData4:    # Y座標が同じデータを抜き出す。                        
            CX = []         # 各データのX座標のデータリストを作成
            for F2 in F1:
                CX.append(F2[1])
            
            # リスト「CX」から降順の並び替えインデックッスを取得
            x=np.argsort(np.array(CX))
            
            # インデックスを用いて並べ替えた「F3」を作成
            F3 = []
            t2 = ""
            for i in range(len(x)):
                F3.append(F1[x[i]])
                t3 = F1[x[i]][0]
                t2 += t3
            # t1 += t2 + "\n"
            t1.append([t2])
            # print(t2,len(F3))
            CharData5.append(F3)
    
    return t1 , CharData5



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
# pdf_out_file = 'サンプル計算書(1)[検索結果].pdf'
# pdf_file = FileName
pdf_out_file = os.path.splitext(pdf_file)[0] + '[検出結果].pdf'

# PyPDF2のツールを使用してPDFのページ情報を読み取る。
with open(pdf_file, "rb") as input:
    reader = PR2(input)
    PageMax = len(reader.pages)     # PDFのページ数
    PaperSize = []
    for page in reader.pages:       # 各ページの用紙サイズの読取り
        p_size = page.mediabox
        page_xmin = float(page.mediabox.lower_left[0])
        page_ymin = float(page.mediabox.lower_left[1])
        page_xmax = float(page.mediabox.upper_right[0])
        page_ymax = float(page.mediabox.upper_right[1])
        PaperSize.append([page_xmax - page_xmin , page_ymax - page_ymin])

startpage = 150     # 検索を開始する最初のページ
# endpage = PageMax   # 検索を終了する最後のページ
endpage = 250

# PDFMinerのツールの準備
resourceManager = PDFResourceManager()
# PDFから単語を取得するためのデバイス
device = PDFPageAggregator(resourceManager, laparams=LAParams())
# PDFから１文字ずつを取得するためのデバイス
device2 = PDFPageAggregator(resourceManager)

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

            xd = 3      #  X座標の左右に加える余白のサイズ（ポイント）を設定

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

            
            if mode == "検定比図" :

                t1 , CharData5 = MakeChar(page, interpreter2,device2)

                if len(t1) > 0:
                    i = -1
                    for line in t1:
                        i += 1
                        t3 = line[0]
                        CharLine = CharData5[i] # １行文のデータを読み込む
                        
                        # if "検定比" in t3 : # 「検定比」が現れた場合の処理
                        # print(t3)
                        st = 0
                        t4 = t3.split()            # 文字列を空白で分割
                        if len(t4)>0:    # 文字列配列が１個以上ある場合に処理
                            for t5 in t4:
                                t6 = t5.replace("(","").replace(")","").replace(" ","")    # 「検定比」と数値が一緒の場合は除去
                                nn = t3.find(t6,st)   # 数値の文字位置を検索
                                ln = len(t6)

                                # カッコがある場合は左右１文字ずつ追加
                                if "(" in t5:
                                    xn = 1
                                else:
                                    xn = 0

                                if isfloat(t6):
                                    a = float(t6)
                                    if a>=limit1 and a<1.0:
                                        # 数値がlimit以上の場合はデータに登録
                                        xxx0 = CharLine[nn-xn][1]
                                        xxx1 = CharLine[nn+ln+xn][2]
                                        yyy0 = CharLine[nn][3]
                                        yyy1 = CharLine[nn][4]
                                        if ln <=4 :
                                            xxx0 -= xd
                                            xxx1 += xd
                                        width3 = xxx1 - xxx0
                                        height3 = yyy1 - yyy0
                                        ResultData.append([a,[xxx0, yyy0, width3, height3],False])
                                        flag = True
                                        pageFlag = True
                                        val = a
                                        print('val={:.2f}'.format(val))

                                # 数値を検索を開始するを文字数分移動
                                st = nn + ln + 1
                    
                            
            elif mode == "柱の検定表" : 

                t1 , CharData5 = MakeChar(page, interpreter2,device2)
                
                if len(t1) > 0:
                    # lines =t1.splitlines()
                    i = -1
                    kmode = False
                    for line in t1:
                        i += 1
                        t3 = line[0]
                        if kmode == False:                           
                            if "検定比" in t3 : # 奇数回目の「検定比」が現れたら「kmode」をTrue
                                kmode = True
                                # 「検定比」の下にある数値だけを検出するためのX座標を取得
                                n = t3.index("検定比")
                                c1 = CharData5[i][n]
                                zx0 = c1[1]
                                c2 = CharData5[i][n+2]
                                zx1 = c2[2]
                                # print(c1[0],c2[0], zx0, zx1)
                        else:
                            # kmode=Trueの場合の処理
                            
                            CharLine = CharData5[i] # １行文のデータを読み込む
                            t4 = ""
                            xxx0 = 100000.0
                            yyy0 = 100000.0
                            xxx1 = -100000.0
                            yyy1 = -100000.0
                            for char in CharLine:
                                # kmodeの時には「検定比」の下にある数値だけを検出する。
                                if char[1]>=zx0 and char[2]<=zx1:
                                    t4 += char[0]

                            if isfloat(t4): # 切り取った文字が数値の場合の処理
                                a = float(t4)
                                if a>=limit1 and a<1.0:
                                    # 数値がlimit以上の場合はデータに登録
                                    nn = t3.index(t4)   # 数値の文字位置を検索
                                    xxx0 = CharLine[nn][1]
                                    xxx1 = CharLine[nn+3][2]
                                    yyy0 = CharLine[nn][3]
                                    yyy1 = CharLine[nn][4]
                                    xxx0 -= xd
                                    xxx1 += xd
                                    width3 = xxx1 - xxx0
                                    height3 = yyy1 - yyy0
                                    ResultData.append([a,[xxx0, yyy0, width3, height3],False])
                                    flag = True
                                    pageFlag = True
                                    val = a
                                    print('val={:.2f}'.format(val))
                            
                            if "検定比" in t3 : # 偶数回目の「検定比」が現れたら「kmode」をFalseにする
                                kmode = False

                                # まず、同様に検定比」の下にある数値だけを検出する。
                                t4 = ""
                                xxx0 = 100000.0
                                yyy0 = 100000.0
                                xxx1 = -100000.0
                                yyy1 = -100000.0
                                for char in CharLine:
                                    if char[1]>=zx0 and char[2]<=zx1:
                                        t4 += char[0]

                                if isfloat(t4):
                                    a = float(t4)
                                    if a>=limit1 and a<1.0:
                                        nn = t3.index(t4)   # 数値の文字位置を検索
                                        xxx0 = CharLine[nn][1]
                                        xxx1 = CharLine[nn+3][2]
                                        yyy0 = CharLine[nn][3]
                                        yyy1 = CharLine[nn][4]
                                        ResultData.append([a,[xxx0, yyy0, width3, height3],False])
                                        flag = True
                                        pageFlag = True
                                        val = a
                                        print('val={:.2f}'.format(val))

                            #　続いて検定比」の右側にある数値を検出する。
                                n = t3.index("検定比")      # 偶数回目の「検定比」の文字位置を検索
                                t4 = t3[n+3:]              # 「検定比」の右側だけの文字列を取得
                                st = n + 3
                                t5 = t4.split()            # 文字列を空白で分割
                                if len(t5)>0:    # 文字列配列が１個以上ある場合に処理
                                    for t6 in t5:
                                        if isfloat(t6):
                                            a = float(t6)
                                            if a>=limit1 and a<1.0:
                                                # 数値がlimit以上の場合はデータに登録
                                                nn = t3.find(t6,st)   # 数値の文字位置を検索
                                                xxx0 = CharLine[nn][1]
                                                xxx1 = CharLine[nn+3][2]
                                                yyy0 = CharLine[nn][3]
                                                yyy1 = CharLine[nn][4]
                                                xxx0 -= xd
                                                xxx1 += xd
                                                width3 = xxx1 - xxx0
                                                height3 = yyy1 - yyy0
                                                ResultData.append([a,[xxx0, yyy0, width3, height3],False])
                                                flag = True
                                                pageFlag = True
                                                val = a
                                                print('val={:.2f}'.format(val))
                                        st += len(t6)
                                    
                                
            elif mode == "梁の検定表" : 

                t1 , CharData5 = MakeChar(page, interpreter2,device2)
                
                if len(t1) > 0:

                    # lines =t1.splitlines()
                    i = -1
                    for line in t1:
                        i += 1
                        t3 = line[0]
                        CharLine = CharData5[i] # １行文のデータを読み込む
                        
                        if "検定比" in t3 : # 「検定比」が現れた場合の処理
                            # print(t3)
                            st = 0
                            t4 = t3.split()            # 文字列を空白で分割
                            if len(t4)>0:    # 文字列配列が１個以上ある場合に処理
                                for t5 in t4:
                                    t6 = t5.replace("検定比","")    # 「検定比」と数値が一緒の場合は除去
                                    nn = t3.find(t6,st)   # 数値の文字位置を検索
                                    ln = len(t5)
                                    if isfloat(t6):
                                        a = float(t6)
                                        if a>=limit1 and a<1.0:
                                            # 数値がlimit以上の場合はデータに登録
                                            xxx0 = CharLine[nn][1]
                                            xxx1 = CharLine[nn+3][2]
                                            yyy0 = CharLine[nn][3]
                                            yyy1 = CharLine[nn][4]
                                            xxx0 -= xd
                                            xxx1 += xd
                                            width3 = xxx1 - xxx0
                                            height3 = yyy1 - yyy0
                                            ResultData.append([a,[xxx0, yyy0, width3, height3],False])
                                            flag = True
                                            pageFlag = True
                                            val = a
                                            print('val={:.2f}'.format(val))

                                    # 数値を検索を開始するを文字数分移動
                                    st += ln
                                    

            elif mode == "壁の検定表":
                t1 , CharData5 = MakeChar(page, interpreter2,device2)
                
                if len(t1) > 0:
                    i = -1
                    tn = len(t1)

                    while True:
                        i += 1
                        if i > tn-1 : break

                        t3 = t1[i][0]
                        # print(t3)
                        CharLine = CharData5[i]
                        if "QDL" in t3:
                            nn = t3.find("QDL",0)   # 数値の文字位置を検索
                            xxx0 = CharLine[nn][1]
                            yyy1 = CharLine[nn][4]
                            t4 = t3[nn+3:].replace(" ","")
                            if isfloat(t4):
                                A1 = float(t4)
                            else:
                                A1 = 0.0
                            
                            i += 1
                            t3 = t1[i][0]
                            CharLine = CharData5[i]
                            
                            nn  = t3.find("QAL",0) 
                            yyy0 = CharLine[nn][3]

                            t4 = t3[nn+3:].replace(" ","")
                            nn2 = len(t3[nn:])
                            
                            xxx1 = CharLine[nn+nn2-1][2]
                            yyy0 = CharLine[nn+nn2-1][3]
                            
                            if isfloat(t4):
                                A2 = float(t4)
                            else:
                                A2 = 10000.0
                            QDL_mode = False
                            
                            if A2 != 0.0:
                                a = abs(A1/A2)
                                if a>=limit2 and a<1.0:
                                    
                                    xxx0 -= xd
                                    xxx1 += xd
                                    width3 = xxx1 - xxx0
                                    height3 = yyy1 - yyy0
                                    ResultData.append([a,[xxx0, yyy0, width3, height3],True])
                                    flag = True
                                    pageFlag = True
                                    val = a
                                    print('val={:.2f}'.format(val))

                            i += 1
                            t3 = t1[i][0]
                            # print(t3)
                            CharLine = CharData5[i]

                            nn = t3.find("QDS",0)   # 数値の文字位置を検索
                            xxx0 = CharLine[nn][1]
                            yyy1 = CharLine[nn][4]
                            t4 = t3[nn+3:].replace(" ","")
                            if isfloat(t4):
                                A1 = float(t4)
                            else:
                                A1 = 0.0
                            QDL_mode = True
                                
                        
                            i += 1
                            t3 = t1[i][0]
                            CharLine = CharData5[i]
                            
                            nn = t3.find("QAS",0)
                            yyy0 = CharLine[nn][3]

                            t4 = t3[nn+3:].split()[0]
                            nn2 = len(t3[nn:])
                            
                            xxx1 = CharLine[nn+nn2-1][2]
                            yyy0 = CharLine[nn+nn2-1][3]
                            
                            if isfloat(t4):
                                A2 = float(t4)
                            else:
                                A2 = 10000.0
                            QDL_mode = False
                            
                            if A2 != 0.0:
                                a = abs(A1/A2)
                                if a>=limit2 and a<1.0:
                                    
                                    xxx0 -= xd
                                    xxx1 += xd
                                    width3 = xxx1 - xxx0
                                    height3 = yyy1 - yyy0
                                    ResultData.append([a,[xxx0, yyy0, width3, height3],True])
                                    flag = True
                                    pageFlag = True
                                    val = a
                                    print('val={:.2f}'.format(val))


            if mode == "杭の検定表":
                pageFlaf = False


        if pageFlag : 
            pageNo.append(pageI)
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