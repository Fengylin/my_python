# 这个程序用于分捡训练集中的图片。验证码图片经处理后，形成单字符图片，
# 集中放在一起，需要按照每个字符进行归类分捡。分捡过程中，将图片放大
# 并显示于屏幕上，输入其相应的字母或数字，程序会自动将其图片文件放入
# 相应的文件夹中

import os,time,msvcrt
import shutil,pyautogui,sys
from PIL import Image

def tif_move(img,pi,po):
    iconset = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','M','N','P','R'] #可识别字符集
    im =Image.open(pi+img)
    src = pi + img
    x,y = im.size
    im = im.resize ((x*10,y*10),Image.ANTIALIAS)
    im.save ('tmp.tif')
    os.startfile('tmp.tif')
    time.sleep(0.5)
    pyautogui.hotkey('alt','tab')
    F = True
    while F:
        print ("请输入相应的字符》》：",end = '')
        c = msvcrt.getche()
        letter = c.decode('utf-8')
        print (letter)
        if letter in iconset:
            dst = po + letter + '/' + img
            shutil.move (src,dst)
            F = False            
        else :
            if letter == str(0):
                print('退出')
                time.sleep(1)
                sys.exit()
            else:
                print("输入有误，请重新输入!!!")
            



if __name__ == "__main__":
    pin = r'./letters_imgs/'                    # 单字符图片集
    pout= r'./train_imgs/'                      # 分类训练字符集
    tif_src = os.listdir (pin)
    total = len (tif_src)
    if total == 0:
        print ("已经没有文件需要处理了")
    try:
        for idx,x in enumerate(tif_src, start=1):
            print("[{}/{}] 处理{}...".format(idx, total, x))
            tif_move(x, pin,pout)
    except Exception as e:
        print("错误:{}".format(e))
