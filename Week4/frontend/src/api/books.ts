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

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
const API_BASE = baseUrl !== "" ? baseUrl.replace(/\/$/, "") : "/api";

const resolveUrl = (path: string) => `${API_BASE}${path}`;

const defaultHeaders = {
  "Content-Type": "application/json"
};

export const listBooks = async (): Promise<Book[]> => {
  const response = await fetch(resolveUrl("/books"), {
    method: "GET",
    headers: defaultHeaders,
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Failed to load books");
  }
  return response.json();
};

export const createBook = async (payload: BookInput): Promise<Book> => {
  const response = await fetch(resolveUrl("/books"), {
    method: "POST",
    headers: defaultHeaders,
    body: JSON.stringify(payload),
    cache: "no-store"
  });
  if (!response.ok) {
    const message = await response.json().catch(() => ({ message: "Failed to create book" }));
    throw new Error(message.message ?? "Failed to create book");
  }
  return response.json();
};

export const updateBook = async (id: number, payload: Partial<BookInput>): Promise<Book> => {
  const response = await fetch(resolveUrl(`/books/${id}`), {
    method: "PUT",
    headers: defaultHeaders,
    body: JSON.stringify(payload),
    cache: "no-store"
  });
  if (!response.ok) {
    const message = await response.json().catch(() => ({ message: "Failed to update book" }));
    throw new Error(message.message ?? "Failed to update book");
  }
  return response.json();
};

export const deleteBook = async (id: number): Promise<void> => {
  const response = await fetch(resolveUrl(`/books/${id}`), {
    method: "DELETE",
    headers: defaultHeaders,
    cache: "no-store"
  });
  if (!response.ok) {
    const message = await response.json().catch(() => ({ message: "Failed to delete book" }));
    throw new Error(message.message ?? "Failed to delete book");
  }
};
