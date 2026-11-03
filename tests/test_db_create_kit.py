from unittest.mock import patch, MagicMock
from db import db_create_kit


class TestDBCreateKit():
    def test_create_kit_success(self, serpent) -> None:
        # Arrange
        data = serpent.model_dump()
        mock_cursor = MagicMock()

        # Act
        with patch('db.db_get_cursor', return_value=mock_cursor):
            result = db_create_kit(data)

        # Assert
        assert result["success"] is True
        assert result["message"] == f"Kit {data.get('name')} created successfully"
        mock_cursor.execute.assert_called_once() 
        # a method in MagicMock to check if execute 
        # was called at least once; error if not, and None if ran. Assert won't work here as a result