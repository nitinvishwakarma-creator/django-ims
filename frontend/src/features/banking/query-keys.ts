import type {
  BankAccountListParameters,
  BankTransactionListParameters,
  BankTransferListParameters,
} from "@/features/banking/types";

export const bankingQueryKeys = {
  all: [
    "banking",
  ] as const,

  accounts: () => [
    ...bankingQueryKeys.all,
    "accounts",
  ] as const,

  accountLists: () => [
    ...bankingQueryKeys.accounts(),
    "list",
  ] as const,

  accountList: (
    parameters:
      BankAccountListParameters,
  ) => [
    ...bankingQueryKeys
      .accountLists(),
    parameters,
  ] as const,

  accountDetails: () => [
    ...bankingQueryKeys.accounts(),
    "detail",
  ] as const,

  accountDetail: (
    bankAccountId: string,
  ) => [
    ...bankingQueryKeys
      .accountDetails(),
    bankAccountId,
  ] as const,

  transactions: () => [
    ...bankingQueryKeys.all,
    "transactions",
  ] as const,

  transactionLists: () => [
    ...bankingQueryKeys.transactions(),
    "list",
  ] as const,

  transactionList: (
    parameters:
      BankTransactionListParameters,
  ) => [
    ...bankingQueryKeys
      .transactionLists(),
    parameters,
  ] as const,

  transactionDetails: () => [
    ...bankingQueryKeys.transactions(),
    "detail",
  ] as const,

  transactionDetail: (
    transactionId: string,
  ) => [
    ...bankingQueryKeys
      .transactionDetails(),
    transactionId,
  ] as const,

  transfers: () => [
    ...bankingQueryKeys.all,
    "transfers",
  ] as const,

  transferLists: () => [
    ...bankingQueryKeys.transfers(),
    "list",
  ] as const,

  transferList: (
    parameters:
      BankTransferListParameters,
  ) => [
    ...bankingQueryKeys
      .transferLists(),
    parameters,
  ] as const,

  transferDetails: () => [
    ...bankingQueryKeys.transfers(),
    "detail",
  ] as const,

  transferDetail: (
    transferId: string,
  ) => [
    ...bankingQueryKeys
      .transferDetails(),
    transferId,
  ] as const,
};