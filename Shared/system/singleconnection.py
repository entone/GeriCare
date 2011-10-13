from pymongo import Connection
from decorators import singleton

@singleton
class SingleConnection(Connection):pass
    
