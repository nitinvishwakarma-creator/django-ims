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