import { ChangeEvent, FormEvent, useState } from "react";
import { Button, Flex, TextField } from "@radix-ui/themes";
import { LoginInput } from "../api/auth";

type LoginFormProps = {
  onSubmit: (input: LoginInput) => Promise<void> | void;
  submitting: boolean;
};

const LoginForm = ({ onSubmit, submitting }: LoginFormProps) => {
  const [formState, setFormState] = useState<LoginInput>({ username: "", password: "" });

  const handleChange = (field: keyof LoginInput) => (event: ChangeEvent<HTMLInputElement>) => {
    setFormState((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const payload = {
      username: formState.username.trim(),
      password: formState.password
    };
    await onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Flex direction="column" gap="3">
        <TextField.Root>
          <TextField.Input
            placeholder="Username"
            value={formState.username}
            onChange={handleChange("username")}
            required
          />
        </TextField.Root>
        <TextField.Root>
          <TextField.Input
            type="password"
            placeholder="Password"
            value={formState.password}
            onChange={handleChange("password")}
            required
          />
        </TextField.Root>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Signing in" : "Sign in"}
        </Button>
      </Flex>
    </form>
  );
};

export default LoginForm;
