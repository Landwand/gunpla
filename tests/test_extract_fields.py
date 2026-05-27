import pytest
from utils import extract_fields


class TestExtractFields():
    def test_valid_kit_returns_tuple_contains_success_true_and_list(self, serpent):
        # Arrange: handled by fixture

        # Act
        extracted = extract_fields(serpent, exceptions=None)

        # Assert
        assert type(extracted) == tuple
        assert extracted[0] == True # success bool
        assert type(extracted[1]) == list #list of Extracted fields
 

    def test_exceptions_contains_too_many_fields(self, serpent):
        # Arranged using fixture

        # Act 
        # these are all of the fields
        exceptions = [
            'name',
            'owner_id',
            'scale',
            'condition',
            'notes',
            'material',
            'grade'
            ]
        
        extracted = extract_fields(serpent, exceptions)
        
        # Assert

        assert type(extracted) == tuple
        assert extracted[0] == False # failure bool
        assert extracted[1] == {"error": "Count of Exceptions >= fields in KitModel"}

    
    def test_exceptions_correctly_omitted_in_return(self, serpent):
        # Arranged by fixture

        # Act
        exceptions = [
        'scale',
        'condition'
        ]

        extracted = extract_fields(serpent,exceptions)

        # Assert
        assert type(extracted) == tuple
        assert extracted[0] == True # success bool
        
        fields_list = extracted[1]

        all_keys = [k for pair in fields_list for k in pair]
        assert 'scale' not in all_keys
        assert 'condition' not in all_keys



