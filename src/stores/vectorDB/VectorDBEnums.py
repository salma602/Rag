from enum import Enum
class VectorDBEnums(str, Enum):
    QDRANT = "QDRANT"

class DistanceMethodEnums(Enum):
    COSINE = "COSINE"
    DOT = "DOT"
