from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol
import sys
import os


sys.path.insert(0, os.getenv("TM_THRIFT_DB"))

from db import CRUDDB, InfoDB
from db.ttypes import DataObject

from tm_logging.tm_logging import TmLogging

g_clients = None
fl_logger = TmLogging()

def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            fl_logger.error(f"File client error: {str(e)}")
            global g_clients
            g_clients = None
            get_thrift_clients()
    
    return wrapper

def get_thrift_clients():
    global g_clients

    if g_clients is not None:
        return g_clients

    transport = TSocket.TSocket('localhost', 5010)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Multiplexed protocol for CRUDDB service
    crud_protocol = TMultiplexedProtocol(protocol, "CRUDDB")
    crud_client = CRUDDB.Client(crud_protocol)

    # Multiplexed protocol for InfoDB service
    info_protocol = TMultiplexedProtocol(protocol, "InfoDB")
    info_client = InfoDB.Client(info_protocol)

    transport.open()

    g_clients = (crud_client, info_client)

    return crud_client, info_client

@handle_exceptions
def read_data(universe, galaxy, solar):
    client, _ = get_thrift_clients()
    response = client.read('{}->{}->{}'.format(universe, galaxy, solar))

    if response.error:
        fl_logger.error(response.error)
    
    return response.dataObjects

@handle_exceptions
def append_data(universe, galaxy, solar, dict_):
    client, _ = get_thrift_clients()

    data_object = DataObject(fields=dict_)
    response = client.create('{}->{}->{}'.format(universe, galaxy, solar), data_object)

    if response.error:
        fl_logger.error(response.error)

@handle_exceptions 
def delete_data(universe, galaxy, solar):
    client, _ = get_thrift_clients()

    response = client.delete('{}->{}->{}'.format(universe, galaxy, solar))

    if response.error:
        fl_logger.error(response.error)
    
    return response.error

@handle_exceptions
def get_books(universe, galaxy):
    _, info_client = get_thrift_clients()

    response = info_client.getSolarSystem("{}->{}".format(universe, galaxy))
    if response.error:
        fl_logger.error(response.error)
    
    return response.dataObjects