import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  cancelBankTransfer,
  createBankAccount,
  createBankTransaction,
  createBankTransfer,
  deactivateBankAccount,
  getBankAccount,
  getBankTransaction,
  getBankTransfer,
  listBankAccounts,
  listBankTransactions,
  listBankTransfers,
  postBankTransfer,
  reconcileBankTransaction,
  updateBankAccount,
} from "@/features/banking/api";

import {
  bankingQueryKeys,
} from "@/features/banking/query-keys";

import type {
  BankAccountListParameters,
  BankTransactionListParameters,
  BankTransferListParameters,
  CreateBankAccountInput,
  CreateBankTransactionInput,
  CreateBankTransferInput,
  UpdateBankAccountInput,
} from "@/features/banking/types";

export function useBankAccountList(
  parameters:
    BankAccountListParameters,
) {
  return useQuery({
    queryKey:
      bankingQueryKeys
      .accountList(
        parameters,
      ),

    queryFn: () =>
      listBankAccounts(
        parameters,
      ),

    staleTime: 30_000,
  });
}

export function useBankAccount(
  bankAccountId: string,
  enabled = true,
) {
  return useQuery({
    queryKey:
      bankingQueryKeys
      .accountDetail(
        bankAccountId,
      ),

    queryFn: () =>
      getBankAccount(
        bankAccountId,
      ),

    enabled:
      enabled
      &&
      Boolean(
        bankAccountId,
      ),

    staleTime: 30_000,
  });
}

export function useCreateBankAccount() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      input:
        CreateBankAccountInput,
    ) =>
      createBankAccount(
        input,
      ),

    onSuccess: async (
      bankAccount,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .accountDetail(
            bankAccount.id,
          ),
        bankAccount,
      );

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .accountLists(),
        }),

        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transactionLists(),
        }),
      ]);
    },
  });
}

interface UpdateBankAccountVariables {
  bankAccountId: string;
  input: UpdateBankAccountInput;
}

export function useUpdateBankAccount() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      bankAccountId,
      input,
    }: UpdateBankAccountVariables) =>
      updateBankAccount(
        bankAccountId,
        input,
      ),

    onSuccess: async (
      bankAccount,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .accountDetail(
            bankAccount.id,
          ),
        bankAccount,
      );

      await queryClient
        .invalidateQueries({
          queryKey:
            bankingQueryKeys
            .accountLists(),
        });
    },
  });
}

export function useDeactivateBankAccount() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      bankAccountId: string,
    ) =>
      deactivateBankAccount(
        bankAccountId,
      ),

    onSuccess: async (
      bankAccount,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .accountDetail(
            bankAccount.id,
          ),
        bankAccount,
      );

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .accountLists(),
        }),

        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transactionLists(),
        }),

        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transferLists(),
        }),
      ]);
    },
  });
}

export function useBankTransactionList(
  parameters:
    BankTransactionListParameters,
) {
  return useQuery({
    queryKey:
      bankingQueryKeys
      .transactionList(
        parameters,
      ),

    queryFn: () =>
      listBankTransactions(
        parameters,
      ),

    staleTime: 15_000,
  });
}

export function useBankTransaction(
  transactionId: string,
  enabled = true,
) {
  return useQuery({
    queryKey:
      bankingQueryKeys
      .transactionDetail(
        transactionId,
      ),

    queryFn: () =>
      getBankTransaction(
        transactionId,
      ),

    enabled:
      enabled
      &&
      Boolean(
        transactionId,
      ),

    staleTime: 30_000,
  });
}

export function useCreateBankTransaction() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      input:
        CreateBankTransactionInput,
    ) =>
      createBankTransaction(
        input,
      ),

    onSuccess: async (
      transaction,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .transactionDetail(
            transaction.id,
          ),
        transaction,
      );

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transactionLists(),
        }),

        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .accounts(),
        }),
      ]);
    },
  });
}

export function useReconcileBankTransaction() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      transactionId: string,
    ) =>
      reconcileBankTransaction(
        transactionId,
      ),

    onSuccess: async (
      transaction,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .transactionDetail(
            transaction.id,
          ),
        transaction,
      );

      await queryClient
        .invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transactionLists(),
        });
    },
  });
}

export function useBankTransferList(
  parameters:
    BankTransferListParameters,
) {
  return useQuery({
    queryKey:
      bankingQueryKeys
      .transferList(
        parameters,
      ),

    queryFn: () =>
      listBankTransfers(
        parameters,
      ),

    staleTime: 15_000,
  });
}

export function useBankTransfer(
  transferId: string,
  enabled = true,
) {
  return useQuery({
    queryKey:
      bankingQueryKeys
      .transferDetail(
        transferId,
      ),

    queryFn: () =>
      getBankTransfer(
        transferId,
      ),

    enabled:
      enabled
      &&
      Boolean(
        transferId,
      ),

    staleTime: 30_000,
  });
}

export function useCreateBankTransfer() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      input:
        CreateBankTransferInput,
    ) =>
      createBankTransfer(
        input,
      ),

    onSuccess: async (
      transfer,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .transferDetail(
            transfer.id,
          ),
        transfer,
      );

      await queryClient
        .invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transferLists(),
        });
    },
  });
}

export function usePostBankTransfer() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      transferId: string,
    ) =>
      postBankTransfer(
        transferId,
      ),

    onSuccess: async (
      transfer,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .transferDetail(
            transfer.id,
          ),
        transfer,
      );

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transferLists(),
        }),

        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .accounts(),
        }),

        queryClient.invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transactionLists(),
        }),
      ]);
    },
  });
}

export function useCancelBankTransfer() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      transferId: string,
    ) =>
      cancelBankTransfer(
        transferId,
      ),

    onSuccess: async (
      transfer,
    ) => {
      queryClient.setQueryData(
        bankingQueryKeys
          .transferDetail(
            transfer.id,
          ),
        transfer,
      );

      await queryClient
        .invalidateQueries({
          queryKey:
            bankingQueryKeys
            .transferLists(),
        });
    },
  });
}