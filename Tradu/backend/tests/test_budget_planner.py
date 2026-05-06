from backend.app.services.budget_planner import BudgetPlanner


def test_budget_plan_2500_3_days():
    plan = BudgetPlanner().create_budget_plan(2500, 3, "relaxed")
    assert plan["days"] == 3
    assert plan["buffer_budget"] >= 250
    assert plan["budget_warning"] == "budget_normal"


def test_budget_plan_800_2_days_tight():
    plan = BudgetPlanner().create_budget_plan(800, 2, "standard")
    assert plan["budget_warning"] == "budget_tight"
    assert plan["buffer_budget"] >= 80


def test_budget_plan_5000_3_days_flexible():
    plan = BudgetPlanner().create_budget_plan(5000, 3, "standard")
    assert plan["budget_warning"] == "budget_flexible"
    assert plan["buffer_budget"] >= 500
