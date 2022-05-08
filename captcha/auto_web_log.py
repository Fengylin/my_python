#-*- coding:utf-8 -*-
import pyautogui
from selenium import webdriver
import time
import xlrd
import pyperclip
import webbrowser
import os
import Colour_to_WB as CtoWB
import math
from PIL import Image,ImageDraw,ImageFont,ImageFont


class VectorCompare:
    def magnitude(self,concordance):                # 计算向量大小
        total = 0
        for word,count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    def relation(self,concordance1, concordance2):  # 相似度（余弦值）
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))

    def vb(self,im):                                # 建立图片向量
        d1 = {}
        count = 0
        for i in im.getdata():                      # 图像点的（R，G，B）
            if i > 1: i=1                           # 二值
            d1[count] = i
            count += 1
        return d1




#形成单字符图像分割线
def find_letters(im2):
    inletter = False
    foundletter=False
    start = 0
    end = 0
    letters = []                                            # 待识别的字符
    for y in range(im2.size[0]): # slice across，
        for x in range(im2.size[1]): # slice down
            pix = im2.getpixel((y,x))
            if pix != 0:
                inletter = True                

        if foundletter == False and inletter == True:
            foundletter = True
            start = y

        if foundletter == True and inletter == False:
            foundletter = False
            end = y-1
            letters.append((start,end))

        inletter=False
    if start > end :
        letters.append ((start,y))
    return letters

def letterIconset():
    iconset = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','M','N','P','R'] #可识别字符集
    imageset = []                                                   # 训练集
    v = VectorCompare()
    for letter in iconset:
        for im in os.listdir('./train_imgs/%s/'%(letter)):
            temp = []
            im2 =Image.open("./train_imgs/%s/%s"%(letter,im))
            if im != "Thumbs.db" and img != ".DS_Store":            # windows check...
                temp.append(v.vb(im2))
            imageset.append({letter:temp})
    return imageset

#识别验证码
def Verify_Code(img):
    im = CtoWB.noise_clean(img,2,12,12)                             # 图片去噪
    im = CtoWB.denoise(im)                                          # 遍历去噪
    v = VectorCompare()
    letters = find_letters(im)
    im2 = im.crop ((letters[0][0],12,letters[5][1]+1,24))           # 待识别图像
    letters = find_letters(im2)
    count = 0
    Text = ''
    imageset = letterIconset()
    for letter in letters:  #识别字符
        im3 = im2.crop(( letter[0] , 0, letter[1]+1,im2.size[1] ))  # 单字符图像
        guess = []
        for image in imageset:
            for x,y in image.items():
                if len(y) != 0:
                    guess.append( ( v.relation(y[0],v.vb(im3)),x) )
        guess.sort(reverse=True)
        print (guess[0])
        Text += guess[0][1]
        count += 1
    return  Text


#打开网站并返回到正常状态
def openweb(url):
    print('打开网站',url)
    pyautogui.hotkey('win', 'd')
    webbrowser.open_new(url)
    time.sleep(5)
    pyautogui.hotkey('ctrl', '0')
    img =Image.open( r"C:\Users\何博\Documents\important\websize.png")    
    location=pyautogui.locateCenterOnScreen(img,confidence=0.8)
    if location == None:
        time.sleep(10)
        return
    pyautogui.click(location.x,location.y,1,interval=0.2,duration=2,) # 网页窗口最大化
    time.sleep(10)

def loginweb(img1,img2,usrId,Paswd):    
    print("登录网站")
    inputbox(img1,usrId)                                    # 输入用户名
    inputbox(img2,Paswd)                                    # 输入密码
    pyautogui.press('Enter')
    time.sleep(5)
    
#填写文本框
def inputbox(img,Text):
    location=pyautogui.locateOnScreen(img,confidence=0.8)
    #print (location,Text)
    if location is not None:
        x=location.left+location.width*1.5
        y=location.top+location.height/2
        pyautogui.click(x,y,1,interval=0.2,duration=2,)
        pyautogui.press('esc')
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('del')
        pyperclip.copy(Text)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('esc')

#网页相关数据检查
def dataCheck(sheet1):
    print('数据检查')
    checkCmd = True
    end=['01.png','02.png','03.png','04.png','05.png']
    #行数检查
    if sheet1.nrows<2:
        print("没数据啊哥")
        checkCmd = False
    #每行数据检查
    i = 0
    while i < sheet1.nrows-1:
        # 第3列 操作类型检查
        i += 1                                      # 第0行为表头。有效行从1开始
        print ('第 ',i,'行,共有',sheet1.nrows,' 行')
        name = sheet1.row(i)[0].value               # 第一列为网页名。
        if name == 0:                               # 为了调试，停止后面的网页。下一行第一列为0
            break
        cmdType = sheet1.row(i)[2]                  # 第三列必须为0或1，表示是否要验证
        if (cmdType.value != 1.0 and cmdType.value != 0.0):
            print('第',i+1,"行,第3列数据有毛病")
            checkCmd = False
        # 检查是否存在图标文件
        j=0
        while j <= 4:
            img=path = "C:\\Users\\何博\\Documents\\important\\"+sheet1.row(i)[0].value+end[j]            
            if not os.path.exists(img):
                print("文件",img,"不存在")
                checkCmd = False
            j += 1
        
    return checkCmd

if __name__ == '__main__':
    path = r"C:\Users\Public\Documents\important\\"
    file= path + "AutoWebLog.xls"                                   # 这是关于需要登录网站的数据文件
    wb = xlrd.open_workbook(filename=file)
    sheet1 = wb.sheet_by_index(0)                                   # 通过索引获取表格sheet页
    print('欢迎使用风飘飘自动登录~')
    checkCmd = dataCheck(sheet1)                                    # 数据检查
    ft = ImageFont.truetype(r'C:\Windows\Fonts\Tahoma.ttf',18)
    if checkCmd:
        i=1
        while i < sheet1.nrows:
            if sheet1.row(i)[0].value == 0:
                print("工作结束,不再继续")
                break
            name_web = path + sheet1.row(i)[0].value
            url= sheet1.row(i)[1].value
            openweb(url)                                            # 打开网页
            img=name_web +"03.png"                                  # 登录验证，图片为已经登录的标识截图
            location=pyautogui.locateOnScreen(img,confidence=0.8)
            if location is None:                                    # 登录网站
                if sheet1.row(i)[2].value !=0:
                    img= name_web+"06.png"                          # 验证码图片标识截图
                    location=pyautogui.locateOnScreen(img)
                    x=location.left+location.width*1.2
                    w=location.width*1.25
                    h=location.height*.6

                    y=location.top+w*0.1
                    s = len(os.listdir('./png/'))
                    im = pyautogui.screenshot(region=(x,y,151,37))  # 截取验证码图片
                    im.save ('./png/{:0>3d}'.format(s)+'.png',dpi=(300.0,300.0))  # 存储验证码图片
                    text = Verify_Code(im)                          # 验证码图片识别
                    img= name_web+"05.png"                          # 验证码输入框标识截图
                    print("输入验证码",text)
                    inputbox(img, text)                             # 输入验证码
                    ig = Image.new ('RGB',(151,75),(255, 255, 255))
                    ig.paste(im,(0,0))
                    im = ImageDraw.Draw(ig)
                    l= list(text)
                    text= ''
                    for t in l:
                        text += t+'  '                        
                    im.text ((10,40),text,font = ft,fill = (0,0,0))
                    ig.save ('./comp/{:0>3d}'.format(s)+'.tif',dpi=(300.0,300.0)) # 比较图片
                    
                img1= name_web + "01.png"                           # 用户名框标识截图
                img2= name_web + "02.png"                           # 密码框标识图片
                usrId= sheet1.row(i)[3].value                       # 用户名
                Paswd= sheet1.row(i)[4].value                       # 密码
                loginweb(img1,img2,usrId,Paswd)                     # 登录
            else:
                print("已经登录")
            img= name_web + "04.png"                                # 打卡标识截图
            location=pyautogui.locateCenterOnScreen(img,confidence=0.8)
            if location is not None:                                # 打卡
                print("打卡")
                pyautogui.click(location.x,location.y,2,interval=0.2,duration=0.2,)
                pyautogui.hotkey('ctrl', 'r')
                time.sleep(3)
            else:
                print("已经打卡")
            i += 1
        checkCmd=False
    else:
        print ("OVER!")

            
