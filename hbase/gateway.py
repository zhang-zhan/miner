# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import Hbase
from ttypes import *
from thrift.transport import *

cfg = {
    'host' : '192.168.21.51',
    'port' : 9090
}

def applyBatch(batches, hbase_cfg=cfg):

    # Connect to HBase Thrift server
    transport = TTransport.TBufferedTransport(TSocket.TSocket(**cfg))
    transport.open()

    # Create and open the client connection
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    client = Hbase.Client(protocol)
    for batch in batches:
        tableName = batch['tableName']
        rowBatches = batch['rowBatches']

        client.mutateRows(tableName,[rowBatches],None)

        #print("%5d mutations inserted into table %s." % (len(rowBatches.mutations),tableName))
    #print("----------------------")
    transport.close()
