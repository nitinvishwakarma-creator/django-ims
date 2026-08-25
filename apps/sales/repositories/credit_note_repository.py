from apps.sales.models import CreditNote


class CreditNoteRepository:

    @staticmethod
    def create_credit_note(
        *,
        organization,
        credit_note_number,
        invoice,
        sales_return,
        customer,
        credit_note_date,
        items,
        subtotal,
        tax_amount,
        discount_amount,
        total_amount,
        reason,
        notes,
        created_by,
        status="DRAFT",
    ):
        credit_note = CreditNote(
            organization=organization,
            credit_note_number=credit_note_number,
            invoice=invoice,
            sales_return=sales_return,
            customer=customer,
            status=status,
            credit_note_date=credit_note_date,
            items=items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            applied_amount=0,
            remaining_credit=total_amount,
            reason=reason,
            notes=notes,
            created_by=created_by,
        )

        credit_note.save()

        return credit_note

    @staticmethod
    def get_by_id(
        *,
        organization,
        credit_note_id,
    ):
        return CreditNote.objects(
            organization=organization,
            id=credit_note_id,
        ).first()

    @staticmethod
    def get_by_number(
        *,
        organization,
        credit_note_number,
    ):
        return CreditNote.objects(
            organization=organization,
            credit_note_number=credit_note_number,
        ).first()

    @staticmethod
    def get_by_sales_return(
        *,
        organization,
        sales_return,
    ):
        return CreditNote.objects(
            organization=organization,
            sales_return=sales_return,
        ).first()

    @staticmethod
    def list_by_organization(
        *,
        organization,
    ):
        return CreditNote.objects(
            organization=organization,
        ).order_by(
            "-credit_note_date",
            "-created_at",
        )

    @staticmethod
    def list_by_invoice(
        *,
        organization,
        invoice,
    ):
        return CreditNote.objects(
            organization=organization,
            invoice=invoice,
        ).order_by(
            "-credit_note_date",
            "-created_at",
        )

    @staticmethod
    def list_by_customer(
        *,
        organization,
        customer,
    ):
        return CreditNote.objects(
            organization=organization,
            customer=customer,
        ).order_by(
            "-credit_note_date",
            "-created_at",
        )

    @staticmethod
    def list_by_status(
        *,
        organization,
        status,
    ):
        return CreditNote.objects(
            organization=organization,
            status=status,
        ).order_by(
            "-credit_note_date",
            "-created_at",
        )

    @staticmethod
    def update_status(
        *,
        credit_note,
        status,
        issued_at=None,
        cancelled_at=None,
    ):
        credit_note.status = status

        if issued_at is not None:
            credit_note.issued_at = issued_at

        if cancelled_at is not None:
            credit_note.cancelled_at = (
                cancelled_at
            )

        credit_note.save()

        return credit_note

    @staticmethod
    def update_application(
        *,
        credit_note,
        applied_amount,
        remaining_credit,
    ):
        credit_note.applied_amount = (
            applied_amount
        )

        credit_note.remaining_credit = (
            remaining_credit
        )

        credit_note.save()

        return credit_note