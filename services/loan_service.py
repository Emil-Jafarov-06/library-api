from datetime import date, timedelta

from repositories import book_repository
from repositories import loan_repository
from repositories import member_repository
from core import checks
from core import fines
from core import notifications
from core import validation
from core.errors import bad_request, not_found, conflict

LOAN_DAYS = 14


def list_loans(only_overdue):
    allLoans = loan_repository.list_loans()
    return [loan for loan in allLoans if checks.is_overdue(loan)] if only_overdue else allLoans


def get_loan(loan_id):
    loan = loan_repository.get_loan(loan_id)
    if loan is None:
        raise not_found("loan not found")
    return loan


def create_loan(data):
    bookId, memberId, dueDate = data.get("book_id"), data.get("member_id"), data.get("due_date")

    if not bookId or not memberId:
        raise bad_request("book_id and member_id are required")
    if dueDate and not validation.is_valid_date(dueDate):
        raise bad_request("invalid due_date")

    book = book_repository.get_book(bookId)
    if book is None:
        raise not_found("book not found")
    member = member_repository.get_member(memberId)
    if member is None:
        raise not_found("member not found")
    if not book.available:
        raise conflict("book is not available")

    memberLoans = loan_repository.list_loans_for_member(memberId)
    if checks.owes_money(memberLoans):
        raise conflict("member has unpaid fines")
    if checks.reached_loan_limit(member, memberLoans):
        raise conflict("loan limit reached")

    today = date.today()
    dueDate = dueDate or (today + timedelta(days=LOAN_DAYS)).isoformat()
    loan = loan_repository.create_loan(bookId, memberId, dueDate, today.isoformat())

    notifications.send_email(member.email, "Book checked out", "You checked out " + book.title)
    return loan


def return_book(loan_id):
    loan = get_loan(loan_id)
    if loan.returned:
        raise conflict("loan already returned")

    fine = fines.fine_for(loan.due_date)
    updatedLoan = loan_repository.mark_returned(loan_id, loan.book_id, fine)

    member = member_repository.get_member(loan.member_id)
    book = book_repository.get_book(loan.book_id)
    notifications.send_email(
        member.email, "Book returned", f"You returned {book.title}. Fine: ${fines.money(fine)}"
    )
    return updatedLoan


def renew_loan(loan_id):
    loan = get_loan(loan_id)
    if loan.returned:
        raise conflict("loan already returned")

    if checks.is_past_due_date(loan):
        raise conflict("overdue loans cannot be renewed")
    if checks.was_renewed(loan):
        raise conflict("loan was already renewed")

    updatedLoan = loan_repository.extend_loan(loan_id, (date.fromisoformat(loan.due_date) + timedelta(days=LOAN_DAYS)).isoformat())

    member = member_repository.get_member(loan.member_id)
    book = book_repository.get_book(loan.book_id)
    notifications.send_email(member.email, "Loan renewed", "You renewed " + book.title)
    return updatedLoan


def pay_fine(loan_id):
    loan = get_loan(loan_id)
    if not loan.returned:
        raise conflict("return the book before paying")
    if not checks.has_fine_to_pay(loan):
        raise conflict("no fine to pay")

    updatedLoan = loan_repository.mark_fine_paid(loan_id)

    member = member_repository.get_member(loan.member_id)
    notifications.send_email(member.email, "Fine paid", f"We received ${fines.money(loan.fine)}")
    return updatedLoan
