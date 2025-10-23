import sys
import os
sys.path.insert(0, os.getcwd())

from core.roles.service import get_role_service
from core.roles.loader import reset_role_loader

# Reset and reload
reset_role_loader()

# Test player 26353 (should be Poacher now)
service = get_role_service()
role = service.get_player_role(26353, 317)

print(f"Player 26353 role: {role['role']}")
print(f"Confidence: {role['confidence']}")
print(f"Description: {role['tooltip']}")
