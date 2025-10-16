import { request } from "./client";

export type Loan = {
  id: number;
  book_id: number;
  borrower: string;
  loaned_at: string;
  returned_at: string | null;
  returned: boolean;
};

export type LoanInput = {
  book_id: number;
  borrower: string;
};

export type LoanReturnInput = {
  returned: boolean;
};

export const listLoans = async (includeHistory: boolean): Promise<Loan[]> => {
  const flag = includeHistory ? "true" : "false";
  return request<Loan[]>(`/loans?include_history=${flag}`, {
    method: "GET"
  });
};

export const createLoan = async (payload: LoanInput): Promise<Loan> => {
  return request<Loan>("/loans", {
    method: "POST",
    body: JSON.stringify(payload)
  });
};

export const returnLoan = async (id: number): Promise<Loan> => {
  const payload: LoanReturnInput = { returned: true };
  return request<Loan>(`/loans/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
};
