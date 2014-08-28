__author__ = 'Peter_Howe<haobibo@gmail.com>'

'''
此脚本用于根据csv格式文件的第一列作为主键，
按照指定的列，将一个文件依GrouBy的列进行GroupBy拆分
文件中，列分隔符可以是Tab键，或者半角英文逗号
'''
#from collections import OrderedDict

inputFile = r'E:/features/Sina2013output(all users 3w).csv'
outputFolder = r'E:/features/byMonth/'
GroupBy = 'Month'

nCol = 0
data = {}
files = {}
headerCols = None

def getFile(groupBy):
    global files
    try:
        f = files[groupBy]
    except:
        f = open(outputFolder + groupBy + '.csv','a')
        f.write(headerCols[0])
        for col in headerCols[1:]:
            print(col)
            if col==GroupBy:continue
            f.write(',%s' % col)
        f.write('\n')
        files[groupBy] = f

    return f

def closeFiles():
    global files
    for k,v in files.iteritems():
        v.close()

with open(inputFile,'r') as f:
    #表头处理
    line = f.readline()
    spliter = "," if "," in line else "\t"
    headerCols = line.strip(' \n\t').split(spliter)

    for i in range(0,len(headerCols)):
        if headerCols[i] == GroupBy:
            groupCol = i
            break

    for line in f:
        cols = line.strip(' \n\t').split(spliter)
        group = cols.pop(groupCol)

        allZeros = True
        for col in cols[1:]:
            try:
                v = float(col)
                if v!=0.0:
                    allZeros = False
                    break
            except ValueError as e:
                pass

        if allZeros: continue

        fout = getFile(group)
        fout.write(cols[0])
        for col in cols[1:]:
            fout.write(',%s' % col)
        fout.write('\n')

    closeFiles()