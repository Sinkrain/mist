from tkinter import *
from tkinter.filedialog import askdirectory
import os,gevent,gevent.pool
import urllib.request
import hashlib
import urllib
import random,json
import http.client


class simpleGUI():
    def __init__(self):
        window = Tk()

        self.sepath = StringVar()
        self.sapath = StringVar()

        # 类型选框
        penal = Frame(window)
        pena2 = Frame(window)
        self.type = IntVar()
        self.type.set(2)

        tp1=Radiobutton(penal,text = 'txt',command=self.filetype,variable = self.type,width=8,value=1)
        tp2=Radiobutton(penal,text = 'py',command=self.filetype,variable = self.type,width=8,value=2)

        # 翻译文件选择
        se_lable = Label(penal,text='选择路径')
        save_lable = Label(penal,text='保存路径')
        se_enter = Entry(penal,textvariable=self.sepath,width=30)
        sa_enter = Entry(penal,textvariable=self.sapath,width=30)
        se_button = Button(penal,text = '...',command=self.selectpath,padx=6)
        sa_button = Button(penal, text='...', command=self.savepath,padx=6)
        translate = Button(penal,text='翻译',pady=16,command=self.translation)


        tp1.grid(row=1, column=2)
        tp2.grid(row=1, column=3)
        se_lable.grid(row=2,column=1,sticky=E)
        save_lable.grid(row=3,column=1,sticky=E)
        se_enter.grid(row=2,column=2,columnspan =2,padx=2,ipady=3)
        sa_enter.grid(row=3,column=2,columnspan=2,padx=2,ipady=3)
        se_button.grid(row=2,column=4)
        sa_button.grid(row=3, column=4)
        translate.grid(row=2,rowspan=2,column=5)

        penal.pack(padx=5,pady=5)

        txt_lable = Label(pena2,text='---  详细信息  ---')
        self.text_box=Text(pena2,width=48,height=15)

        txt_lable.grid(row=1,column=1)
        self.text_box.grid(row=2,column=1,pady=2)
        pena2.pack()

        window.mainloop()


    def selectpath(self):
        path = askdirectory()
        self.sepath.set(path)

    def savepath(self):
        path = askdirectory()
        self.sapath.set(path)

    def filetype(self):
        print(self.type.get())


    def searchfile(self,slpath,svpath,add):
        alist = os.listdir(slpath)
        flist=[]
        slist=[]
        for li in alist:
            lpath = slpath + '/' +li
            spath = svpath + '/' +li
            if os.path.isfile(lpath) and li.endswith(add):
                flist.append(lpath)
                slist.append(spath)
                if not os.path.exists(svpath):
                    # 在保存的位置创建文件夹
                    os.makedirs(svpath)

            elif os.path.isdir(lpath):
                back = self.searchfile(lpath, spath,add)
                flist += back[0]
                slist += back[1]
        return [flist, slist]


    def interpret(self,line):
        appid = '20171110000094059'
        secretKey = '0u7yfvWgaLcWxIQAJYXR'

        httpClient = None
        myurl = '/api/trans/vip/translate'
        q = 'apple'
        fromLang = 'en'
        toLang = 'zh'
        salt = random.randint(32768, 65536)

        sign = appid + q + str(salt) + secretKey
        m1 = hashlib.md5()
        m1.update(sign.encode('utf-8'))
        sign = m1.hexdigest()
        myurl = myurl + '?appid=' + appid + '&q=' + urllib.request.quote(
            q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

        print(myurl)
        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)

            # response是HTTPResponse对象
            response = httpClient.getresponse()
            return json.loads(response.read())["trans_result"][0]["dst"]
        except Exception as e:
            print(e)
            return ''
        finally:
            if httpClient:
                httpClient.close()


    def translation(self):
        ftype = self.type.get()
        if ftype == 1:
            add = '.txt'
        else:
            add = '.py'
        slpath, svpath=self.sepath.get(),self.sapath.get()
        bank = self.searchfile(slpath,svpath,add)
        oldlist = bank[0]
        newlist = bank[1]
        for i in range(len(oldlist)):
            ofile = open(oldlist[i],'rb')
            nfile = open(newlist[i],'w')
            count = 0
            tag = False
            regex1 = re.compile('#')
            regex2 = re.compile('(\'\'\')|(\"\"\")')
            regex3 = re.compile('^.*?#(.*)')

            while True:
                try:
                    line = ofile.readline().decode('utf-8')
                except:
                    line =ofile.readline().decode('gbk','ignore')
                if not line:
                    break
                else:
                    if len(regex1.findall(line))>=1 and not tag:
                        # 判断是否需要翻译
                        print('-- 翻译 --',line)
                        if line.startswith('^\s*#'):
                            lline = line.split('#')[1]
                            line = self.interpret(lline)
                            nfile.write('#'+line)
                        else:
                            print('-- 翻译 --', lline)
                            rline = regex3.findall(line)[0]
                            lline = line.split('#')[0]
                            lline = self.interpret(lline)
                            nfile.write(lline+' # '+rline)

                    elif len(regex2.findall(line))==1 or tag:
                        print('-- 翻译 --', line)
                        line = self.interpret(line)
                        nfile.write(line)
                        if len(regex2.findall(line))==1:
                            count+=1
                        if count%2==0:
                            tag = False
                        else:
                            tag = True
                    elif len(regex2.findall(line))==2:
                        print('-- 翻译 --', line)
                        line = self.interpret(line)
                        nfile.write(line)
                    else:
                        nfile.write(line)
            ofile.close()
            nfile.close()
            self.text_box.insert(END,'\n%s  已完成翻译  '%i)

if __name__ == '__main__':
    simpleGUI()
    #time is too long
    #it`s seem to Rain, can we go to home?
