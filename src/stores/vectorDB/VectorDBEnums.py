from enum import Enum
class VectorDBType(str, Enum):
    QDRANT = "QDRANT"

class DistanceMethodEnums(Enum):
    COSINE = "COSINE"
    DOT = "DOT"
