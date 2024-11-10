import pytest
from contextlib import contextmanager

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, create_meal, clear_meals


@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    """Fixture to provide the first sample Meal object."""
    return Meal(id=1, meal="Spaghetti", price=25.0, cuisine="Italian", difficulty="MED")

@pytest.fixture
def sample_meal2():
    """Fixture to provide the second sample Meal object."""
    return Meal(id=2, meal="Sushi", price=30.0, cuisine="Japanese", difficulty="HIGH")

@pytest.fixture
def sample_meal3():
    """Fixture to provide the second sample Meal object."""
    return Meal(id=3, meal="Hamburger", price=10.0, cuisine="American", difficulty="LOW")

# Mocking the database connection for tests
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

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")



##################################################
# Battle Preparation Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Spaghetti"

def test_prep_combatant_over_two(battle_model, sample_meal1, sample_meal2, sample_meal3):
    """Test error when trying to add the third combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)

##################################################
# Battle Execution Test Cases
##################################################

def test_battle_not_enough_combatants(battle_model):
    """Test error when starting a battle with combatants fewer than 2 (No combatants for this test)."""
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_battle(battle_model, sample_meal1, sample_meal2, mock_cursor):
    # Simulating that both Meal exists and are not deleted
    mock_cursor.fetchone.side_effect = [
            [False],
            [False]
    ]
    # Add the two meals to database.
    create_meal(sample_meal1.meal, sample_meal1.cuisine, sample_meal1.price, sample_meal1.difficulty)
    create_meal(sample_meal2.meal, sample_meal2.cuisine, sample_meal2.price, sample_meal2.difficulty)
    
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    winner = battle_model.battle()

    # Winner must be one of the meal.
    assert winner == sample_meal1.meal or winner == sample_meal2.meal
    # Check if loser is removed from combatant list
    assert len(battle_model.combatants) == 1

##################################################
# Battle Score Calculation Test Cases
##################################################

def test_get_battle_score_low(battle_model, sample_meal3):
    """Test calculating battle score for a meal with LOW difficulty."""
    score = battle_model.get_battle_score(sample_meal3)
    expect = (sample_meal3.price * len("American")) - 3  # Difficulty "LOW" has modifier val of 3
    assert score == expect

def test_get_battle_score_med(battle_model, sample_meal1):
    """Test calculating battle score for a meal with MED difficulty."""
    score = battle_model.get_battle_score(sample_meal1)
    expect= (sample_meal1.price * len("Italian")) - 2  # Difficulty "MED" has modifier val of 2
    assert score == expect

def test_get_battle_score_high(battle_model, sample_meal2):
    """Test calculating battle score for a meal with HIGH difficulty."""
    score = battle_model.get_battle_score(sample_meal2)
    expect = (sample_meal2.price * len("Japanese")) - 1  # Difficulty "HIGH" has modifier val of 1
    assert score == expect

##################################################
# Combatant Retrieve/Remove Management Test Cases
##################################################

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test of getting the list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Spaghetti"
    assert combatants[1].meal == "Sushi"

def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing combatants and if an empty list is generated."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    battle_model.clear_combatants()
    assert battle_model.get_combatants() == []