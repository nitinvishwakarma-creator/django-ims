from apps.core.services.api_serialization_service import (
    APISerializationService,
)


class ChartOfAccountAPISerializer:

    @staticmethod
    def _serialize_created_by(
        user,
    ):
        if not user:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    user.id
                )
            ),
            "email":
                user.email,
            "first_name":
                user.first_name,
            "last_name":
                user.last_name,
        }

    @staticmethod
    def serialize_summary(
        account,
    ):
        if not account:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    account.id
                )
            ),
            "account_code":
                account.account_code,
            "account_name":
                account.account_name,
            "account_type":
                account.account_type,
            "account_subtype":
                (
                    account.account_subtype
                    or
                    None
                ),
            "normal_balance":
                account.normal_balance,
            "system_key":
                (
                    account.system_key
                    or
                    None
                ),
            "is_system_account":
                bool(
                    account.is_system_account
                ),
            "is_active":
                bool(
                    account.is_active
                ),
            "allow_manual_posting":
                bool(
                    account.allow_manual_posting
                ),
        }

    @staticmethod
    def serialize_detail(
        account,
    ):
        if not account:
            return None

        summary = (
            ChartOfAccountAPISerializer
            .serialize_summary(
                account
            )
        )

        return {
            **summary,
            "description":
                (
                    account.description
                    or
                    None
                ),
            "created_by": (
                ChartOfAccountAPISerializer
                ._serialize_created_by(
                    account.created_by
                )
            ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    account.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    account.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_many(
        accounts,
    ):
        return [
            (
                ChartOfAccountAPISerializer
                .serialize_summary(
                    account
                )
            )
            for account
            in accounts
        ]


class JournalEntryAPISerializer:

    @staticmethod
    def _serialize_created_by(
        user,
    ):
        if not user:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    user.id
                )
            ),
            "email":
                user.email,
            "first_name":
                user.first_name,
            "last_name":
                user.last_name,
        }

    @staticmethod
    def serialize_line(
        line,
    ):
        if not line:
            return None

        return {
            "account": (
                ChartOfAccountAPISerializer
                .serialize_summary(
                    line.account
                )
            ),
            "description":
                (
                    line.description
                    or
                    None
                ),
            "debit":
                str(
                    line.debit
                ),
            "credit":
                str(
                    line.credit
                ),
        }

    @staticmethod
    def serialize_summary(
        journal,
    ):
        if not journal:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    journal.id
                )
            ),
            "journal_number":
                journal.journal_number,
            "journal_date": (
                APISerializationService
                .serialize_datetime(
                    journal.journal_date
                )
            ),
            "description":
                (
                    journal.description
                    or
                    None
                ),
            "source_type":
                journal.source_type,
            "source_id":
                (
                    journal.source_id
                    or
                    None
                ),
            "status":
                journal.status,
            "total_debit":
                str(
                    journal.total_debit
                ),
            "total_credit":
                str(
                    journal.total_credit
                ),
            "line_count":
                len(
                    journal.lines
                    or
                    []
                ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    journal.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    journal.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_detail(
        journal,
    ):
        if not journal:
            return None

        summary = (
            JournalEntryAPISerializer
            .serialize_summary(
                journal
            )
        )

        return {
            **summary,
            "lines": [
                (
                    JournalEntryAPISerializer
                    .serialize_line(
                        line
                    )
                )
                for line
                in (
                    journal.lines
                    or
                    []
                )
            ],
            "posted_at": (
                APISerializationService
                .serialize_datetime(
                    journal.posted_at
                )
            ),
            "reversed_at": (
                APISerializationService
                .serialize_datetime(
                    journal.reversed_at
                )
            ),
            "reversal_of_id": (
                APISerializationService
                .serialize_identifier(
                    journal.reversal_of.id
                )
                if journal.reversal_of
                else None
            ),
            "reversed_by_id": (
                APISerializationService
                .serialize_identifier(
                    journal.reversed_by.id
                )
                if journal.reversed_by
                else None
            ),
            "created_by": (
                JournalEntryAPISerializer
                ._serialize_created_by(
                    journal.created_by
                )
            ),
        }

    @staticmethod
    def serialize_many(
        journals,
    ):
        return [
            (
                JournalEntryAPISerializer
                .serialize_summary(
                    journal
                )
            )
            for journal
            in journals
        ]


class GeneralLedgerAPISerializer:

    @staticmethod
    def serialize(
        result,
    ):
        return {
            "account": (
                ChartOfAccountAPISerializer
                .serialize_detail(
                    result["account"]
                )
            ),
            "start_date": (
                APISerializationService
                .serialize_datetime(
                    result["start_date"]
                )
            ),
            "end_date": (
                APISerializationService
                .serialize_datetime(
                    result["end_date"]
                )
            ),
            "opening_balance":
                str(
                    result[
                        "opening_balance"
                    ]
                ),
            "entries": [
                {
                    "journal_number":
                        entry[
                            "journal_number"
                        ],
                    "journal_date": (
                        APISerializationService
                        .serialize_datetime(
                            entry[
                                "journal_date"
                            ]
                        )
                    ),
                    "description":
                        (
                            entry[
                                "description"
                            ]
                            or
                            None
                        ),
                    "source_type":
                        entry[
                            "source_type"
                        ],
                    "source_id":
                        (
                            entry[
                                "source_id"
                            ]
                            or
                            None
                        ),
                    "debit":
                        str(
                            entry[
                                "debit"
                            ]
                        ),
                    "credit":
                        str(
                            entry[
                                "credit"
                            ]
                        ),
                    "running_balance":
                        str(
                            entry[
                                "running_balance"
                            ]
                        ),
                }
                for entry
                in result[
                    "entries"
                ]
            ],
            "total_debit":
                str(
                    result[
                        "total_debit"
                    ]
                ),
            "total_credit":
                str(
                    result[
                        "total_credit"
                    ]
                ),
            "closing_balance":
                str(
                    result[
                        "closing_balance"
                    ]
                ),
        }


class TrialBalanceAPISerializer:

    @staticmethod
    def serialize(
        result,
    ):
        return {
            "as_of_date": (
                APISerializationService
                .serialize_datetime(
                    result["as_of_date"]
                )
            ),
            "rows": [
                {
                    "account": (
                        ChartOfAccountAPISerializer
                        .serialize_summary(
                            row["account"]
                        )
                    ),
                    "total_debit":
                        str(
                            row[
                                "total_debit"
                            ]
                        ),
                    "total_credit":
                        str(
                            row[
                                "total_credit"
                            ]
                        ),
                    "debit_balance":
                        str(
                            row[
                                "debit_balance"
                            ]
                        ),
                    "credit_balance":
                        str(
                            row[
                                "credit_balance"
                            ]
                        ),
                }
                for row
                in result[
                    "rows"
                ]
            ],
            "total_debit_balance":
                str(
                    result[
                        "total_debit_balance"
                    ]
                ),
            "total_credit_balance":
                str(
                    result[
                        "total_credit_balance"
                    ]
                ),
            "difference":
                str(
                    result[
                        "difference"
                    ]
                ),
            "is_balanced":
                bool(
                    result[
                        "is_balanced"
                    ]
                ),
        }

class BankAccountAPISerializer:

    @staticmethod
    def _serialize_created_by(
        user,
    ):
        if not user:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    user.id
                )
            ),
            "email":
                user.email,
            "first_name":
                user.first_name,
            "last_name":
                user.last_name,
        }

    @staticmethod
    def serialize_summary(
        bank_account,
    ):
        if not bank_account:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    bank_account.id
                )
            ),
            "account_name":
                bank_account.account_name,
            "account_type":
                bank_account.account_type,
            "bank_name":
                (
                    bank_account.bank_name
                    or
                    None
                ),
            "account_number":
                (
                    bank_account.account_number
                    or
                    None
                ),
            "ifsc_code":
                (
                    bank_account.ifsc_code
                    or
                    None
                ),
            "currency":
                bank_account.currency,
            "opening_balance":
                str(
                    bank_account.opening_balance
                ),
            "current_balance":
                str(
                    bank_account.current_balance
                ),
            "is_active":
                bool(
                    bank_account.is_active
                ),
        }

    @staticmethod
    def serialize_detail(
        bank_account,
    ):
        if not bank_account:
            return None

        summary = (
            BankAccountAPISerializer
            .serialize_summary(
                bank_account
            )
        )

        return {
            **summary,
            "created_by": (
                BankAccountAPISerializer
                ._serialize_created_by(
                    bank_account.created_by
                )
            ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    bank_account.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    bank_account.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_many(
        bank_accounts,
    ):
        return [
            (
                BankAccountAPISerializer
                .serialize_summary(
                    bank_account
                )
            )
            for bank_account
            in bank_accounts
        ]

class BankTransactionAPISerializer:

    @staticmethod
    def _serialize_created_by(
        user,
    ):
        if not user:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    user.id
                )
            ),
            "email":
                user.email,
            "first_name":
                user.first_name,
            "last_name":
                user.last_name,
        }

    @staticmethod
    def serialize_summary(
        transaction,
    ):
        if not transaction:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    transaction.id
                )
            ),
            "bank_account": (
                BankAccountAPISerializer
                .serialize_summary(
                    transaction.bank_account
                )
            ),
            "transaction_number":
                transaction.transaction_number,
            "transaction_type":
                transaction.transaction_type,
            "transaction_date": (
                APISerializationService
                .serialize_datetime(
                    transaction.transaction_date
                )
            ),
            "amount":
                str(
                    transaction.amount
                ),
            "balance_before":
                str(
                    transaction.balance_before
                ),
            "balance_after":
                str(
                    transaction.balance_after
                ),
            "external_reference":
                (
                    transaction.external_reference
                    or
                    None
                ),
            "description":
                (
                    transaction.description
                    or
                    None
                ),
            "reconciliation_status":
                transaction.reconciliation_status,
            "reconciled_at": (
                APISerializationService
                .serialize_datetime(
                    transaction.reconciled_at
                )
            ),
        }

    @staticmethod
    def serialize_detail(
        transaction,
    ):
        if not transaction:
            return None

        summary = (
            BankTransactionAPISerializer
            .serialize_summary(
                transaction
            )
        )

        return {
            **summary,
            "reference_type":
                (
                    transaction.reference_type
                    or
                    None
                ),
            "reference_id":
                (
                    transaction.reference_id
                    or
                    None
                ),
            "created_by": (
                BankTransactionAPISerializer
                ._serialize_created_by(
                    transaction.created_by
                )
            ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    transaction.created_at
                )
            ),
        }

    @staticmethod
    def serialize_many(
        transactions,
    ):
        return [
            (
                BankTransactionAPISerializer
                .serialize_summary(
                    transaction
                )
            )
            for transaction
            in transactions
        ]

class BankTransferAPISerializer:

    @staticmethod
    def _serialize_created_by(
        user,
    ):
        if not user:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    user.id
                )
            ),
            "email":
                user.email,
            "first_name":
                user.first_name,
            "last_name":
                user.last_name,
        }

    @staticmethod
    def serialize_summary(
        transfer,
    ):
        if not transfer:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    transfer.id
                )
            ),
            "transfer_number":
                transfer.transfer_number,
            "source_account": (
                BankAccountAPISerializer
                .serialize_summary(
                    transfer.source_account
                )
            ),
            "destination_account": (
                BankAccountAPISerializer
                .serialize_summary(
                    transfer.destination_account
                )
            ),
            "transfer_date": (
                APISerializationService
                .serialize_datetime(
                    transfer.transfer_date
                )
            ),
            "amount":
                str(
                    transfer.amount
                ),
            "status":
                transfer.status,
            "reference":
                (
                    transfer.reference
                    or
                    None
                ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    transfer.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    transfer.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_detail(
        transfer,
    ):
        if not transfer:
            return None

        summary = (
            BankTransferAPISerializer
            .serialize_summary(
                transfer
            )
        )

        return {
            **summary,
            "notes":
                (
                    transfer.notes
                    or
                    None
                ),
            "posted_at": (
                APISerializationService
                .serialize_datetime(
                    transfer.posted_at
                )
            ),
            "cancelled_at": (
                APISerializationService
                .serialize_datetime(
                    transfer.cancelled_at
                )
            ),
            "created_by": (
                BankTransferAPISerializer
                ._serialize_created_by(
                    transfer.created_by
                )
            ),
        }

    @staticmethod
    def serialize_many(
        transfers,
    ):
        return [
            (
                BankTransferAPISerializer
                .serialize_summary(
                    transfer
                )
            )
            for transfer
            in transfers
        ]

class BankStatementAPISerializer:

    @staticmethod
    def serialize_line(
        line,
    ):
        if not line:
            return None

        return {
            "line_number":
                line.line_number,
            "transaction_date": (
                APISerializationService
                .serialize_datetime(
                    line.transaction_date
                )
            ),
            "value_date": (
                APISerializationService
                .serialize_datetime(
                    line.value_date
                )
            ),
            "description":
                (
                    line.description
                    or
                    None
                ),
            "external_reference":
                (
                    line.external_reference
                    or
                    None
                ),
            "debit_amount":
                str(
                    line.debit_amount
                ),
            "credit_amount":
                str(
                    line.credit_amount
                ),
            "running_balance": (
                str(
                    line.running_balance
                )
                if (
                    line.running_balance
                    is not None
                )
                else None
            ),
            "match_status":
                line.match_status,
            "matched_transaction": (
                BankTransactionAPISerializer
                .serialize_summary(
                    line.matched_transaction
                )
                if line.matched_transaction
                else None
            ),
            "matched_at": (
                APISerializationService
                .serialize_datetime(
                    line.matched_at
                )
            ),
        }

    @staticmethod
    def serialize_summary(
        statement,
    ):
        if not statement:
            return None

        lines = (
            statement.lines
            or
            []
        )

        matched_count = sum(
            1
            for line in lines
            if line.match_status == "MATCHED"
        )

        ignored_count = sum(
            1
            for line in lines
            if line.match_status == "IGNORED"
        )

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    statement.id
                )
            ),
            "statement_number":
                statement.statement_number,
            "bank_account": (
                BankAccountAPISerializer
                .serialize_summary(
                    statement.bank_account
                )
            ),
            "statement_start_date": (
                APISerializationService
                .serialize_datetime(
                    statement
                    .statement_start_date
                )
            ),
            "statement_end_date": (
                APISerializationService
                .serialize_datetime(
                    statement
                    .statement_end_date
                )
            ),
            "opening_balance":
                str(
                    statement.opening_balance
                ),
            "closing_balance":
                str(
                    statement.closing_balance
                ),
            "source_filename":
                (
                    statement.source_filename
                    or
                    None
                ),
            "source_type":
                statement.source_type,
            "status":
                statement.status,
            "line_count":
                len(
                    lines
                ),
            "matched_count":
                matched_count,
            "ignored_count":
                ignored_count,
            "unmatched_count": (
                len(
                    lines
                )
                -
                matched_count
                -
                ignored_count
            ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    statement.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    statement.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_detail(
        statement,
    ):
        if not statement:
            return None

        summary = (
            BankStatementAPISerializer
            .serialize_summary(
                statement
            )
        )

        return {
            **summary,
            "lines": [
                (
                    BankStatementAPISerializer
                    .serialize_line(
                        line
                    )
                )
                for line
                in (
                    statement.lines
                    or
                    []
                )
            ],
            "reconciled_at": (
                APISerializationService
                .serialize_datetime(
                    statement.reconciled_at
                )
            ),
            "cancelled_at": (
                APISerializationService
                .serialize_datetime(
                    statement.cancelled_at
                )
            ),
            "created_by": (
                BankAccountAPISerializer
                ._serialize_created_by(
                    statement.created_by
                )
            ),
        }

    @staticmethod
    def serialize_many(
        statements,
    ):
        return [
            (
                BankStatementAPISerializer
                .serialize_summary(
                    statement
                )
            )
            for statement
            in statements
        ]