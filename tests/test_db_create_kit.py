from unittest.mock import patch, MagicMock
from db import db_create_kit
import sqlite3


class TestDBCreateKit:
    def test_create_kit_success(self, serpent) -> None:
        # ARRANGE: set the stage
        # `serpent` arrives from conftest.py by name. pytest matches the
        # parameter name to the fixture and passes it in. No import needed.
        data = serpent.model_dump()   # KitModel -> plain dict, the shape db_create_kit expects

        # A fake cursor. MagicMock accepts any call (like .execute(...))
        # without complaining, and records every call it gets.
        mock_cursor = MagicMock()

        # ACT: let the real code perform on a rigged stage
        # `with patch(...)` swaps the real db_get_cursor in db.py for a fake,
        # but ONLY inside this block. The real one comes back afterwards.
        # return_value=mock_cursor: whenever db_get_cursor() is called,
        # hand back our fake cursor. That's what the real one would
        # return: a cursor.
        with patch('db.db_get_cursor', return_value=mock_cursor):
            # Call the REAL function we're testing. It runs normally,
            # but where db_create_kit calls db_get_cursor(), it gets our fake cursor
            # so cursor.execute(...) touches no database.
            # The test never builds the result itself. db_create_kit does.
            result = db_create_kit(data)

        # ASSERT: review the performance
        # These check what db_create_kit RETURNED (our logic, the "cashier").
        assert result["success"] is True
        assert result["message"] == f"Kit {data.get('name')} created successfully"

        # Self-checking: raises on its own if execute wasn't called exactly
        # once, and returns None if it was. No `assert` in front.
        mock_cursor.execute.assert_called_once()


    def test_create_kit_db_error(self, serpent) -> None:
        # Arrange
        data = serpent.model_dump()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = sqlite3.Error("Database exploded!")

        # Act

        # the 'new=MagicMock' instructs MM to replace replace db.current_app 
        # with this exact object, and don’t inspect the original.
        with patch('db.db_get_cursor', return_value=mock_cursor), \
            patch('db.current_app', new=MagicMock()) as mock_app:
            result = db_create_kit(data)

        # Assert
        assert result["success"] is False
        assert result["error"] == "Database failed to create kit: Database exploded!"
        mock_app.logger.error.assert_called_once() # assert that this was actually used