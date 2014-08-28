__author__ = 'Peter_Howe<haobibo@gmail.com>'

'''
此脚本用于根据csv格式文件的第一列作为主键，将多个文件依主键按行合并
文件中，列分隔符可以是Tab键，或者半角英文逗号
'''

from collections import OrderedDict

def mergeCol(files, outputfile):
    header = ["SinaUid"]
    data = {}
    nCol = 0

    for flag in files:
        fname = files[flag]
        f = open(fname)
        lines = f.readlines()
        spliter = "," if "," in lines[0] else "\t"

        #表头处理
        headerCols = lines[0].strip(' \n\t,').split(spliter)[1:]
        for col in headerCols:
            header.append(flag + col)

        #数据从第二行开始
        for line in lines[1:]:
            line = line.strip(' \n\t,')
            fields = line.split(spliter)

            #第一列是UID，第二列开始是特征数据
            uid = fields[0].rstrip(".txt")
            values = fields[1:]
            #print(values)

            row = data.get(uid)
            if row is None:
                data[uid]=[]

            for value in values:
                data.get(uid).append(value)
                if len ( data.get(uid) )> nCol:
                    nCol = len( data.get(uid) )

    f = open(outputfile,"w")

    f.write(header[0])
    for h in header[1:]:
        f.write(","+h)

    for uid in data:
        if len( data[uid] ) < nCol:
            continue
        f.write("\n" + uid)
        for c in data[uid]:
            f.write(","+c)
'''
Month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
for month in Month:
    files=OrderedDict([
        ('',  u"E:/features/byMonth/%s.csv" % month),
        ('_',  u"E:/features/f_B.csv"),
    ])
    outputFile = r"E:/features/byMonthMerged/[%s].csv" % month
    mergeCol(files,outputFile)

'''


base = u'E:/Study/Research-Suicide/Data-用户实验/csv/'
outputFile = base + u'Merged.csv'
files=OrderedDict([
    ('S_', base + u"用户实验用户问卷数据.csv"),
    ('B_', base + u"用户实验微博行为数据.csv"),
    ('L_', base + u"用户实验微博内容数据.csv")
])
mergeCol(files,outputFile)
