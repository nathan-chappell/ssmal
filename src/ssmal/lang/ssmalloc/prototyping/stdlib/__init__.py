from ssmal.lang.ssmalloc.internal.System import *

# NOTE:
# Importing the memory manager must happen first!
from ssmal.lang.ssmalloc.stdlib.TrivialMemoryManager import TrivialMemoryManager

mem = TrivialMemoryManager(Int(0x1000))
#
# NO ADDITIONAL IMPORTS ABOVE THIS LINE!!!
#

# from ssmal.lang.ssmalloc.stdlib.String import String
from ssmal.lang.ssmalloc.stdlib.TypeInfo import TypeInfo, MethodInfo, FieldInfo, ParameterInfo
from ssmal.lang.ssmalloc.internal.Reflection import Reflection
