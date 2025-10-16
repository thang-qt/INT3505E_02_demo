import { useCallback, useEffect, useMemo, useState } from "react";
import { Box, Button, Container, Dialog, Flex, Heading, Text } from "@radix-ui/themes";
import BookForm from "./components/BookForm";
import BookList from "./components/BookList";
import LoanForm from "./components/LoanForm";
import LoanList from "./components/LoanList";
import LoginForm from "./components/LoginForm";
import { Book, BookInput, createBook, deleteBook, listBooks, updateBook } from "./api/books";
import { login } from "./api/auth";
import { initializeToken, setToken as persistToken, getToken } from "./api/client";
import { Loan, createLoan, listLoans, returnLoan } from "./api/loans";

const App = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [loginSubmitting, setLoginSubmitting] = useState(false);
  const [token, setTokenState] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [loanDialogOpen, setLoanDialogOpen] = useState(false);
  const [loanSubmitting, setLoanSubmitting] = useState(false);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loansLoading, setLoansLoading] = useState(true);
  const [loanError, setLoanError] = useState<string | null>(null);
  const [returningId, setReturningId] = useState<number | null>(null);
  const [includeHistory, setIncludeHistory] = useState(false);

  useEffect(() => {
    initializeToken();
    setTokenState(getToken());
  }, []);

  const isAuthenticated = Boolean(token);

  const ensureAuthenticated = () => {
    if (!isAuthenticated) {
      setError("Authentication required");
      return false;
    }
    return true;
  };

  const handleFailure = (err: unknown, fallback: string) => {
    const message = err instanceof Error ? err.message : fallback;
    if (message === "Unauthorized") {
      persistToken(null);
      setTokenState(null);
      setAuthError("Session expired. Sign in again.");
      return;
    }
    setError(message);
  };

  const fetchBooks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listBooks();
      setBooks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load books");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLoans = useCallback(async () => {
    setLoansLoading(true);
    setLoanError(null);
    try {
      const data = await listLoans(includeHistory);
      setLoans(data);
    } catch (err) {
      setLoanError(err instanceof Error ? err.message : "Failed to load loans");
    } finally {
      setLoansLoading(false);
    }
  }, [includeHistory]);

  const handleLoanFailure = (err: unknown, fallback: string) => {
    const message = err instanceof Error ? err.message : fallback;
    if (message === "Unauthorized") {
      persistToken(null);
      setTokenState(null);
      setAuthError("Session expired. Sign in again.");
      return;
    }
    setLoanError(message);
  };

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  useEffect(() => {
    fetchLoans();
  }, [fetchLoans]);

  const handleCreate = async (input: BookInput) => {
    if (!ensureAuthenticated()) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await createBook(input);
      await fetchBooks();
      setCreateDialogOpen(false);
    } catch (err) {
      handleFailure(err, "Failed to create book");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!ensureAuthenticated()) {
      return;
    }
    setDeletingId(id);
    setError(null);
    try {
      await deleteBook(id);
      await fetchBooks();
    } catch (err) {
      handleFailure(err, "Failed to delete book");
    } finally {
      setDeletingId(null);
    }
  };

  const handleEditOpen = (book: Book) => {
    setEditingBook(book);
    setEditDialogOpen(true);
  };

  const handleUpdate = async (input: BookInput) => {
    if (!editingBook) {
      return;
    }
    if (!ensureAuthenticated()) {
      return;
    }
    setUpdating(true);
    setError(null);
    try {
      await updateBook(editingBook.id, input);
      await fetchBooks();
      setEditDialogOpen(false);
      setEditingBook(null);
    } catch (err) {
      handleFailure(err, "Failed to update book");
    } finally {
      setUpdating(false);
    }
  };

  const handleLogin = async (credentials: { username: string; password: string }) => {
    setLoginSubmitting(true);
    setAuthError(null);
    try {
      const response = await login(credentials);
      persistToken(response.token);
      setTokenState(response.token);
      setAuthError(null);
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Failed to sign in");
    } finally {
      setLoginSubmitting(false);
    }
  };

  const handleLogout = () => {
    persistToken(null);
    setTokenState(null);
  };

  const handleCreateLoan = async (input: { book_id: number; borrower: string }) => {
    if (!ensureAuthenticated()) {
      return;
    }
    setLoanSubmitting(true);
    setLoanError(null);
    try {
      await createLoan(input);
      await fetchBooks();
      await fetchLoans();
      setLoanDialogOpen(false);
    } catch (err) {
      handleLoanFailure(err, "Failed to create loan");
    } finally {
      setLoanSubmitting(false);
    }
  };

  const handleReturnLoan = async (id: number) => {
    if (!ensureAuthenticated()) {
      return;
    }
    setReturningId(id);
    setLoanError(null);
    try {
      await returnLoan(id);
      await fetchBooks();
      await fetchLoans();
    } catch (err) {
      handleLoanFailure(err, "Failed to return loan");
    } finally {
      setReturningId(null);
    }
  };

  const editInitialValues = useMemo(() => {
    if (!editingBook) {
      return undefined;
    }
    return {
      title: editingBook.title,
      author: editingBook.author,
      publisher: editingBook.publisher,
      publication_year: editingBook.publication_year,
      quantity: editingBook.quantity
    };
  }, [editingBook]);

  return (
    <Container size="3" pt="6" pb="7">
      <Flex direction="column" gap="5">
        <Flex align="center" justify="between">
          <Heading size="8">Library</Heading>
          {isAuthenticated ? (
            <Button variant="soft" onClick={handleLogout}>
              Sign out
            </Button>
          ) : null}
        </Flex>
        {!isAuthenticated ? (
          <Box px="4" py="4" style={{ backgroundColor: "#f8fafc", borderRadius: "12px" }}>
            <Flex direction="column" gap="3">
              <Heading size="5">Sign in</Heading>
              {authError && (
                <Box px="3" py="2" style={{ backgroundColor: "#fee2e2", borderRadius: "8px" }}>
                  <Text color="red">{authError}</Text>
                </Box>
              )}
              <LoginForm onSubmit={handleLogin} submitting={loginSubmitting} />
            </Flex>
          </Box>
        ) : null}
        <Flex align="center" justify="between">
          <Dialog.Root open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <Dialog.Trigger>
              <Button disabled={!isAuthenticated}>Add Book</Button>
            </Dialog.Trigger>
            <Dialog.Content maxWidth="450px">
              <Dialog.Title>Add a book</Dialog.Title>
              <Dialog.Description mb="4">Provide basic details to add a book to the catalog.</Dialog.Description>
              <BookForm onSubmit={handleCreate} submitting={submitting} />
            </Dialog.Content>
          </Dialog.Root>
          <Dialog.Root open={loanDialogOpen} onOpenChange={setLoanDialogOpen}>
            <Dialog.Trigger>
              <Button disabled={!isAuthenticated}>Create Loan</Button>
            </Dialog.Trigger>
            <Dialog.Content maxWidth="450px">
              <Dialog.Title>Create loan</Dialog.Title>
              <Dialog.Description mb="4">Choose a book and borrower to record a loan.</Dialog.Description>
              <LoanForm
                key={loanDialogOpen ? "open" : "closed"}
                books={books}
                onSubmit={handleCreateLoan}
                submitting={loanSubmitting}
              />
            </Dialog.Content>
          </Dialog.Root>
        </Flex>
        {error && (
          <Box px="4" py="3" style={{ backgroundColor: "#fee2e2", borderRadius: "12px" }}>
            <Text color="red">{error}</Text>
          </Box>
        )}
        {loading ? (
          <Text>Loading books...</Text>
        ) : (
          <BookList
            books={books}
            onEdit={handleEditOpen}
            onDelete={handleDelete}
            deletingId={deletingId}
            canManage={isAuthenticated}
          />
        )}
        {loanError && (
          <Box px="4" py="3" style={{ backgroundColor: "#fee2e2", borderRadius: "12px" }}>
            <Text color="red">{loanError}</Text>
          </Box>
        )}
        <LoanList
          loans={loans}
          loading={loansLoading}
          includeHistory={includeHistory}
          onIncludeHistoryChange={setIncludeHistory}
          onReturn={handleReturnLoan}
          returningId={returningId}
        />
      </Flex>
      <Dialog.Root
        open={editDialogOpen}
        onOpenChange={(open) => {
          setEditDialogOpen(open);
          if (!open) {
            setEditingBook(null);
          }
        }}
      >
        <Dialog.Content maxWidth="450px">
          <Dialog.Title>Edit book</Dialog.Title>
          <Dialog.Description mb="4">Update the details for this book.</Dialog.Description>
          <BookForm
            initialValues={editInitialValues}
            onSubmit={handleUpdate}
            submitting={updating}
            submitLabel="Update"
          />
        </Dialog.Content>
      </Dialog.Root>
    </Container>
  );
};

export default App;
