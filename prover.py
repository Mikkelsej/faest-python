import random
from main import ExtensionField

class Prover:
  def __init__(self, field: ExtensionField) -> None:
    self.field = field
    self.u = [random.randint(0, 1) for _ in range(self.field.m)]
    self.v = [random.randint(0,1 )for _ in range(self.field.m)]




