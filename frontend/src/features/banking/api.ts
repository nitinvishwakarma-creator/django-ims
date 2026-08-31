import {
  apiRequest,
} from "@/lib/api/client";

import type {
  BankAccountData,
  BankAccountDetail,
  BankAccountListData,
  BankAccountListParameters,
  BankTransactionData,
  BankTransactionDetail,
  BankTransactionListData,
  BankTransactionListParameters,
  BankTransferData,
  BankTransferDetail,
  BankTransferListData,
  BankTransferListParameters,
  CreateBankAccountInput,
  CreateBankTransactionInput,
  CreateBankTransferInput,
  UpdateBankAccountInput,
} from "@/features/banking/types";

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

export async function listBankAccounts(
  parameters:
    BankAccountListParameters = {},
): Promise<BankAccountListData> {
  const response =
    await apiRequest<
      BankAccountListData
    >(
      (
        "/bank-accounts/"
        +
        buildQuery({
          page:
            parameters.page,
          page_size:
            parameters.page_size,
          account_type:
            parameters.account_type,
          currency:
            parameters.currency,
          is_active:
            parameters.is_active,
          search:
            parameters.search,
          sort:
            parameters.sort,
        })
      ),
    );

  return response.data;
}

export async function getBankAccount(
  bankAccountId: string,
): Promise<BankAccountDetail> {
  const response =
    await apiRequest<
      BankAccountData
    >(
      (
        "/bank-accounts/"
        +
        `${bankAccountId}/`
      ),
    );

  return response
    .data
    .bank_account;
}

export async function createBankAccount(
  input: CreateBankAccountInput,
): Promise<BankAccountDetail> {
  const response =
    await apiRequest<
      BankAccountData
    >(
      "/bank-accounts/",
      {
        method: "POST",
        body: input,
      },
    );

  return response
    .data
    .bank_account;
}

export async function updateBankAccount(
  bankAccountId: string,
  input: UpdateBankAccountInput,
): Promise<BankAccountDetail> {
  const response =
    await apiRequest<
      BankAccountData
    >(
      (
        "/bank-accounts/"
        +
        `${bankAccountId}/`
      ),
      {
        method: "PATCH",
        body: input,
      },
    );

  return response
    .data
    .bank_account;
}

export async function deactivateBankAccount(
  bankAccountId: string,
): Promise<BankAccountDetail> {
  const response =
    await apiRequest<
      BankAccountData
    >(
      (
        "/bank-accounts/"
        +
        `${bankAccountId}/deactivate/`
      ),
      {
        method: "POST",
      },
    );

  return response
    .data
    .bank_account;
}

export async function listBankTransactions(
  parameters:
    BankTransactionListParameters = {},
): Promise<BankTransactionListData> {
  const response =
    await apiRequest<
      BankTransactionListData
    >(
      (
        "/bank-transactions/"
        +
        buildQuery({
          page:
            parameters.page,
          page_size:
            parameters.page_size,
          bank_account_id:
            parameters.bank_account_id,
          transaction_type:
            parameters.transaction_type,
          reconciliation_status:
            parameters
              .reconciliation_status,
          search:
            parameters.search,
          sort:
            parameters.sort,
        })
      ),
    );

  return response.data;
}

export async function getBankTransaction(
  transactionId: string,
): Promise<BankTransactionDetail> {
  const response =
    await apiRequest<
      BankTransactionData
    >(
      (
        "/bank-transactions/"
        +
        `${transactionId}/`
      ),
    );

  return response
    .data
    .bank_transaction;
}

export async function createBankTransaction(
  input: CreateBankTransactionInput,
): Promise<BankTransactionDetail> {
  const response =
    await apiRequest<
      BankTransactionData
    >(
      "/bank-transactions/",
      {
        method: "POST",
        body: input,
      },
    );

  return response
    .data
    .bank_transaction;
}

export async function reconcileBankTransaction(
  transactionId: string,
): Promise<BankTransactionDetail> {
  const response =
    await apiRequest<
      BankTransactionData
    >(
      (
        "/bank-transactions/"
        +
        `${transactionId}/reconcile/`
      ),
      {
        method: "POST",
      },
    );

  return response
    .data
    .bank_transaction;
}

export async function listBankTransfers(
  parameters:
    BankTransferListParameters = {},
): Promise<BankTransferListData> {
  const response =
    await apiRequest<
      BankTransferListData
    >(
      (
        "/bank-transfers/"
        +
        buildQuery({
          page:
            parameters.page,
          page_size:
            parameters.page_size,
          source_account_id:
            parameters
              .source_account_id,
          destination_account_id:
            parameters
              .destination_account_id,
          status:
            parameters.status,
          search:
            parameters.search,
          sort:
            parameters.sort,
        })
      ),
    );

  return response.data;
}

export async function getBankTransfer(
  transferId: string,
): Promise<BankTransferDetail> {
  const response =
    await apiRequest<
      BankTransferData
    >(
      (
        "/bank-transfers/"
        +
        `${transferId}/`
      ),
    );

  return response
    .data
    .bank_transfer;
}

export async function createBankTransfer(
  input: CreateBankTransferInput,
): Promise<BankTransferDetail> {
  const response =
    await apiRequest<
      BankTransferData
    >(
      "/bank-transfers/",
      {
        method: "POST",
        body: input,
      },
    );

  return response
    .data
    .bank_transfer;
}

export async function postBankTransfer(
  transferId: string,
): Promise<BankTransferDetail> {
  const response =
    await apiRequest<
      BankTransferData
    >(
      (
        "/bank-transfers/"
        +
        `${transferId}/post/`
      ),
      {
        method: "POST",
      },
    );

  return response
    .data
    .bank_transfer;
}

export async function cancelBankTransfer(
  transferId: string,
): Promise<BankTransferDetail> {
  const response =
    await apiRequest<
      BankTransferData
    >(
      (
        "/bank-transfers/"
        +
        `${transferId}/cancel/`
      ),
      {
        method: "POST",
      },
    );

  return response
    .data
    .bank_transfer;
}