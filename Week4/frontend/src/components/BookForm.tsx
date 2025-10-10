import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { Button, Flex, TextField } from "@radix-ui/themes";
import { BookInput } from "../api/books";

type BookFormProps = {
  initialValues?: BookInput;
  onSubmit: (input: BookInput) => Promise<void> | void;
  submitting: boolean;
  submitLabel?: string;
};

type FormState = {
  title: string;
  author: string;
  publisher: string;
  publication_year: string;
  quantity: string;
};

const toFormState = (values?: BookInput): FormState => ({
  title: values?.title ?? "",
  author: values?.author ?? "",
  publisher: values?.publisher ?? "",
  publication_year: values ? String(values.publication_year) : "",
  quantity: values ? String(values.quantity) : ""
});

const BookForm = ({ initialValues, onSubmit, submitting, submitLabel }: BookFormProps) => {
  const [formState, setFormState] = useState<FormState>(toFormState(initialValues));

  useEffect(() => {
    setFormState(toFormState(initialValues));
  }, [initialValues]);

  const handleChange = (field: keyof FormState) => (event: ChangeEvent<HTMLInputElement>) => {
    setFormState((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const payload = {
      title: formState.title.trim(),
      author: formState.author.trim(),
      publisher: formState.publisher.trim(),
      publication_year: Number.parseInt(formState.publication_year, 10),
      quantity: Number.parseInt(formState.quantity, 10)
    };
    await onSubmit(payload);
    if (!initialValues) {
      setFormState(toFormState());
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Flex direction="column" gap="3">
        <TextField.Root>
          <TextField.Input
            placeholder="Title"
            value={formState.title}
            onChange={handleChange("title")}
            required
          />
        </TextField.Root>
        <TextField.Root>
          <TextField.Input
            placeholder="Author"
            value={formState.author}
            onChange={handleChange("author")}
            required
          />
        </TextField.Root>
        <TextField.Root>
          <TextField.Input
            placeholder="Publisher"
            value={formState.publisher}
            onChange={handleChange("publisher")}
            required
          />
        </TextField.Root>
        <TextField.Root>
          <TextField.Input
            type="number"
            placeholder="Publication Year"
            value={formState.publication_year}
            onChange={handleChange("publication_year")}
            required
            min={1}
          />
        </TextField.Root>
        <TextField.Root>
          <TextField.Input
            type="number"
            placeholder="Quantity"
            value={formState.quantity}
            onChange={handleChange("quantity")}
            required
            min={0}
          />
        </TextField.Root>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving" : submitLabel ?? "Save"}
        </Button>
      </Flex>
    </form>
  );
};

export default BookForm;
