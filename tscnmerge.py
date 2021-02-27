import os

from TscnVisitor import parse
from model.TscnFile import TscnFile

mine: TscnFile = parse(os.getenv("LOCAL"))
theirs: TscnFile = parse(os.getenv("REMOTE"))

# Step 1: Patch together external resources
