from enum import Enum


class Industry(str, Enum):
    clothing_and_accessories = "clothing_and_accessories"
    hardware_and_automotive = "hardware_and_automotive"
    pet_supplies = "pet_supplies"
    health_and_beauty = "health_and_beauty"
    home_and_garden = "home_and_garden"
    toys_and_games = "toys_and_games"
    art_and_entertainment = "art_and_entertainment"
    food_and_drink = "food_and_drink"
    sports_and_recreation = "sports_and_recreation"
    electronics = "electronics"
    business_equipment_and_supplies = "business_equipment_and_supplies"
    unknown = "unknown"
