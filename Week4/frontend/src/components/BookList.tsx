import { Button, Card, Flex, Heading, Text } from "@radix-ui/themes";
import { Pencil1Icon, TrashIcon } from "@radix-ui/react-icons";
import { Book } from "../api/books";

type BookListProps = {
  books: Book[];
  onEdit: (book: Book) => void;
  onDelete: (id: number) => Promise<void> | void;
  deletingId: number | null;
  canManage: boolean;
};

const BookList = ({ books, onEdit, onDelete, deletingId, canManage }: BookListProps) => {
  if (books.length === 0) {
    return (
      <Card>
        <Text size="3">No books available</Text>
      </Card>
    );
  }
  return (
    <Flex direction="column" gap="3">
      {books.map((book) => (
        <Card key={book.id}>
          <Flex align="center" justify="between" gap="4">
            <Flex direction="column" gap="1">
              <Heading size="4">{book.title}</Heading>
              <Text size="3" color="gray">{book.author}</Text>
              <Text size="2" color="gray">{book.publisher} • {book.publication_year}</Text>
              <Text size="2">Quantity: {book.quantity}</Text>
            </Flex>
            <Flex align="center" gap="2">
              <Button variant="soft" onClick={() => onEdit(book)} disabled={!canManage}>
                <Pencil1Icon />
                Edit
              </Button>
              <Button
                color="red"
                variant="soft"
                onClick={() => onDelete(book.id)}
                disabled={!canManage || deletingId === book.id}
              >
                <TrashIcon />
                {deletingId === book.id ? "Removing" : "Remove"}
              </Button>
            </Flex>
          </Flex>
        </Card>
      ))}
    </Flex>
  );
};

export default BookList;
