import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture
def create_battle_model():
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

def test_battle_winner(battle_model, sample_meal1, sample_meal2, mocker):
    """Test that a battle correctly determines a winner."""
    # Mock get_random to control randomness
    mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.1)
    
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    winner = battle_model.battle()
    # Winner will always be spaghetti when the value return by .get_random is set to 0.1
    assert winner == "Spaghetti", f"Expected 'Spaghetti', but got {winner}"
    # Check if loser is removed from combatant list
    assert len(battle_model.combatants) == 1
    # Check the status of winner (Spaghetti)
    assert winner.id == 'win'

##################################################
# Battle Score Calculation Test Cases
##################################################

def test_get_battle_score_low(battle_model, sample_meal3):
    """Test calculating battle score for a meal with 'MED' difficulty."""
    score = battle_model.get_battle_score(sample_meal3)
    expect = (sample_meal3.price * len("American")) - 3  # Difficulty "MED" has modifier 3
    assert score == expect

def test_get_battle_score_med(battle_model, sample_meal1):
    """Test calculating battle score for a meal with 'MED' difficulty."""
    score = battle_model.get_battle_score(sample_meal1)
    expect= (sample_meal1.price * len("Italian")) - 2  # Difficulty "MED" has modifier 2
    assert score == expect

def test_get_battle_score_high(battle_model, sample_meal2):
    """Test calculating battle score for a meal with 'HIGH' difficulty."""
    score = battle_model.get_battle_score(sample_meal2)
    expect = (sample_meal2.price * len("Japanese")) - 1  # Difficulty "HIGH" has modifier 1
    assert score == expect

##################################################
# Combatant Management Test Cases
##################################################

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test retrieving the list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Spaghetti"
    assert combatants[1].meal == "Sushi"

def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing combatants and if an empty list is retrieved."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    battle_model.clear_combatants()
    assert battle_model.get_combatants() == []