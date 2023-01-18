import os
import sys
import cv2
from PyPDF2 import PdfReader ,PdfMerger
from pdf2image import convert_from_path, convert_from_bytes
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pyocr
import re

def isfloat(s):  # 浮動小数点数値を表しているかどうかを判定
    try:
        float(s)  # 文字列を実際にfloat関数で変換してみる
    except ValueError:
        return False
    else:
        return True



#OCRエンジンを取得する
tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("OCRエンジンが指定されていません")
    sys.exit(1)
else:
    tool = tools[0]
# print(text)
pdfFileName = "サンプル計算書(1).pdf"
dpi0 = 600
dpi1 = 150
Cdpi = dpi0 / dpi1
start_page = 185
end_page = 188
LineW = 1

with open(pdfFileName, "rb") as input:
    reader = PdfReader(input)
    # pdfの総ページ数は？
    print("サンプル計算書(1).pdf has %d pages.\n" % len(reader.pages))
    # 指定のページのデータを読み込む
    images = convert_from_path(pdfFileName,dpi=dpi0,first_page=start_page,last_page=end_page)
    Out_image2 = convert_from_path(pdfFileName,dpi=dpi1,first_page=start_page,last_page=end_page)
    # img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # retval, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    pdf_file_merger = PdfMerger()

    no =  0
    Total_Contents = []
    Total_Positions = []
    Total_PointN = []

    for image in images:
        no += 1
        print("page {0}".format(no))
        print()
        img = np.array(image)
        img2 = img
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.show()

        # モノクロ・グレースケール画像へ変換（2値化前の画像処理）
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2値化（Binarization）：白（1）黒（0）のシンプルな2値画像に変換
        retval, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # plt.imshow(img_binary)
        print('【直線を検出中・・・】2値化処理画像 - Binarization')
        # plt.imshow(cv2.cvtColor(img_binary, cv2.COLOR_BGR2RGB))
        # plt.show()

        lines = cv2.HoughLinesP(img_binary, rho=1, theta=np.pi/360, threshold=15, minLineLength=60, maxLineGap=5.4)

        if lines is None:  # 直線が検出されない場合
            print('\n【直線の検出結果】')
            print('　直線は検出されませんでした。')
            
        else:  # 直線が検出された場合
            print('\n【直線の検出結果】')
            print('　直線が検出されました。検出した直線を削除します。')
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 検出した直線に赤線を引く
                red_lines_img = cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 1)
            print('\n【直線検出部位の視覚化】')
            print('　赤色部分が検出できた直線。')
            # plt.imshow(cv2.cvtColor(red_lines_img, cv2.COLOR_BGR2RGB))
            # plt.show()

            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 検出した直線を消す（白で線を引く）：2値化した際に黒で表示される
                no_lines_img = cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
                
            print('\n【直線検出部位の削除結果：元の画像から削除】')
            print('　白色部分が検出した直線を消した場所（背景が白の場合は区別できません）。')
            # plt.imshow(cv2.cvtColor(no_lines_img, cv2.COLOR_BGR2RGB))
            # plt.show()

        image2 = Image.fromarray(no_lines_img)

        img = np.array(image2)
        # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # plt.show()

        # モノクロ・グレースケール画像へ変換（2値化前の画像処理）
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2値化（Binarization）：白（1）黒（0）のシンプルな2値画像に変換
        retval, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # plt.imshow(img_binary)
        print('【直線を検出中・・・】2値化処理画像 - Binarization')
        # plt.imshow(cv2.cvtColor(img_binary, cv2.COLOR_BGR2RGB))
        # plt.show()

        lines = cv2.HoughLinesP(img_binary, rho=1, theta=np.pi/360, threshold=15, minLineLength=60, maxLineGap=5.4)

        if lines is None:  # 直線が検出されない場合
            print('\n【直線の検出結果】')
            print('　直線は検出されませんでした。')
            
        else:  # 直線が検出された場合
            print('\n【直線の検出結果】')
            print('　直線が検出されました。検出した直線を削除します。')
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 検出した直線に赤線を引く
                red_lines_img = cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 1)
            print('\n【直線検出部位の視覚化】')
            print('　赤色部分が検出できた直線。')
            # plt.imshow(cv2.cvtColor(red_lines_img, cv2.COLOR_BGR2RGB))
            # plt.show()

            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 検出した直線を消す（白で線を引く）：2値化した際に黒で表示される
                no_lines_img = cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 1)

            print('\n【直線検出部位の削除結果：元の画像から削除】')
            print('　白色部分が検出した直線を消した場所（背景が白の場合は区別できません）。')
            # plt.imshow(cv2.cvtColor(no_lines_img, cv2.COLOR_BGR2RGB))
            # plt.show()


        image2 = Image.fromarray(no_lines_img)


        # 読み込んだページのテキストを抽出
        # print(extract_text(page))
        #文字と座標を読み取る

        # tesseract_layout=No
        # No の意味
        # 0 オリエンテーションとスクリプト検出（OSD）のみ。
        # 1 自動ページ分割とOSD。
        # 2 自動ページ分割、ただしOSD、またはOCRはなし。(未実装)
        # 3 完全自動ページ分割、ただしOSDなし。(初期設定)
        # 4 サイズの異なるテキストが1列に並んでいると仮定します。
        # 5 縦書きの一様なテキストブロックを想定しています。
        # 6 一様なテキストブロックを想定しています。
        # 7 画像を1つのテキスト行として扱う。
        # 8 画像を1つの単語として扱う。
        # 9 画像を円内の単一単語として扱う。
        # 10 画像を1つの文字として扱う。
        # 11 疎なテキスト。できるだけ多くのテキストを順不同に探します。
        # 12 OSDでテキストを疎にする。
        # 13 生の行。画像を1つのテキスト行として扱います。

        # box_builder = pyocr.builders.WordBoxBuilder(tesseract_layout=11)
        box_builder = pyocr.builders.WordBoxBuilder()
        text_position = tool.image_to_string(image2,lang="eng",builder=box_builder)

        #取得した座標と文字を出力するし、画像に枠を書き込む/\©
        img2 = np.array(image)
        t0 = ""
        p0 = [0,0]
        p1 = [0,0]
        flag = False
        limit = 0.95
        box_builder2 = pyocr.builders.WordBoxBuilder(tesseract_layout=7)
        
        Contents = []
        Positions = []
        PointN = 0
        for res in text_position:
            m = res.content
            x = res.position
            print(m)

            m = m.replace(",",".").replace("@","0.").replace("/","").replace("\\","").replace("©","0.").replace("Q","0")
            m = m.replace("Q","0").replace("U","0").replace("P","0").replace(' ', '').replace('ha', '42').replace('eo', '70').replace('oe', '0.')
            m = m.replace("o","").replace("-","").replace("«","")
            if m == "(0" or m == "0":
                m = m + "."
            if m == "(0." or m == "0.":
                t0 = m
                p0 = res.position[0]
                flag = True
            else:
                t = t0 + m
                t0 = ""

                if flag == False:
                    p0 = res.position[0]
                p1 = res.position[1]
                flag = False

                if re.search(r'\d', t):
                    # print(m)
                    # print(res.position)
                    if isfloat(t.replace("(","").replace(")","")):
                        a = float(t.replace("(","").replace(")",""))
                        print(a)
                        if a >= limit and a < 1.0 :
                            PointN += 1
                            Contents.append(a)
                            Positions.append([list(p0),list(p1)])
                
                        elif a >= 1 and a <= 99:
                            b = a / 100.0
                            if b >= limit and b < 1.0 :
                                p02 = list(p0)
                                p12 = list(p1)
                                p02[0] = p02[0]- int((p12[0]-p02[0])*1.4)
                                p0 = tuple(p02)
                                PointN += 1
                                Contents.append(a)
                                Positions.append([list(p0),list(p1)])
        
        # plt.imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
        # plt.show()

        box_builder2 = pyocr.builders.TextBuilder(tesseract_layout=7)
        Positions2 = []
        PointN2 = 0
        Contents2 = []
        for P in Positions:

            img3 = img2[P[0][1]-5:P[1][1]+5,P[0][0]-5:P[1][0]+5]
            
            # plt.imshow(cv2.cvtColor(img3, cv2.COLOR_BGR2RGB))
            # plt.show()
            image3 = Image.fromarray(img3)
            
            t = tool.image_to_string(image3,lang="eng",builder=box_builder2)
            print("?:" + t)
            t = t.replace(",",".").replace("@","0.").replace("/","").replace("\\","").replace("©","0.").replace("Q","0")
            t = t.replace("Q","0").replace("U","0").replace("P","0").replace(' ', '').replace('ha', '42').replace('eo', '70').replace('oe', '0.')
            t = t.replace("o","").replace("-","").replace("«","")
            
            if re.search(r'\d', t):
                # print(m)
                # print(res.position)
                if isfloat(t.replace("(","").replace(")","")):
                    a = float(t.replace("(","").replace(")",""))
                    print(a)
                    if a >= limit and a < 1.0 :
                        PointN2 += 1
                        Contents2.append(a)
                        Positions2.append(P)
            
                    elif a >= 1 and a <= 99:
                        b = a / 100.0
                        if b >= limit and b < 1.0 :
                            PointN2 += 1
                            Contents2.append(a)
                            Positions2.append(P)
        
        print(Contents2)
        Total_Contents.append(Contents2)
        Total_Positions.append(Positions2)
        Total_PointN.append(PointN2)

    i = 0
    for image in Out_image2:
        if Total_PointN[i] > 0:
            img2 = np.array(image)
            Position = Total_Positions[i]
            for P in Position:
                P0 = [int(P[0][0]/Cdpi) - LineW*2,int(P[0][1]/Cdpi) - LineW*2]
                P1 = [int(P[1][0]/Cdpi) + LineW,int(P[1][1]/Cdpi) + LineW]
                cv2.rectangle(img2,tuple(P0),tuple(P1),(255,0,0),LineW)

            pil_image = Image.fromarray(img2)
            im_pdf = pil_image.convert("RGB")
            fname = "P"+str(no)+ ".pdf"
            # im_pdf.save(r"test.pdf")
            im_pdf.save(fname)
            pdf_file_merger.append(fname)
            os.remove(fname)

        i += 1



    pdf_file_merger.write('test2.pdf')
    pdf_file_merger.close()

