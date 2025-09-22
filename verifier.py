import random
from main import ExtensionField

class Verifier:
  def __init__(self, field: ExtensionField) -> None:
    self.field = field
    self.delta = self.field.elements[random.randint(0, 256)]
