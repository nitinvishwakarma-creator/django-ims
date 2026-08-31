from django.urls import (
    path,
)

from apps.finance.api.v1 import (
    accounting_report_views,
    bank_account_views,
    bank_transaction_views,
    bank_transfer_views,
    chart_of_account_views,
    journal_entry_views,
)


app_name = "finance_api_v1"


urlpatterns = [
    path(
        "bank-accounts/",
        (
            bank_account_views
            .bank_account_collection_api
        ),
        name="bank_account_collection",
    ),

    path(
        (
            "bank-accounts/"
            "<str:bank_account_id>/"
            "deactivate/"
        ),
        (
            bank_account_views
            .bank_account_deactivate_api
        ),
        name="bank_account_deactivate",
    ),

    path(
        (
            "bank-accounts/"
            "<str:bank_account_id>/"
        ),
        (
            bank_account_views
            .bank_account_detail_api
        ),
        name="bank_account_detail",
    ),
    path(
        "bank-transactions/",
        (
            bank_transaction_views
            .bank_transaction_collection_api
        ),
        name="bank_transaction_collection",
    ),

    path(
        (
            "bank-transactions/"
            "<str:transaction_id>/reconcile/"
        ),
        (
            bank_transaction_views
            .bank_transaction_reconcile_api
        ),
        name="bank_transaction_reconcile",
    ),

    path(
        (
            "bank-transactions/"
            "<str:transaction_id>/"
        ),
        (
            bank_transaction_views
            .bank_transaction_detail_api
        ),
        name="bank_transaction_detail",
    ),
    path(
        "bank-transfers/",
        (
            bank_transfer_views
            .bank_transfer_collection_api
        ),
        name="bank_transfer_collection",
    ),

    path(
        (
            "bank-transfers/"
            "<str:transfer_id>/post/"
        ),
        (
            bank_transfer_views
            .bank_transfer_post_api
        ),
        name="bank_transfer_post",
    ),

    path(
        (
            "bank-transfers/"
            "<str:transfer_id>/cancel/"
        ),
        (
            bank_transfer_views
            .bank_transfer_cancel_api
        ),
        name="bank_transfer_cancel",
    ),

    path(
        (
            "bank-transfers/"
            "<str:transfer_id>/"
        ),
        (
            bank_transfer_views
            .bank_transfer_detail_api
        ),
        name="bank_transfer_detail",
    ),
    path(
        "chart-of-accounts/",
        (
            chart_of_account_views
            .chart_of_account_collection_api
        ),
        name=(
            "chart_of_account_collection"
        ),
    ),

    path(
        (
            "chart-of-accounts/"
            "<str:account_id>/deactivate/"
        ),
        (
            chart_of_account_views
            .chart_of_account_deactivate_api
        ),
        name=(
            "chart_of_account_deactivate"
        ),
    ),

    path(
        (
            "chart-of-accounts/"
            "<str:account_id>/"
        ),
        (
            chart_of_account_views
            .chart_of_account_detail_api
        ),
        name="chart_of_account_detail",
    ),

    path(
        "journal-entries/",
        (
            journal_entry_views
            .journal_entry_collection_api
        ),
        name="journal_entry_collection",
    ),

    path(
        (
            "journal-entries/"
            "<str:journal_id>/post/"
        ),
        (
            journal_entry_views
            .journal_entry_post_api
        ),
        name="journal_entry_post",
    ),

    path(
        (
            "journal-entries/"
            "<str:journal_id>/reverse/"
        ),
        (
            journal_entry_views
            .journal_entry_reverse_api
        ),
        name="journal_entry_reverse",
    ),

    path(
        (
            "journal-entries/"
            "<str:journal_id>/"
        ),
        (
            journal_entry_views
            .journal_entry_detail_api
        ),
        name="journal_entry_detail",
    ),

    path(
        (
            "general-ledger/"
            "<str:account_id>/"
        ),
        (
            accounting_report_views
            .general_ledger_api
        ),
        name="general_ledger",
    ),

    path(
        "trial-balance/",
        (
            accounting_report_views
            .trial_balance_api
        ),
        name="trial_balance",
    ),
]