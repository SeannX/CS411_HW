from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal, 
    create_meal, 
    clear_meals, 
    delete_meal, 
    get_leaderboard, 
    get_meal_by_id, 
    get_meal_by_name, 
    update_meal_stats
)
def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
    
    return mock_cursor



######################################################
#
#    Add and delete Meal in db
#
######################################################
def test_create_meal(mock_cursor):
    """Test adding a new meal to the meals table."""
    create_meal("Pizza", "Italian", 12.0, "LOW")
    
    # Expected SQL query and parameters
    expected_query = "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)"
    expected_params = ("Pizza", "Italian", 12.0, "LOW")

    # Assert the query and parameters match expectations
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    actual_params = mock_cursor.execute.call_args[0][1]

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    assert actual_params == expected_params, f"Expected {expected_params}, but got {actual_params}."


def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate artist, title, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal, meals.cuisince, meals.price, meals.difficulty")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
        create_meal("Pizza", "Italian", 12.2, "LOW")


# Test creating a meal with invalid data
def test_create_meal_invalid_price():
    """Test error handling when creating a meal with invalid price."""

    with pytest.raises(ValueError, match="Invalid price: -100.2. Price must be a positive number."):
        create_meal("Pizza", "Italian", -100.2, "LOW")


def test_create_meal_invalid_difficulty():
    """Test error handling when creating a meal with invalid difficult."""

    with pytest.raises(ValueError, match="Invalid difficulty level: OTHER. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal("Pizza", "Italian", 10.2, "OTHER")


# Test clearing meal
def test_clear_meals(mock_cursor, mocker):
    """Test clearing all meals by recreating the meals table."""
    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meals_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meals_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


# Test deleting a meal by ID
def test_delete_meal(mock_cursor):
    """Test marking a meal as deleted in the database by meal ID."""
    mock_cursor.fetchone.return_value = ([False])
    delete_meal(1)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""
    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)


def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)


######################################################
#
#    Get Meals, Leaderboard
#
######################################################
# Test retrieving leaderboard
def test_get_leaderboard(mock_cursor):
    """Test retrieving the leaderboard, sorted by wins or win percentage."""
    


# Test retrieving a meal by ID
def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal from the database by its ID."""
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.0, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Pizza", "Italian", 12.0, "LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)


def test_get_deleted_meal_by_id(mock_cursor):
    #meal's deleted field set to TRUE
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.0, "LOW", True)

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)


# Test retrieving a meal by name
def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal from the database by its name."""
    # Simulate that the meal exists (meal = "Pizza")
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.0, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_name("Pizza")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Pizza", "Italian", 12.0, "LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Pizza",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_name_bad_name(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with name bla not found"):
        get_meal_by_name("bla")


def test_get_deleted_meal_by_name(mock_cursor):
    #meal's deleted field set to TRUE
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.0, "LOW", True)

    with pytest.raises(ValueError, match="Meal with name Pizza has been deleted"):
        get_meal_by_name("Pizza")


def test_get_leaderboard(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Italian", 15.0, "MED", 10, 8, 0.8),
        (2, "Meal B", "Chinese", 12.0, "LOW", 5, 3, 0.6)
    ]

    # Call get_leaderboard with a valid sort_by parameter ("wins")
    leaderboard = get_leaderboard(sort_by="wins")

    # Expected result based on the mock data
    expected_leaderboard = [
        {'id': 1, 'meal': "Meal A", 'cuisine': "Italian", 'price': 15.0, 'difficulty': "MED", 'battles': 10, 'wins': 8, 'win_pct': 80.0},
        {'id': 2, 'meal': "Meal B", 'cuisine': "Chinese", 'price': 12.0, 'difficulty': "LOW", 'battles': 5, 'wins': 3, 'win_pct': 60.0}
    ]
    assert leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, but got {leaderboard}"

    expected_query = """
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0 ORDER BY wins DESC
    """
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert normalize_whitespace(expected_query) == actual_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_invalid_sort_by():
    """Test that get_leaderboard raises a ValueError for an invalid sort_by parameter."""
    
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        get_leaderboard(sort_by="invalid_sort")

######################################################
#
#    Update Meals
#
######################################################

# Test updating meal statistics
def test_update_meal_stats_win(mock_cursor):
    """Test updating the battle statistics of a meal."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and winning the battle
    meal_id = 1
    update_meal_stats(meal_id, "win")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_meal_stats_lose(mock_cursor):
    """Test updating the battle statistics of a meal."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and winning the battle
    meal_id = 1
    update_meal_stats(meal_id, "loss")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1 WHERE id = ?")

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."



# Test handling invalid result in update_meal_stats
def test_update_deleted_meal_stats(mock_cursor):
    """Test error handling when updating meal stats with an invalid result."""
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.0, "LOW", True)

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")


def test_update_not_founded_meal_stats(mock_cursor):
    """Test error when trying to update a non-existent meal."""
    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to update a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)


def test_update_meal_stats_invalid_result(mock_cursor):
    """Test error handling when updating meal stats with an invalid result."""
    mock_cursor.fetchone.return_value = [False]
    meal_id = 1

    with pytest.raises(ValueError, match="Invalid result: invalid result. Expected 'win' or 'loss'."):
        update_meal_stats(meal_id, "invalid result")