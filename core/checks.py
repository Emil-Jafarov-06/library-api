from datetime import date

from core import fines

STUDENT_LIMIT = 3
STAFF_LIMIT = 5
MAX_RENEWALS = 1


def amount_owed(loan):
    if not loan.returned:
        return fines.fine_for(loan.due_date)
    return 0 if loan.fine_paid else loan.fine


def total_owed(loans):
    return sum(amount_owed(loan) for loan in loans)


def owes_money(loans):
    return total_owed(loans) > 0


def count_open_loans(loans):
    return sum(1 for loan in loans if not loan.returned)


def has_open_loans(loans):
    return count_open_loans(loans) > 0


def loan_limit(member):
    return STAFF_LIMIT if member.type == "staff" else STUDENT_LIMIT


def reached_loan_limit(member, loans):
    return count_open_loans(loans) >= loan_limit(member)


def is_overdue(loan):
    return not loan.returned and fines.days_late(loan.due_date) > 0


def is_past_due_date(loan):
    return date.fromisoformat(loan.due_date) < date.today()


def was_renewed(loan):
    return loan.renewals >= MAX_RENEWALS


def has_fine_to_pay(loan):
    return loan.fine > 0 and not loan.fine_paid
