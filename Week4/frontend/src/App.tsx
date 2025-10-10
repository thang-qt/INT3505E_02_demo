import { useCallback, useEffect, useMemo, useState } from "react";
import { Box, Button, Container, Dialog, Flex, Heading, Text } from "@radix-ui/themes";
import BookForm from "./components/BookForm";
import BookList from "./components/BookList";
import { Book, BookInput, createBook, deleteBook, listBooks, updateBook } from "./api/books";

const App = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

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

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  const handleCreate = async (input: BookInput) => {
    setSubmitting(true);
    setError(null);
    try {
      await createBook(input);
      await fetchBooks();
      setCreateDialogOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create book");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    setError(null);
    try {
      await deleteBook(id);
      await fetchBooks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete book");
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
    setUpdating(true);
    setError(null);
    try {
      await updateBook(editingBook.id, input);
      await fetchBooks();
      setEditDialogOpen(false);
      setEditingBook(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update book");
    } finally {
      setUpdating(false);
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
          <Dialog.Root open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <Dialog.Trigger>
              <Button>Add Book</Button>
            </Dialog.Trigger>
            <Dialog.Content maxWidth="450px">
              <Dialog.Title>Add a book</Dialog.Title>
              <Dialog.Description mb="4">Provide basic details to add a book to the catalog.</Dialog.Description>
              <BookForm onSubmit={handleCreate} submitting={submitting} />
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
          <BookList books={books} onEdit={handleEditOpen} onDelete={handleDelete} deletingId={deletingId} />
        )}
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
