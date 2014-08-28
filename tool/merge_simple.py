__author__ = 'Peter_Howe<haobibo@gmail.com>'

fmerge = open('./merged.txt','w',1)

for i in range(1,13):

    fname = "./%d.txt" % i
    f = open(fname,'r',1)
    lines = f.readlines()
    
    for l in lines[0:-1]:
        #l = l.split(',')[0]
        fmerge.write('%s'%l)
        #print(l)
        
    f.close()