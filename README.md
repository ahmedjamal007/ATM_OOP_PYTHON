# ATM_OOP_PYTHON

A console ATM simulator written in Python. I built it to learn **object-oriented
programming** by modelling something that actually has objects in it — a bank, a
customer, a card, an account, transactions — instead of learning the theory from
isolated `class Dog: def bark()` examples.

The point of the project is the *design*, not the features. Everything runs in
memory and resets when you quit.

---

## What it does

Insert a card, enter a PIN, and you get a menu:

| # | Option | What happens |
|---|---|---|
| 1 | Check balance | Reads the account balance |
| 2 | Withdraw | Subtracts an amount, records the transaction |
| 3 | Deposit | Adds an amount, records the transaction |
| 4 | Show transactions | Prints this account's transaction history |
| 5 | Transfer | Moves money to another account in the same bank |
| 6 | Change PIN | Asks for old + new PIN and replaces it |
| 7 | Exit | Ends the session |

## Running it

```bash
python main.py
```

Two demo accounts are created at startup by `build_bank()` in `main.py`:

| Account | Customer | Balance | PIN |
|---|---|---|---|
| 1001 | John Doe | 5000.0 | 1234 |
| 1002 | Jane Roe | 1200.0 | 4321 |

Log in with PIN `1234`, then pick option 5 and transfer to account `1002` to
watch money move between two accounts.

Requires Python 3.7+ and no third-party packages.

---

## Project structure

One class per concept, each in its own module. Arrows point from a module to the
modules it imports, and nothing points backwards — the dependencies flow one
way, which is what keeps circular imports from happening:

```
main.py              entry point - builds the bank, inserts the card
  |
  +-- atm.py         AtmInterFace (menu + dispatch), CardReader
        |
        +-- Transaction.py     TransactionType, Transaction (+4 subclasses), 4 handlers
        +-- authentication.py  Authentication (PIN check, PIN change)
        +-- screen.py          Screen (all printing)
              |
              +-- keypad.py    Keypad (all reading - the only input() in the project)

Account.py   bank.py   card.py   customer.py       the domain objects
```

### The two hardware classes

`Screen` and `Keypad` model the two physical parts of an ATM a user touches, and
splitting them that way gives each one exactly one job:

```python
# keypad.py
class Keypad():
    def get_input(self, prompt: str, secure: bool = False):
        if secure:
            return self.get_secure_input(prompt)
        return input(prompt)

    def get_secure_input(self, prompt: str):
        return getpass.getpass(prompt)
```

Every prompt in the program goes through `get_input`. The only raw `input()`
call left in the whole project is the one inside `Keypad` itself - a single
chokepoint. PINs pass `secure=True`, which routes them to `getpass` so the
digits never appear on screen:

| Prompt | Secure? |
|---|---|
| PIN at card insert (`atm.py`) | yes |
| old / new / confirm PIN (`authentication.py`) | yes |
| menu choice, amount (`atm.py`) | no |
| recipient account, yes/no confirm (`Transaction.py`) | no |
| "press any key" (`screen.py`) | no |

The payoff is that hiding a PIN is **one argument**, not a reimplementation at
each of the four places a PIN gets typed. If the ATM later needs a real numeric
keypad, or needs to log every keystroke, there is one class to change.

> **Testing note:** `getpass` reads the terminal directly and ignores piped
> stdin, so `echo 1234 | python main.py` will hang at the PIN prompt on Windows.
> Run it interactively, or patch `keypad.getpass.getpass` in a test harness.

### Why `Screen` has its own file

`Screen` started out inside `atm.py`. But `Transaction.py` and
`authentication.py` both need to print messages, and `atm.py` needs the
transaction handlers — so `atm.py` -> `Transaction.py` -> `atm.py` was a loop
and Python refused to import it. Moving `Screen` into a leaf module that imports
nothing broke the cycle.

**Lesson: when two modules need each other, the thing they both depend on
usually wants to be pulled out into a third module.**

### Why some imports sit inside `if TYPE_CHECKING:`

`Account` mentions `Transaction` and `Customer` in its type hints, and both of
those mention `Account` right back — a real circular reference in the *design*.
But it only exists in the type hints, never in the running code, so those
imports are guarded:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:          # False at runtime, so this never actually imports
    from bank import Bank  # but mypy / Pyright / the IDE still read it

class Account():
    def __init__(self, account_number: int, balance: float, bank: Bank, ...):
```

`TYPE_CHECKING` is just a constant that equals `False` when Python runs, and
that type checkers pretend is `True`. You keep the autocomplete and the type
errors without paying for the import.

Rule of thumb: **if a name only ever appears in a type hint, guard it; if you
actually call or instantiate it, import it normally.** That is why `screen.py`
and `authentication.py` are imported for real in `atm.py` (it builds a `Screen()`
and an `Authentication()`), while all four of `Account.py`'s imports are guarded.

---

## The OOP principles in this project

### 1. Encapsulation — hiding data behind methods

The clearest example is the PIN. `Card` stores it with two leading underscores,
which makes Python *name-mangle* the attribute so outside code cannot reach it:

```python
# card.py
class Card():
    def __init__(self, card_number: int, pin_code: str):
        self.card_number = card_number
        self.__pin_code = pin_code      # private

    def get_pin_code(self):             # controlled read
        return self.__pin_code

    def rest_pin_code(self, old_pin, new_pin):   # controlled write...
        if self.__pin_code == old_pin:           # ...with a rule attached
            self.__pin_code = new_pin
            return True
        return False
```

```python
>>> card.__pin_code
AttributeError: 'Card' object has no attribute '__pin_code'
>>> vars(card)
{'card_number': 1001, '_Card__pin_code': '1234'}   # renamed, not truly secret
```

Here is why it matters: `rest_pin_code` **cannot** change the PIN without the
old one. The rule lives inside the object that owns the data, so no caller can
forget to check it. That is encapsulation — not "make everything private", but
"don't let outside code reach in and break a rule".

### 2. Abstraction — a contract without an implementation

`Transaction` is an **abstract base class**. It says *every transaction has an
id, a timestamp, an account, an amount, and can be executed* — without saying
what executing means:

```python
# Transaction.py
class Transaction(ABC):
    def __init__(self, type: str, account: Account, amount: float = None):
        self.transaction_id = uuid4()
        self.timestamp = datetime.now()
        ...

    @abstractmethod
    def execute(self):
        pass
```

Python enforces the contract — the class cannot be created directly:

```python
>>> Transaction('x', account, 100)
TypeError: Can't instantiate abstract class Transaction without an
           implementation for abstract method 'execute'
```

So the shared bookkeeping (id, timestamp) is written **once**, and every subclass
is *forced* to supply `execute`. Add a new transaction type and forget it, and
you find out immediately instead of halfway through a withdrawal.

### 3. Inheritance — reusing the parent

Four concrete transactions extend `Transaction` and get its `__init__` for free
through `super().__init__(...)`:

```
WithdrawalTransaction     --+
DepositTransaction        --+
BalanceInquiryTransaction --+--> Transaction --> ABC
TransferTransaction       --+
```

Each one writes only the part that is genuinely different.
`BalanceInquiryTransaction` is five lines long because everything else is
inherited.

### 4. Polymorphism — one call, different behaviour

Every subclass overrides `execute()`, so the *same* method name does the right
thing for each type:

```python
WithdrawalTransaction.execute()      # balance -= amount, returns True
DepositTransaction.execute()         # balance += amount, returns a message
BalanceInquiryTransaction.execute()  # touches nothing, returns the balance
TransferTransaction.execute()        # runs a withdrawal AND a deposit
```

`TransferTransaction` shows the payoff — it **reuses the other two transaction
objects** instead of re-implementing the arithmetic:

```python
def execute(self):
    Withdrawal = WithdrawalTransaction(TransactionType.WITHDRAWAL, self.account, self.amount)
    transaction_successful = Withdrawal.execute(call_back=True)
    if transaction_successful:
        Deposit = DepositTransaction(TransactionType.DEPOSIT, self.recipient_account, self.amount)
        Deposit.execute(call_back=True)
        ...
```

### 5. Composition — objects built out of other objects

Most of the structure here is "has-a", not "is-a", and that is deliberate. An
account **is not** a kind of bank; it **has** a bank:

```
Bank         has many  Account          (self.accounts dict)
Customer     has many  Account          (self.accounts dict)
Account      has one   Bank, Customer, Card + a list of Transactions
AtmInterFace has a     Screen + an Authentication
CardReader   has a     Card + an AtmInterFace
```

```python
>>> {k: type(v).__name__ for k, v in vars(account).items()}
{'transactions_number': 'UUID', 'transactions': 'list', 'bank': 'Bank',
 'account_number': 'int', 'balance': 'float', 'linked_card': 'Card',
 'coustmer': 'Customer'}
```

*Prefer composition over inheritance* is the usual advice, and this project is a
decent illustration of when each one applies: inheritance for the transactions
(they really are all Transactions), composition for everything else.

### 6. Single responsibility — one job per class

Each class has one reason to change:

- `Screen` — the *only* place that prints. Swap it for a GUI and nothing else
  has to change.
- `Keypad` — the *only* place that reads what the user types, and the only class
  that knows `getpass` exists.
- `Authentication` — checking a PIN and changing a PIN, nothing more.
- `Account` — holds a balance and a transaction list; has no idea what an ATM is.
- `AtmInterFace` — shows the menu and dispatches; does no banking arithmetic.
- `*Transaction` classes — move the money.
- `*Handler` classes — talk to the user about a transaction (validate the input,
  report the result), then delegate to a `*Transaction`.

That last split is the one worth defending: `WithdrawalTransaction` knows how to
subtract money, `WithdarawlHandler` knows how to *ask* about it and print the
outcome. The money logic contains no `input()` and no `print()`, which is
exactly what makes it testable without an ATM:

```python
from main import build_bank
from Transaction import TransferTransaction

b = build_bank()
a, r = b.get_account_by_number(1001), b.get_account_by_number(1002)
TransferTransaction('Transfer', a, 300.0, r).execute()
assert a.balance == 4700.0 and r.balance == 1500.0   # no screen, no menu needed
```

---

## Known weaknesses — my learning to-do list

Being honest about what is still wrong is part of the exercise:

- **Withdrawals never check the balance.** `WithdarawlHandler` only tests
  `amount <= 0`, so withdrawing 99999 from 5000 succeeds and leaves the balance
  negative. That rule belongs *inside* `WithdrawalTransaction.execute` — the
  same encapsulation argument as the PIN above.
- **The handlers share no base class.** `WithdarawlHandler`,
  `BalanceInquiryHandle`, `DepositHandle` and `TransferHandle` are unrelated
  classes whose main methods are even named inconsistently
  (`transaction_handler`, `transction_handle`, `transction_handelr`). One
  abstract `TransactionHandler` with a single `handle()` method would turn the
  big `match` statement in `atm.py` into a dictionary lookup — real
  polymorphism instead of a switch.
- **`execute()` signatures disagree across subclasses** — some take `call_back`,
  some do not; some return `bool`, one returns `str`. A subclass should be
  usable anywhere the parent is; differing signatures break that (the *Liskov
  substitution* principle), and it is why the `call_back` flag feels awkward.
- **`Screen` still triggers a read.** Input and output are now separate classes
  (`Keypad` and `Screen`), but `clear_screen()` still calls the keypad to wait
  for a keypress, which is why every message pauses. Arguably the *caller* should
  decide when to pause, not `Screen`.
- **No persistence.** Change a PIN and restart, and it is back to `1234`,
  because the whole bank lives in memory.
- **Spelling.** `coustmer`, `WithdarawlHandler`, `rest_pin_code`, `sucsess`.
  Left alone for now because renaming touches every call site, but naming is
  part of design.

## Ideas to practise on next

1. Add the insufficient-funds check, and make `TransferTransaction` roll back
   cleanly when the debit fails.
2. Extract an abstract `TransactionHandler` base class and replace the `match`
   block with a `{choice: HandlerClass}` dictionary.
3. Add a `SavingsAccount` with an interest rate and a `CheckingAccount` with an
   overdraft limit — a genuine reason to inherit from `Account`.
4. Limit failed PIN attempts to three and have `CardReader` retain the card.
5. Save and load the bank as JSON so state survives a restart.
6. Write unit tests for the `*Transaction` classes — they need no screen at all,
   which is the whole payoff of keeping the money logic out of the UI.
