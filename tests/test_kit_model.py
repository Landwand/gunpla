from models.kit_model import KitModel
# from pydantic import ValidationError

class TestKitModel:
    """Test the KitModel validation logic"""
    
    def test_grade_only_hg_assigns_correct_scale(self):
        """Test: HG grade with no scale should auto-assign 144"""
        # Arrange
        guncannon = {'name' : "RX-77 Guncannon",
                     'grade' : "HG",
                     'scale' : None,                
                     }

        # Act
        kit = KitModel(**guncannon) #unpack the Dict

        # Assert
        assert kit.scale == 144
    
    def test_grade_only_mg_assigns_correct_scale(self):
        """Test: MG grade with no scale should auto-assign 100"""

        # Arrange
        barbatos = {'name': "ASW-G-08 Gundam Barbatos",
                'grade': "MG", 
                'scale': None}
        
        # Act
        kit = KitModel(**barbatos)

        # Assert
        assert kit.scale == 100

    def test_grade_only_pg_assigns_correct_scale(self):
        """Test: PG grade with no scale should auto-assign 60"""

        # Arrange
        gundam78 = {'name': "RX-78-2 Gundam",
                'grade': "PG", 
                'scale': None}
        
        # Act
        kit = KitModel(**gundam78)

        # Assert
        assert kit.scale == 60

    def test_grade_pg_w_trailing_whitespace_assigns_correct_scale(self):
        """Test: "PG " (whitespace included) with no scale should auto-assign 60"""

        # Arrange
        gundam78 = {'name': "RX-78-2 Gundam",
                'grade': "PG ", 
                'scale': None}
        
        # Act
        kit = KitModel(**gundam78)

        # Assert
        assert kit.scale == 60
    
    def test_grade_user_provided_scale_is_kept(self):
        """Test: User scale should override grade-based scale"""
        
        # Arrange
        ingram = {'name': "AV-98 Ingram 1",
                'grade': "MG", 
                'scale': 35}
        
        # Act
        kit = KitModel(**ingram)

        # Assert
        assert kit.scale == 35


    def test_grade_no_grade_match_returns_original_scale(self):
        """Test: Unknown grade should keep user's provided"""

        # Arrange
        sephiroth = {'name': "Sephiroth",
                'grade': 'Kotobukiya Resin', 
                'scale': 7}
        
        # Act
        kit = KitModel(**sephiroth)

        # Assert
        assert kit.scale == 7