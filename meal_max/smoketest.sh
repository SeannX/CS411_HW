#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##################################################
# Meal Management Smoketests
##################################################


##################################################
# Battle Management Smoketests
##################################################

# start battle and check if success
start_battle() {
  echo "Initiating battle test..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle test passed: $response"
  else
    echo "Battle test failed: $response"
    exit 1
  fi
}

# Clear combatants
clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared."
  else
    echo "Failed to clear combatants: $response"
    exit 1
  fi
}

# Function to get the combatants
get_combatants() {
  echo "Getting the combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully: $response"
  else
    echo "Failed to get combatants: $response"
    exit 1
  fi
}

# Prepare a combatant
prep_combatant() {
  meal=$1
  echo "Preparing combatant meal: $meal..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatant prepared successfully: $response"
  else
    echo "Failed to prepare combatant: $response"
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Function to get the song leaderboard sorted by wins
get_meal_leaderboard() {
  echo "Getting meal leaderboard sorted by wins..."

  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully (sorted by wins)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard (sorted by wins)."
    exit 1
  fi
}

##################################################
# Running Smoketests
##################################################

echo "Running smoketests..."

# Health checks
check_health
check_db

# battle
clear_combatants

prep_combatant "Spaghetti"
prep_combatant "Sushi"
get_combatants
clear_combatants

prep_combatant "Spaghetti"
prep_combatant "Sushi"
get_combatants

start_battle
get_combatants

clear_combatants

get_meal_leaderboard

echo "All tests passed successfully!"