import enum


class Plan(str, enum.Enum):
    Tier1 = "lebesgue_tier1"
    Tier2 = "lebesgue_tier2"
    Tier3 = "lebesgue_tier3"
    Refunded = "lebesgue_refunded"


plan_to_shop_number: dict[Plan, int] = {
    Plan.Tier1: 1,
    Plan.Tier2: 5,
    Plan.Tier3: 25,
    Plan.Refunded: 0,
}
