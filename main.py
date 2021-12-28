import math
import os

import jieba
import jieba.posseg as pseg
import re
import sys
import xlwt

# 导入用于对象保存与加载的joblib
import  joblib
import fasttext

# 停用词
# 创建停用词列表
def get_stopwords_list():
    stopwords = [line.strip() for line in open('./hoteldata/stopwords.txt',encoding='UTF-8').readlines()]
    return stopwords

# 对句子进行中文分词
def seg_depart(sentence):
    # 对文档中的每一行进行中文分词
    depart_list = []
    for i in sentence:
        sentence_depart = jieba.lcut(i.strip(),cut_all=False)
        # move_stopwords(sentence_depart, stopwords)
        depart_list.append(sentence_depart)
    return depart_list

def remove_digits(input_str):
    punc = u'、一二三四五六七0123456789,!，。！-'
    output_str = re.sub(r'[{}]+'.format(punc), '', input_str)
    return output_str

# 去除停用词
def move_stopwords(sentence_list, stopwords_list):
    # 去停用词
    out_list = []
    for word in sentence_list:
        if word not in stopwords_list:
            if not remove_digits(word):
                continue
            if word != '\t':
                out_list.append(word)
    return out_list
#   用python 读取配置文件 然后将数据分成列表

def read_config(config):
    out_list = []
    # Open file

    fileHandler = open(config, "r")
    while True:
        # Get next line from file
        line = fileHandler.readline()
        # If line is empty then end of file reached
        if not line:
            break;
        print(line.strip())
        out_list.append(line)
        # Close Close
    fileHandler.close()
    return out_list

def readfullnames():
    fullnamelist =[]
    for dir in os.listdir(os.getcwd()+'/train/wenbenfenleiku'):
        try:
            for filename in os.listdir(os.getcwd()+'/train/wenbenfenleiku/'+dir):
                fullname= os.getcwd()+'/train/wenbenfenleiku/'+dir+'/'+filename
                #print(fullname)
                fullnamelist.append(fullname)
        except:
            continue
    return fullnamelist

def readfillnames():
    fillnamelist=[]
    for dir in os.listdir(os.getcwd()+'/train/jieci'):
        fillname = os.getcwd()+'/train/jieci/'+dir+'/'+dir+'.txt'
        print(fillname)
        fillnamelist.append(fillname)
    return fillnamelist

def write_words(word_dict,dfs):
    for k in word_dict.items():
        st = ''.join(['%s : %s' % k])
        dfs.write(st)
        dfs.write('\n')

def segfile(fullname_list):
    all_stopwords_list = get_stopwords_list()
    # 这两个map的区别

    # 统计一个词在 该类别下   统计一个词在多少篇文章中出现，每篇文章中最多统计一次
    words_dic = {}

    # 统计一个词在  该类别下  所有文章中出现的次数
    all_words = {}
    i = 1
    name_temp = "neg"
    for fullname in fullname_list:
        i += 1
        dfs = open(os.getcwd()+'/train/jieci/'+name_temp+'/'+name_temp+'.txt','w')
        ddfs = open(os.getcwd()+'/train/jieci/'+name_temp+'/cipin/'+name_temp+'.txt','w')
        dirname = fullname.split(os.getcwd()+'/train/wenbenfenleiku/')[1].split('/')[0]
        if i==5:
            print(dirname)
        if name_temp != dirname:
            write_words(words_dic,dfs)
            write_words(all_words,ddfs)
            words_dic.clear()
            all_words.clear()
            name_temp=dirname

        filename = fullname.split('/')[-1]
        print (fullname)
        # 二进制读取很关键，否则会有乱码发生
        ifs = open(fullname,'rb')
        print(os.getcwd()+'/train/jieci/'+dirname+'/'+filename)
        ofs = open(os.getcwd()+'/train/jieci/'+dirname+'/'+filename,'w')
        # 存放一次循环中的所有分词，不重复的分词，也就是一篇文章中
        words_temp = []
        for line in ifs.readlines():
            try:
                line = line.decode('gbk').encode('utf-8').strip()

                line = remove_digits(line.decode('utf-8'))

                words_list = []
                result = pseg.lcut(line)
                # 对于酒店情感分类问题，主要有用的是形容词 和副词
                # 现在只是保留形容词和副词
                for x in result:
                    if (x.flag == 'a' or x.flag == 'd'):
                        words_list.append(x.word)
                print(words_list)
            except:
                print('zhc'+os.getcwd()+'/train/jieci/'+dirname+'/'+filename)
                continue
            for w in words_list:
                if w.strip()== '':
                    continue
                if w in all_stopwords_list:
                    continue
                if w not in words_temp:
                    words_temp.append(w)
                if w not in all_words.keys():
                    all_words[w] = 1
                else:
                    all_words[w] += 1
                print(w)
                ofs.write(w+' ')
            ofs.write('\n')
        for t in words_temp:
            if t not in words_dic.keys():
                words_dic[t] = 1
            else:
                words_dic[t] +=1
        ifs.close()
        ofs.close()
        dfs.close()
        ddfs.close()
    # 这个目录下存放的是单个类别下的词典，也就是一个词在该类下的多少篇文章中出现过
    dfs = open(os.getcwd() + '/train/jieci/' + name_temp + '/' + name_temp + '.txt', 'w')
    write_words(words_dic,dfs)
    dfs.close()
    # 这个目录下存放的是单个类别下的词频，也就是一个词，在该类的所有文章中出现的次数
    ddfs = open(os.getcwd() + '/train/jieci/' + name_temp + '/cipin/' + name_temp + '.txt', 'w')
    write_words(all_words,ddfs)
    ddfs.close()
# zidian.txt 里存放的是，一个单词在多少的文章中出现
# 这个文章包括消极和积极的
# 所有文章

# 这个叫统计总字典
def sumdic(list):
    dic = {}
    print(list)
    for file in list:
        try:
            dfs = open(file,'r')
            for line in dfs.readlines():
                key = line.split(':')[0].strip()
                value = int(line.split(':')[-1].strip())
                if key not in dic.keys():
                    dic[key] = value
                else:
                    dic[key] += value
                # print("程序运行中...")
        except:
            print("open file exception!!!")
            continue
    # 将次数少于10次的词删除,先把字典中的key记录下来，然后在删除
    list_key = []
    for t in dic.keys():
        if dic[t] < 10:
            #del dic[t]
            list_key.append(t)
    for del_key in list_key:
        del dic[del_key]

    afs = open(os.getcwd()+'/train/zidian.txt','w')
    write_words(dic,afs)
    afs.close()

# 读取每个类别的词频的路径
def readcipin_fullnames():
    cipin_name_list = []
    for dir in os.listdir(os.getcwd()+'/train/jieci/'):
        file_name = os.getcwd()+'/train/jieci/'+dir+'/cipin/'+dir+'.txt'
        cipin_name_list.append(file_name)
    return cipin_name_list

# 统计总词频，就是统计一个单词在所有文章中出现的频率

def sum_cipin_dic():
    cipin_dic = {}
    cipin_fullnamelist = readcipin_fullnames()
    print(cipin_fullnamelist)

    for file in cipin_fullnamelist:
        try:
            dfs = open(file,'r')
            for line in dfs.readlines():
                key = line.split(':')[0].strip()
                value = int(line.split(':')[-1].strip())
                if key not in cipin_dic.keys():
                    cipin_dic[key] = value
                else:
                    cipin_dic[key] += value
        except:
            continue
    # 出现次数少于10次的词的干掉
    list_key = []
    for t in cipin_dic.keys():
        if cipin_dic[t] < 10:
            # del dic[t]
            list_key.append(t)
    for del_key in list_key:
        del cipin_dic[del_key]


    afs = open(os.getcwd()+'/train/cipinzidian.txt','w')
    write_words(cipin_dic,afs)
    afs.close()

#对每个类别进行编号 消极是1 积极2
#也就是打标签
def create_classname_dict():
    classname_dict = {}
    classname_dict['neg'] = 1
    classname_dict['pos'] = 2
    return classname_dict

# 获取总的字典，代表一个词 在多少篇文章中出现
def get_worddict():
    dic = {}
    afs = open(os.getcwd()+'/train/zidian.txt','r')
    for line in afs.readlines():
        key = line.split(':')[0].strip()
        value = int(line.split(':')[-1].strip())
        dic[key] = value
    afs.close()
    return dic

# 获取总词频
def get_cipinworddict():
    dic = {}
    afs = open(os.getcwd()+'/train/cipinzidian.txt','r')
    for line in afs.readlines():
        key = line.split(':')[0].strip()
        value = int(line.split(':')[-1].strip())
        dic[key] = value
    afs.close()
    return dic

#读取每个类别的词频字典

def get_class_cipinworddict(name_temp):
    dic = {}
    afs = open(os.getcwd() + '/train/jieci/'+name_temp+'/cipin/'+name_temp+'.txt', 'r')
    for line in afs.readlines():
        key = line.split(':')[0].strip()
        value = int(line.split(':')[-1].strip())
        dic[key] = value
    afs.close()
    return dic

# 获取所有的分词文件

def get_fullname_list():
    fullnamelist = []
    for dir in os.listdir(os.getcwd() + '/train/jieci'):
        for filename in os.listdir(os.getcwd() + '/train/jieci/' + dir):
            # print(type(filename))
            if filename == 'neg.txt':
                print('neg.txt')
                continue
            if filename == 'pos.txt':
                print('pos.txt')
                continue
            if filename == 'cipin':
                print('cipin')
                continue
            fullname = os.getcwd() + '/train/jieci/' + dir + '/' + filename
            # print(fullname)
            fullnamelist.append(fullname)

    return fullnamelist

# 创建特征文件

def create_feature_file():
    classname_dict = create_classname_dict()

    # 获取总的字典，代表一个词 在多少篇文章中出现
    worddict = get_worddict()

    # 获取总词频，就是统计一个单词在所有文章中出现的频率
    cipin_dict = get_cipinworddict()

    #获取总词典的所有key 值
    array_worddict = list(worddict.keys())

    # 获取所有分词文件的全路径
    fullname_list = get_fullname_list()


    # 新建一个特征向量文件
    ofs = open(os.getcwd()+'/train/'+'featurefile.txt','w')

    temp_class = ''
    for fullname in fullname_list:
        str = ''

        # dirname有两个值 neg pos
        dirname = fullname.split(os.getcwd()+'/train/jieci/')[1].split('/')[0]

        for classname in classname_dict.keys():
            if classname in fullname:
                # 只会取得两个值 1 2
                classno = classname_dict[classname]
                break
        # 代码写的有问题，不应该每次都 读取分类词频，应该读取两次就行了
        if temp_class != dirname:
            # 读取每个类别的词频字典
            class_cipindict = get_class_cipinworddict(dirname)
            temp_class = dirname
            print (dirname)
        # classno = -1
        str = repr(classno) + ' '

        # 打开分词文件
        ifs_curfile = open(fullname,'r')

        # 统计每个词在每篇文章中出现的次数tf
        print(fullname)
        file_worddict = {}
        try:
            for line in ifs_curfile.readlines():
                words = line.rstrip().split()
                for w in words:
                    if w not in file_worddict:
                        file_worddict[w] = 1
                    else:
                        file_worddict[w] += 1
        except:
            print("exception 369")
            print(fullname)
        # print('zhc')
        # print(len(array_worddict))
        for wordno in range(0,len(array_worddict)):
            # tf 是在一篇文章中出现的次数
            tf = 0
            # ctf 是在这类文章中，出现的次数
            ctf = 0
            # all_ctf 是在该类中，所有词条个数
            all_ctf = 0
            # 用下标访问list
            w = array_worddict[wordno]
            if w in file_worddict.keys():
                tf = file_worddict[w]
                print(tf)
                try:
                    ctf = class_cipindict[w]
                    print(ctf)
                    array_cipin = list(class_cipindict.keys())
                    all_ctf = len(array_cipin)
                except:
                    continue
                print (all_ctf)
            df = worddict[w]
            # weight = 1.0*tf * math.log((2000.0/df),2)
            # tf = ctf/all_ctf
            if all_ctf==0:
                all_ctf = 1
            weight = (ctf/all_ctf) * math.log((2000.0 / df), 2)
            str += repr(wordno+1) + ':' + repr(weight) + '  '
        ofs.write(str.rstrip()+'\n')
    ofs.close()

def create_test_feature_file(query):
    # 新建一个特征向量测试文件
    # 把这一个词进行处理，得到数据写进入文件
    # 1.去掉数字，特殊符号
    # 2.进行切词，保留形容词和副词
    # 3.去除停用词
    # 4.计算每个词的权重，形成特征文件
    # 这里有个疑问这个 文章总数怎么进行计算呢，这里1篇文章，最后就是

    line = remove_digits(query)
    all_words = []
    words_list = []
    result = pseg.lcut(line)
    # 对于酒店情感分类问题，主要有用的是形容词 和副词
    # 现在只是保留形容词和副词
    for x in result:
        if (x.flag == 'a' or x.flag == 'd'):
            words_list.append(x.word)
    print(words_list)
    all_stopwords_list = get_stopwords_list()
    for w in words_list:
        if w.strip() == '':
            continue
        if w in all_stopwords_list:
            continue
        all_words.append(w)
        print(w)
    # 通过分词的记录来把 特征文件计算出来
    # 统计每个词在每篇文章中出现的次数tf
    file_worddict = {}
    try:
        for w in all_words:
            if w not in file_worddict:
                file_worddict[w] = 1
            else:
                file_worddict[w] += 1
    except:
        pass
    tf = 0
    df = 0
    # 获取总的字典，代表一个词 在多少篇文章中出现
    worddict = get_worddict()

    # 获取总词典的所有key值 ,主要是为了计算特征向量使用
    array_worddict = list(worddict.keys())

    # 再进行计算特征向量文件
    ofs = open(os.getcwd() + '/train/' + 'featurefile_test.txt', 'w')
    str = ''
    for w in list(file_worddict.keys()):

        try:
            # 本篇文章中出现的次数
            tf = file_worddict[w]
            # 在多少篇文章中出现过
            df = worddict[w]
        except:
            df = 0
        if df == 0:
            # 防止分母为零
            df += 1
        weight = 1.0 * tf * math.log((2000.0/df),2)
        wordno = 0
        for wordno in range(0,len(array_worddict)):
            key = array_worddict[wordno]
            if key in file_worddict.keys():
                del file_worddict[key]
                break

        str += repr(wordno + 1) + ':' + repr(weight) + '  '
    print(str)
    ofs.write(str.rstrip() + '\n')
    ofs.close()
    # file_worddict 统计的是词频tf  就是在 这篇文章中出现的次数

def seg_cixing():
    fenci_list = []
    result = pseg.lcut("酒店很脏，Wi-Fi信号差，服务员态度不好，交通不方便,屋子小，热水器里的水很凉")
    print(result)
    for x in result:
        print(x.flag)
        print(x.word)
        if(x.flag=='a' or x.flag =='d'):
            fenci_list.append(x.word)
    print(fenci_list)





if __name__ == '__main__':
    for dir in os.listdir(os.getcwd()+'/train/wenbenfenleiku'):
        print(dir)
        if not os.path.exists(os.getcwd()+'/train/jieci/'+dir):
            print(os.getcwd()+'/train/jieci/'+dir)
            os.mkdir(os.getcwd()+'/train/jieci/'+dir)

# 读取所有对txt 文件的 全路径后续使用
# fullname_list= readfullnames()

# 读取分类数据里新建立的两个文本文件的全目录
# fillname_list = readfillnames()

# 对每一个txt文件进行分词处理

# segfile(fullname_list)

# 统计总词典
# sumdic(fillname_list)

# 统计总的词频
# sum_cipin_dic()

# 以上两步骤相当于找到了每个词的特征向量

# 下面开始向量化
# create_feature_file()

# 建立一个测试集的特征向量 #参数接一个string
str = "这个酒店服务非常的差，房间潮湿，没有网络,酒店很脏，Wi-Fi信号差，服务员态度不好，交通不方便,屋子小，热水器里的水很凉"
str1 = "这次是元旦期间入住的，酒店装修不是很新，但是比较干净。房间比想象当中的大，正好面对门口的河，风景还算不错。" \
       "房间不能开窗，感觉空调不是太好。入住和退房比较快。离地铁有点远，" \
       "但是门口有公交或者可以打的（起步价即可）到沙田火车站转轨道交通。酒店的早餐很难吃，" \
       "但是酒店附近有很多餐馆，蛮实惠的。附近还有屈臣氏和711便利店，买点日用品或者零食饮料也很方便。" \
       "考虑到性价比高，今后仍有可能还住这里。"
create_test_feature_file(str)
'''
1  将已有的特征文件进行缩放，将所有没有用的数字（如：0）剔除掉；
svm-scale -l 0 -u 1 -s temp.txt featurefile.txt > feature_scale.txt
2  而该局是用步骤1生成的缩放标准来缩放，测试数据
svm-scale -r temp.txt txt_featurefile.txt > txt_feature_scale.txt
3  将步骤1缩放后的特征文件进行训练，即得到model.txt训练标准文件
svm-train -c 32.0 -g 0.0078125 feature_scale.txt model.txt
4  用步骤3得到的model.txt文件来测试步骤2、得到的特征文件，将结构输出至result.txt
svm-predict txt_feature_scale.txt model.txt result.txt
'''