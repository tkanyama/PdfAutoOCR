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
from PdfOCR import PdfOCR

def isfloat(s):  # 浮動小数点数値を表しているかどうかを判定
    try:
        float(s)  # 文字列を実際にfloat関数で変換してみる
    except ValueError:
        return False
    else:
        return True




if __name__ == '__main__':

    pdfFileName = "/Users/kanyama/VS Code/PdfAutoOCR/サンプル計算書(1).pdf"
    OcrTool = PdfOCR(pdfFileName)
    OcrTool.pageRead()


