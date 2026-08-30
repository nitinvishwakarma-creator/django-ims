import {
  apiRequest,
} from "@/lib/api/client";

import type {
  ChartOfAccountData,
  ChartOfAccountDetail,
  ChartOfAccountListData,
  ChartOfAccountListParameters,
  CreateChartOfAccountInput,
  CreateJournalEntryInput,
  GeneralLedger,
  GeneralLedgerData,
  GeneralLedgerParameters,
  JournalEntryData,
  JournalEntryDetail,
  JournalEntryListData,
  JournalEntryListParameters,
  ReverseJournalEntryData,
  ReverseJournalEntryInput,
  TrialBalance,
  TrialBalanceData,
  TrialBalanceParameters,
  UpdateChartOfAccountInput,
  UpdateJournalEntryInput,
} from "@/features/accounting/types";

type QueryValue =
  | string
  | number
  | boolean
  | undefined;

function buildQuery(
  parameters: Record<
    string,
    QueryValue
  >,
): string {
  const searchParameters =
    new URLSearchParams();

  for (
    const [
      key,
      value,
    ]
    of Object.entries(
      parameters,
    )
  ) {
    if (
      value === undefined
      ||
      value === ""
    ) {
      continue;
    }

    searchParameters.set(
      key,
      String(
        value,
      ),
    );
  }

  const query =
    searchParameters.toString();

  return query
    ? `?${query}`
    : "";
}

export async function listChartOfAccounts(
  parameters:
    ChartOfAccountListParameters = {},
): Promise<ChartOfAccountListData> {
  const response =
    await apiRequest<
      ChartOfAccountListData
    >(
      (
        "/chart-of-accounts/"
        +
        buildQuery({
          page:
            parameters.page,
          page_size:
            parameters.page_size,
          account_type:
            parameters.account_type,
          account_subtype:
            parameters.account_subtype,
          normal_balance:
            parameters.normal_balance,
          is_system_account:
            parameters
              .is_system_account,
          is_active:
            parameters.is_active,
          allow_manual_posting:
            parameters
              .allow_manual_posting,
          search:
            parameters.search,
          sort:
            parameters.sort,
        })
      ),
    );

  return response.data;
}

export async function getChartOfAccount(
  accountId: string,
): Promise<ChartOfAccountDetail> {
  const response =
    await apiRequest<
      ChartOfAccountData
    >(
      (
        "/chart-of-accounts/"
        +
        `${accountId}/`
      ),
    );

  return response.data.account;
}

export async function createChartOfAccount(
  input: CreateChartOfAccountInput,
): Promise<ChartOfAccountDetail> {
  const response =
    await apiRequest<
      ChartOfAccountData
    >(
      "/chart-of-accounts/",
      {
        method: "POST",
        body: input,
      },
    );

  return response.data.account;
}

export async function updateChartOfAccount(
  accountId: string,
  input: UpdateChartOfAccountInput,
): Promise<ChartOfAccountDetail> {
  const response =
    await apiRequest<
      ChartOfAccountData
    >(
      (
        "/chart-of-accounts/"
        +
        `${accountId}/`
      ),
      {
        method: "PATCH",
        body: input,
      },
    );

  return response.data.account;
}

export async function deactivateChartOfAccount(
  accountId: string,
): Promise<ChartOfAccountDetail> {
  const response =
    await apiRequest<
      ChartOfAccountData
    >(
      (
        "/chart-of-accounts/"
        +
        `${accountId}/deactivate/`
      ),
      {
        method: "POST",
      },
    );

  return response.data.account;
}

export async function listJournalEntries(
  parameters:
    JournalEntryListParameters = {},
): Promise<JournalEntryListData> {
  const response =
    await apiRequest<
      JournalEntryListData
    >(
      (
        "/journal-entries/"
        +
        buildQuery({
          page:
            parameters.page,
          page_size:
            parameters.page_size,
          status:
            parameters.status,
          source_type:
            parameters.source_type,
          source_id:
            parameters.source_id,
          search:
            parameters.search,
          sort:
            parameters.sort,
        })
      ),
    );

  return response.data;
}

export async function getJournalEntry(
  journalId: string,
): Promise<JournalEntryDetail> {
  const response =
    await apiRequest<
      JournalEntryData
    >(
      (
        "/journal-entries/"
        +
        `${journalId}/`
      ),
    );

  return response
    .data
    .journal_entry;
}

export async function createJournalEntry(
  input: CreateJournalEntryInput,
): Promise<JournalEntryDetail> {
  const response =
    await apiRequest<
      JournalEntryData
    >(
      "/journal-entries/",
      {
        method: "POST",
        body: input,
      },
    );

  return response
    .data
    .journal_entry;
}

export async function updateJournalEntry(
  journalId: string,
  input: UpdateJournalEntryInput,
): Promise<JournalEntryDetail> {
  const response =
    await apiRequest<
      JournalEntryData
    >(
      (
        "/journal-entries/"
        +
        `${journalId}/`
      ),
      {
        method: "PATCH",
        body: input,
      },
    );

  return response
    .data
    .journal_entry;
}

export async function postJournalEntry(
  journalId: string,
): Promise<JournalEntryDetail> {
  const response =
    await apiRequest<
      JournalEntryData
    >(
      (
        "/journal-entries/"
        +
        `${journalId}/post/`
      ),
      {
        method: "POST",
      },
    );

  return response
    .data
    .journal_entry;
}

export async function reverseJournalEntry(
  journalId: string,
  input: ReverseJournalEntryInput,
): Promise<ReverseJournalEntryData> {
  const response =
    await apiRequest<
      ReverseJournalEntryData
    >(
      (
        "/journal-entries/"
        +
        `${journalId}/reverse/`
      ),
      {
        method: "POST",
        body: input,
      },
    );

  return response.data;
}

export async function getGeneralLedger(
  parameters:
    GeneralLedgerParameters,
): Promise<GeneralLedger> {
  const response =
    await apiRequest<
      GeneralLedgerData
    >(
      (
        "/general-ledger/"
        +
        `${parameters.account_id}/`
        +
        buildQuery({
          start_date:
            parameters.start_date,
          end_date:
            parameters.end_date,
        })
      ),
    );

  return response
    .data
    .general_ledger;
}

export async function getTrialBalance(
  parameters:
    TrialBalanceParameters = {},
): Promise<TrialBalance> {
  const response =
    await apiRequest<
      TrialBalanceData
    >(
      (
        "/trial-balance/"
        +
        buildQuery({
          as_of_date:
            parameters.as_of_date,
          include_zero_balances:
            parameters
              .include_zero_balances,
        })
      ),
    );

  return response
    .data
    .trial_balance;
}