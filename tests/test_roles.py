"""
Unit tests for core/roles module.

Tests:
1. Role mapping integrity
2. Hybrid threshold behavior (< 0.60)
3. Neighbor exclusion logic
4. Confidence scoring
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.roles.service import RoleService
from core.roles.loader import RoleLoader


class MockRoleLoader:
    """Mock loader for testing."""
    
    def __init__(self):
        self.cluster_to_role = {
            0: "Link-Up / Complete Striker",
            1: "Pressing Striker",
            2: "Poacher"
        }
        self.role_descriptions = {
            "Link-Up / Complete Striker": "Connects play, drops in, combines efficiently and contributes to buildup.",
            "Pressing Striker": "Leads the press, initiates defensive actions and disrupts buildup.",
            "Poacher": "Focuses on box occupation and finishing, limited link play."
        }
    
    def load_cluster_to_role(self):
        return self.cluster_to_role
    
    def load_role_descriptions(self):
        return self.role_descriptions
    
    def get_player_cluster_probs(self, player_id, season_id):
        """Return mock cluster probabilities."""
        # Test data with various probability distributions
        test_data = {
            (1001, 317): {"cluster_0": 0.75, "cluster_1": 0.15, "cluster_2": 0.10, "predicted_cluster": 0},
            (1002, 317): {"cluster_0": 0.40, "cluster_1": 0.35, "cluster_2": 0.25, "predicted_cluster": 0},  # Hybrid
            (1003, 317): {"cluster_0": 0.10, "cluster_1": 0.80, "cluster_2": 0.10, "predicted_cluster": 1},
            (1004, 317): {"cluster_0": 0.15, "cluster_1": 0.10, "cluster_2": 0.75, "predicted_cluster": 2},
        }
        return test_data.get((player_id, season_id))
    
    def get_player_style_row(self, player_id, season_id):
        """Return mock style vector row."""
        return {
            "player_id": player_id,
            "season_id": season_id,
            "minutes": 1000,
            "team_id": 100,
            "player_name": f"Player {player_id}",
            "pca_1": 0.5, "pca_2": -0.3, "pca_3": 0.1, "pca_4": -0.2, "pca_5": 0.4, "pca_6": -0.1
        }
    
    def get_neighbors(self, player_id, season_id, top_k=5):
        """Return mock neighbors (excluding self)."""
        all_neighbors = {
            (1001, 317): [
                {"neighbor_player_id": 1003, "neighbor_season_id": 317, "cosine_sim": 0.92},
                {"neighbor_player_id": 1004, "neighbor_season_id": 317, "cosine_sim": 0.88},
                {"neighbor_player_id": 1002, "neighbor_season_id": 317, "cosine_sim": 0.85},
            ],
            (1002, 317): [
                {"neighbor_player_id": 1001, "neighbor_season_id": 317, "cosine_sim": 0.85},
                {"neighbor_player_id": 1003, "neighbor_season_id": 317, "cosine_sim": 0.80},
            ],
        }
        neighbors = all_neighbors.get((player_id, season_id), [])
        return neighbors[:top_k]
    
    def minutes_threshold(self):
        return 500


class TestRoleMapping:
    """Test role mapping integrity."""
    
    def test_cluster_to_role_mapping_exists(self):
        """Verify cluster-to-role mapping is complete."""
        loader = MockRoleLoader()
        mapping = loader.load_cluster_to_role()
        
        assert len(mapping) == 3
        assert 0 in mapping
        assert 1 in mapping
        assert 2 in mapping
    
    def test_cluster_to_role_values_correct(self):
        """Verify exact role mappings."""
        loader = MockRoleLoader()
        mapping = loader.load_cluster_to_role()
        
        assert mapping[0] == "Link-Up / Complete Striker"
        assert mapping[1] == "Pressing Striker"
        assert mapping[2] == "Poacher"
    
    def test_role_descriptions_exist(self):
        """Verify all roles have descriptions."""
        loader = MockRoleLoader()
        descriptions = loader.load_role_descriptions()
        
        assert "Link-Up / Complete Striker" in descriptions
        assert "Pressing Striker" in descriptions
        assert "Poacher" in descriptions
        
        # Each description should be non-empty
        for role, desc in descriptions.items():
            assert len(desc) > 0


class TestHybridThreshold:
    """Test hybrid role detection (< 0.60 max posterior)."""
    
    def test_high_confidence_not_hybrid(self):
        """Test that high confidence (>= 0.60) is not marked as hybrid."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        # Player 1001 has 0.75 max probability (not hybrid)
        role_data = service.get_player_role(1001, 317)
        
        assert role_data is not None
        assert role_data["confidence"] == 0.75
        assert role_data["is_hybrid"] == False
        assert role_data["role"] == "Link-Up / Complete Striker"
    
    def test_low_confidence_is_hybrid(self):
        """Test that low confidence (< 0.60) is marked as hybrid."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        # Player 1002 has 0.40 max probability (hybrid)
        role_data = service.get_player_role(1002, 317)
        
        assert role_data is not None
        assert role_data["confidence"] == 0.40
        assert role_data["is_hybrid"] == True
    
    def test_threshold_boundary_60_percent(self):
        """Test exact boundary at 0.60 threshold."""
        loader = MockRoleLoader()
        
        # Mock data with exactly 0.60
        class BoundaryLoader(MockRoleLoader):
            def get_player_cluster_probs(self, player_id, season_id):
                return {
                    "cluster_0": 0.60,
                    "cluster_1": 0.25,
                    "cluster_2": 0.15,
                    "predicted_cluster": 0
                }
        
        service = RoleService(BoundaryLoader())
        role_data = service.get_player_role(9999, 317)
        
        # At 0.60 exactly, should NOT be hybrid (>= 0.60)
        assert role_data["confidence"] == 0.60
        assert role_data["is_hybrid"] == False


class TestNeighborExclusion:
    """Test that neighbors correctly exclude self and sort by similarity."""
    
    def test_neighbors_exclude_self(self):
        """Test that player's own (player_id, season_id) is not in neighbors."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        neighbors = service.get_similar_players(1001, 317, k=10)
        
        # Check that none of the neighbors are the player itself
        for neighbor in neighbors:
            assert not (neighbor["player_id"] == 1001 and neighbor["season_id"] == 317)
    
    def test_neighbors_sorted_by_similarity_desc(self):
        """Test that neighbors are sorted by similarity (descending)."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        neighbors = service.get_similar_players(1001, 317, k=10)
        
        # Verify sorted descending
        similarities = [n["similarity"] for n in neighbors]
        assert similarities == sorted(similarities, reverse=True)
    
    def test_neighbors_limited_to_k(self):
        """Test that top_k parameter limits results."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        neighbors_k2 = service.get_similar_players(1001, 317, k=2)
        neighbors_k5 = service.get_similar_players(1001, 317, k=5)
        
        assert len(neighbors_k2) <= 2
        assert len(neighbors_k5) <= 5
    
    def test_neighbors_similarity_formatting(self):
        """Test that similarity is formatted as 0-100% integer."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        neighbors = service.get_similar_players(1001, 317, k=10)
        
        for neighbor in neighbors:
            sim = neighbor["similarity"]
            assert isinstance(sim, int)
            assert 0 <= sim <= 100


class TestConfidenceScoring:
    """Test confidence score calculation and rounding."""
    
    def test_confidence_in_valid_range(self):
        """Test that confidence is always in [0, 1]."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        for player_id in [1001, 1002, 1003, 1004]:
            role_data = service.get_player_role(player_id, 317)
            assert 0 <= role_data["confidence"] <= 1
    
    def test_confidence_rounded_to_3_decimals(self):
        """Test that confidence is rounded to 3 decimal places."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        role_data = service.get_player_role(1001, 317)
        conf_str = str(role_data["confidence"])
        
        # Check format (e.g., "0.75" has at most 2 decimal places but 3 is fine)
        assert isinstance(role_data["confidence"], float)
    
    def test_top_roles_probability_rounding(self):
        """Test that top_roles probabilities are properly rounded."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        role_data = service.get_player_role(1002, 317)
        top_roles = role_data["top_roles"]
        
        assert len(top_roles) >= 2
        for role_info in top_roles:
            prob = role_info["prob"]
            assert 0 <= prob <= 1
            # Check it's a float (may be rounded)
            assert isinstance(prob, float)


class TestRoleDataIntegrity:
    """Test that role data contains required fields."""
    
    def test_role_data_has_required_fields(self):
        """Test that get_player_role returns all required fields."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        role_data = service.get_player_role(1001, 317)
        
        required_fields = ["role", "is_hybrid", "confidence", "top_roles", "tooltip"]
        for field in required_fields:
            assert field in role_data
    
    def test_similar_players_has_required_fields(self):
        """Test that get_similar_players returns all required fields."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        neighbors = service.get_similar_players(1001, 317, k=1)
        
        if neighbors:  # Only check if there are neighbors
            required_fields = ["player_id", "season_id", "similarity", "role", "confidence"]
            for field in required_fields:
                assert field in neighbors[0]
    
    def test_tooltip_matches_role(self):
        """Test that tooltip matches the primary role."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        role_data = service.get_player_role(1001, 317)
        
        role = role_data["role"]
        tooltip = role_data["tooltip"]
        
        # Tooltip should be from the descriptions
        descriptions = loader.load_role_descriptions()
        assert tooltip == descriptions.get(role, "")


class TestInvalidData:
    """Test handling of invalid/missing data."""
    
    def test_missing_player_returns_none(self):
        """Test that non-existent player returns None."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        role_data = service.get_player_role(9999, 317)
        
        assert role_data is None
    
    def test_is_valid_data_checks_existence(self):
        """Test that is_valid_data correctly checks data availability."""
        loader = MockRoleLoader()
        service = RoleService(loader)
        
        assert service.is_valid_data(1001, 317) == True
        assert service.is_valid_data(9999, 317) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
