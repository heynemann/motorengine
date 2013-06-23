import sys
sys.path[0:0] = [""]
import unittest

from tests.document.class_methods import *  # NOQA
from tests.document.delta import *  # NOQA
from tests.document.dynamic import *  # NOQA
from tests.document.indexes import *  # NOQA
from tests.document.inheritance import *  # NOQA
from tests.document.instance import *  # NOQA
from tests.document.json_serialisation import *  # NOQA
from tests.document.validation import *  # NOQA

if __name__ == '__main__':
    unittest.main()
