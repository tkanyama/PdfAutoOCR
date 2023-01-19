import os
import sys
import cv2
from PyPDF2 import PdfReader ,PdfMerger
from pdf2image import convert_from_path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pyocr
import re
import json

class PdfOCR():
    def __init__(self, FileName):
        if not os.path.isfile(FileName):
            print('ファイルがありません！！')      
            sys.exit()

        self.pdfFileName = FileName

        #OCRエンジンを取得する
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("OCRエンジンが指定されていません")
            sys.exit(1)
        else:
            self.tool = tools[0]

        self.jsonFileName = os.path.splitext(self.pdfFileName)[0] + '.json'
        print(self.jsonFileName)

        self.dpi0 = 600      # 数値を読み取る場合のDPI
        self.dpi1 = 200      # 結果出力時に使用するDPI
        self.dpi2 = 600      # ページのタイトル（日本語）を読み取る場合のDPI
        self.Cdpi = self.dpi0 / self.dpi1      # 結果出力時に使用するDPIの比率


    def pageRead(self):
        if os.path.isfile(self.jsonFileName):
            json_open = open(self.jsonFileName, 'r')
            json_load = json.load(json_open)
            self.titles = json_load['item']
            self.pageNumber = json_load['page']
        else:
            self.titles = [["断面検定比図","短期荷重時"],["柱の断面検定表"],["梁の断面検定表"],["壁の断面検定表"]]
            with open(self.pdfFileName, "rb") as input:
                reader = PdfReader(input)
                self.PageMax = len(reader.pages)

            self.PageMax = 300
            # pdfの総ページ数は？
            # print("サンプル計算書(1).pdf has %d pages.\n" % PageMax)
            self.pageNumber = []
            for i in range(len(self.titles)):
                self.pageNumber.append([])

            for i in range(self.PageMax):
                if i > 10:
                    images = convert_from_path(self.pdfFileName,dpi=self.dpi2,first_page=i+1,last_page=i+1)
                    image = images[0]
                    img = np.array(image)
                    h , w = img.shape[:2]
                    split_pic=img[int(h*0.05):int(h*0.125),int(w*0.66):int(w*0.92),:]
                    # plt.imshow(cv2.cvtColor(split_pic, cv2.COLOR_BGR2RGB))
                    # plt.show()
                    image2 = Image.fromarray(split_pic)

                    # box_builder = pyocr.builders.TextBuilder(tesseract_layout=6)
                    box_builder = pyocr.builders.TextBuilder()
                    text = self.tool.image_to_string(image2,lang="jpn",builder=box_builder)
                    text = text.replace(" ","").replace("　","").replace("\t","").replace("\n","").replace("染","梁")
                    print(text)
                    print(i+1)
                    j = 0
                    for title in self.titles:
                        b = title[0] in text
                        if len(title)>1 :
                            for k in range(len(title)-1):
                                b = b and title[k+1] in text
                        if b:
                            self.pageNumber[j].append(i+1)
                        j += 1

            pageData = {"item":self.titles,"page":self.pageNumber}
            # data_json = json.dumps(pageData, indent=4, ensure_ascii=False)
            with open(self.jsonFileName, 'w') as fp:
                json.dump(pageData, fp, indent=4, ensure_ascii=False)



