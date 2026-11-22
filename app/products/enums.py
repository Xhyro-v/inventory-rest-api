from enum import Enum

class Reason(str, Enum):
    RESTOCK = "Restock"
    DAMAGED = "Damaged" 
    LOST = "Lost"
    MANUAL_CORRECTION = "Manual_Correction"
    BUY = "Buy"
    CANCEL_RESTOCK = "Cancel_Restock"   # baru