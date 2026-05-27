import pytest
from models.kit_model import KitModel


@pytest.fixture
def serpent():
    kit_data = {
        'name': 'Serpent Custom',
        'owner_id': 1,
        'scale': 144,
        'condition': 'bags opened',
        'notes': 'fighting action HG',
        'material': 'plastic',
        'grade': 'HG'
    }
    return KitModel(**kit_data)
