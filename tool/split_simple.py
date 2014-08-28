__author__ = 'Peter_Howe<haobibo@gmail.com>'

perFile = 14
fileName = './Token.txt'
outputFolder = "./Splited/"

try:
    import os
    os.makedirs(outputFolder)
except:
    pass

i = 0;
fNumber = 0;
try:
    with open(fileName,'r') as infile:
        f = None
        for line in infile:
            if i % perFile == 0:
                if f is not None:
                    f.close()
                fNumber += 1
                f = open('%s%d.txt'%(outputFolder , fNumber),'w')
                print("Processing part %d" % fNumber)
            f.write(line)
            i += 1

except Exception as e:
    print(e)