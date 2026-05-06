from fastapi import APIRouter

from ..schemas import TaxCalculatorRequest, TaxCalculatorResponse, TaxSavingSuggestion, TaxSavingSuggestionRequest

router = APIRouter(prefix="/tools", tags=["Financial Tools"])


def slab_tax(amount: float, slabs: list[tuple[float, float]]) -> float:
    tax = 0.0
    previous_limit = 0.0
    for limit, rate in slabs:
        if amount > previous_limit:
            taxable_slice = min(amount, limit) - previous_limit
            tax += taxable_slice * rate
        previous_limit = limit
        if amount <= limit:
            break
    return max(tax, 0.0)


def add_cess(tax: float) -> float:
    return round(tax * 1.04, 2)


@router.post("/tax-calculator", response_model=TaxCalculatorResponse)
def calculate_tax(payload: TaxCalculatorRequest):
    old_deductions = (
        min(payload.deductions_80c, 150000)
        + min(payload.medical_80d, 25000)
        + min(payload.home_loan_interest, 200000)
        + payload.other_deductions
    )
    taxable_old = max(payload.annual_income - old_deductions, 0)
    taxable_new = payload.annual_income

    old_slabs = [
        (250000, 0.00),
        (500000, 0.05),
        (1000000, 0.20),
        (float("inf"), 0.30),
    ]
    new_slabs = [
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float("inf"), 0.30),
    ]

    old_tax_before_cess = slab_tax(taxable_old, old_slabs)
    if taxable_old <= 500000:
        old_tax_before_cess = max(old_tax_before_cess - 12500, 0)

    new_tax_before_cess = slab_tax(taxable_new, new_slabs)
    if taxable_new <= 1200000:
        new_tax_before_cess = max(new_tax_before_cess - 60000, 0)

    old_tax = add_cess(old_tax_before_cess)
    new_tax = add_cess(new_tax_before_cess)
    recommended = "Old Regime" if old_tax < new_tax else "New Regime"

    return {
        "taxable_old_regime": round(taxable_old, 2),
        "taxable_new_regime": round(taxable_new, 2),
        "old_regime_tax": old_tax,
        "new_regime_tax": new_tax,
        "recommended_regime": recommended,
        "savings_difference": round(abs(old_tax - new_tax), 2),
        "note": "Basic AY 2026-27 style estimate for demo use. It ignores surcharge, marginal relief, special income rates, and case-specific exemptions.",
    }


@router.post("/tax-saving-suggestions", response_model=list[TaxSavingSuggestion])
def tax_saving_suggestions(payload: TaxSavingSuggestionRequest):
    suggestions: list[dict] = []
    remaining_80c = max(150000 - payload.invested_80c, 0)
    remaining_80d = max(25000 - payload.medical_80d, 0)
    remaining_home = max(200000 - payload.home_loan_interest, 0)

    if remaining_80c:
        suggestions.append(
            {
                "title": "Use Section 80C fully",
                "message": "Consider ELSS, PPF, EPF, life insurance premium, or principal repayment options up to the 80C limit.",
                "potential_deduction": remaining_80c,
            }
        )
    if remaining_80d:
        suggestions.append(
            {
                "title": "Review medical insurance under 80D",
                "message": "Health insurance premiums may reduce taxable income under old-regime rules.",
                "potential_deduction": remaining_80d,
            }
        )
    if remaining_home and payload.annual_income > 500000:
        suggestions.append(
            {
                "title": "Check home loan interest eligibility",
                "message": "Interest on a self-occupied housing loan can be considered under old-regime rules within limits.",
                "potential_deduction": remaining_home,
            }
        )
    if not suggestions:
        suggestions.append(
            {
                "title": "Good coverage",
                "message": "Your basic old-regime deduction inputs are already near common demo limits.",
                "potential_deduction": 0,
            }
        )
    return suggestions

