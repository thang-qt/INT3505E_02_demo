import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { Button, Flex, TextField } from "@radix-ui/themes";
import { Book } from "../api/books";
import { LoanInput } from "../api/loans";

type LoanFormProps = {
  books: Book[];
  onSubmit: (input: LoanInput) => Promise<void> | void;
  submitting: boolean;
};

const LoanForm = ({ books, onSubmit, submitting }: LoanFormProps) => {
  const [selection, setSelection] = useState<string>("");
  const [borrower, setBorrower] = useState<string>("");

  useEffect(() => {
    if (books.length === 0) {
      setSelection("");
      return;
    }
    if (!selection) {
      setSelection(String(books[0].id));
    }
  }, [books, selection]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selection) {
      return;
    }
    const payload = {
      book_id: Number.parseInt(selection, 10),
      borrower: borrower.trim()
    };
    await onSubmit(payload);
  };

  const handleSelectionChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setSelection(event.target.value);
  };

  const handleBorrowerChange = (event: ChangeEvent<HTMLInputElement>) => {
    setBorrower(event.target.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Flex direction="column" gap="3">
        <select value={selection} onChange={handleSelectionChange} required disabled={books.length === 0}>
          <option value="" disabled>
            Select a book
          </option>
          {books.map((book) => (
            <option key={book.id} value={book.id}>
              {book.title} ({book.quantity} available)
            </option>
          ))}
        </select>
        <TextField.Root>
          <TextField.Input
            placeholder="Borrower name"
            value={borrower}
            onChange={handleBorrowerChange}
            required
          />
        </TextField.Root>
        <Button type="submit" disabled={submitting || books.length === 0}>
          {submitting ? "Processing" : "Create loan"}
        </Button>
      </Flex>
    </form>
  );
};

export default LoanForm;
