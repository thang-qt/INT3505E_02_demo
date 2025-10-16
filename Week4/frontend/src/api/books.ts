import { request } from "./client";

export type Book = {
  id: number;
  title: string;
  author: string;
  publisher: string;
  publication_year: number;
  quantity: number;
};

export type BookInput = {
  title: string;
  author: string;
  publisher: string;
  publication_year: number;
  quantity: number;
};

export const listBooks = async (): Promise<Book[]> => {
  return request<Book[]>("/books", {
    method: "GET"
  });
};

export const createBook = async (payload: BookInput): Promise<Book> => {
  return request<Book>("/books", {
    method: "POST",
    body: JSON.stringify(payload)
  });
};

export const updateBook = async (id: number, payload: Partial<BookInput>): Promise<Book> => {
  return request<Book>(`/books/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
};

export const deleteBook = async (id: number): Promise<void> => {
  await request(`/books/${id}`, {
    method: "DELETE"
  });
};
