from prover import Prover
from verifier import Verifier
from main import ExtensionField

class Vole:
  def __init__(self, m) -> None:
    self.field = ExtensionField(m)
    self.p = Prover(self.field)
    self.v = Verifier(self.field)
    self.shared_secret()

  def shared_secret(self):
    self.qs = [(vi+ui*delta) % 2 for (vi,ui,delta) in zip(self.p.v, self.p.u, self.v.delta)]

  def commit(self, w):
    ui = self.p.u[0]
    vi = self.p.v[0]
    
    di = ui ^ vi

    qi = (self.qs[0] + di*self.v.delta[0]) % 2

    
