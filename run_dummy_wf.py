
import random

from aiida import load_profile
from aiida.orm import Int, Code
from aiida.engine import submit
from aiida_dummy import DummyWorkChain


load_profile()

wf = DummyWorkChain.get_builder()
wf.code = Code.get_from_string('Dummy@yascheduler')

dice = random.randint(1, 100)

wf.foobar = Int(dice)

print(submit(DummyWorkChain, **wf))
