import { ChangeEvent } from "react";
import { Button, Card, Flex, Heading, Text } from "@radix-ui/themes";
import { Loan } from "../api/loans";

type LoanListProps = {
  loans: Loan[];
  loading: boolean;
  includeHistory: boolean;
  onIncludeHistoryChange: (value: boolean) => void;
  onReturn: (id: number) => Promise<void> | void;
  returningId: number | null;
};

const LoanList = ({ loans, loading, includeHistory, onIncludeHistoryChange, onReturn, returningId }: LoanListProps) => {
  const handleIncludeHistoryChange = (event: ChangeEvent<HTMLInputElement>) => {
    onIncludeHistoryChange(event.target.checked);
  };

  return (
    <Flex direction="column" gap="3">
      <Flex align="center" justify="between">
        <Heading size="6">Loans</Heading>
        <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <input type="checkbox" checked={includeHistory} onChange={handleIncludeHistoryChange} />
          <Text size="2">Include returned</Text>
        </label>
      </Flex>
      {loading ? (
        <Text>Loading loans...</Text>
      ) : loans.length === 0 ? (
        <Card>
          <Text size="3">No loans recorded</Text>
        </Card>
      ) : (
        <Flex direction="column" gap="3">
          {loans.map((loan) => (
            <Card key={loan.id}>
              <Flex align="center" justify="between">
                <Flex direction="column" gap="1">
                  <Heading size="4">Borrower: {loan.borrower}</Heading>
                  <Text size="2">Book ID: {loan.book_id}</Text>
                  <Text size="2">Loaned at: {new Date(loan.loaned_at).toLocaleString()}</Text>
                  <Text size="2">Returned: {loan.returned ? new Date(loan.returned_at ?? "").toLocaleString() : "No"}</Text>
                </Flex>
                <Button
                  onClick={() => onReturn(loan.id)}
                  disabled={loan.returned || returningId === loan.id}
                >
                  {loan.returned ? "Returned" : returningId === loan.id ? "Returning" : "Return"}
                </Button>
              </Flex>
            </Card>
          ))}
        </Flex>
      )}
    </Flex>
  );
};

export default LoanList;
