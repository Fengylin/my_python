import pyautogui
import time
import xlrd
import pyperclip
import webbrowser
import os



#打开网站并返回到正常状态
def openweb(url):
    webbrowser.open(url, new=0, autoraise=True)
    time.sleep(10)
    pyautogui.hotkey('ctrl', '0')

    

def dataCheck(sheet1):
    checkCmd = True
    end=['01.png','02.png','03.png','04.png','05.png']
    #行数检查
    if sheet1.nrows<2:
        print("没数据啊哥")
        checkCmd = False
    #每行数据检查
    i = 1
    while i < sheet1.nrows:
        # 第3列 操作类型检查
        cmdType = sheet1.row(i)[2] #第三列必须为0或1
        if (cmdType.value != 1.0 and cmdType.value != 0.0):
            print('第',i+1,"行,第3列数据有毛病")
            checkCmd = False
        # 检查是否存在图标文件
        j=0
        while j <= 4:
            img=sheet1.row(i)[0].value+end[j]            
            if not os.path.exists(img):
                print("文件",img,"不存在")
                checkCmd = False
            j += 1
        i += 1
    return checkCmd

def loginweb(img1,img2,usrId,Paswd):
    print(img,usrId,Paswd,F)
    inpubox(img1,usrId)#输入用户名
    inpubox(img2,Padwd)#输入密码
    pyautogui.press('Enter')
    time.sleep(5)
    
#填写文本框
def inputbox(img,Text):
    location=pyautogui.locateOnScreen(img)
    print (location)
    if location is not None:
        x=location.left+location.width*1.5
        y=location.top+location.height/2
        pyautogui.click(x,y,1,interval=0.2,duration=0.2,)
        pyautogui.press('esc')
        pyautogui.hotkey('ctrl', 'a')
        pyperclip.copy(Text)
        pyperclip.paste()
        pyautogui.press('esc')

#识别验证码
def Verify_Code(img):
    time.sleep(1)
    return  Verify_Code



if __name__ == '__main__':
    file=r"C:\Users\何博\Documents\important\AutoWebLog.xls"
    #打开文件
    wb = xlrd.open_workbook(filename=file)
    #通过索引获取表格sheet页
    sheet1 = wb.sheet_by_index(0)
    print('欢迎使用风飘飘自动登录~')
    #数据检查
    checkCmd = dataCheck(sheet1)
    if checkCmd:
        i=1
        while i < sheet1.nrows:
            url= sheet1.row(i)[1].value
            openweb(url)#打开网页
            img= sheet1.row(i)[0].value+"03.png" #登录验证
            location=pyautogui.locateOnScreen(img)
            if location is None:  #登录网站
                img= sheet1.row(i)[0].value+"05.png" #验证码
                if sheet1.row(i)[2].value==0:
                    Verify_Code(img)
                    inputbox(img, Verify_Code)#输入验证码
                img1= sheet1.row(i)[0].value+"01.png" #用户名图片
                img2= sheet1.row(i)[0].value+"02.png" #密码图片
                usrId= sheet1.row(i)[3].value       #用户名图片
                Paswd= sheet1.row(i)[4].value        #密码图片
                loginweb(img,usrId,Paswd)           #登录
            img= sheet1.row(i)[0].value+"04.png" #打卡验证
            location=pyautogui.locateCenterOnScreen(img)
            if location is not None:  #打卡
                pyautogui.click(location.x,location.y,1,interval=0.2,duration=0.2,)
                pyautogui.hotkey('ctrl', 'r')
            i += 1
        checkCmd=False
    else:
        print ("OVER!")

            
