# Comment Public Functions and API Endpoints

## Rule

Every public function and every API endpoint MUST have a docstring or doc comment.

### What counts as "public"

- Any function, method, or class **not** prefixed with `_` (Python) or marked `private`/`internal`
- Any route handler decorated with a framework decorator (e.g. `@app.get`, `@app.post`, `@router.put`, `@app.delete`, `@app.patch`)

### Required comment content

The comment MUST include, at minimum:

1. **Summary** — one line describing what the function does
2. **Parameters** — each parameter with its type and meaning (skip `self`/`cls`)
3. **Return value** — what is returned and its type (skip for `None`/void)
4. **Raises** — any exceptions that may be raised (if applicable)

For API endpoints also include:

5. **Request body** — shape and required fields (if applicable)
6. **Response shape** — the fields returned on success

### Style

- **Python**: use Google-style or NumPy-style docstrings inside triple quotes (`"""`)
- **TypeScript / JavaScript**: use JSDoc (`/** ... */`)
- **Other languages**: follow the idiomatic doc-comment style for that language

### Examples

#### Python — plain function

```python
def get_todo_by_id(todo_id: int) -> Todo:
    """Retrieve a single todo item by its primary key.

    Args:
        todo_id: The integer primary key of the todo to fetch.

    Returns:
        The matching Todo object.

    Raises:
        HTTPException: 404 if no todo with the given id exists.
    """
```

#### Python — FastAPI endpoint

```python
@router.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    """Return a single todo item.

    Args:
        todo_id: Path parameter identifying the todo.
        db: Database session injected by FastAPI's dependency system.

    Returns:
        TodoResponse containing id, title, completed, and created_at.

    Raises:
        HTTPException: 404 if the todo does not exist.
    """
```

#### TypeScript — exported function

```typescript
/**
 * Calculates the total price including tax.
 *
 * @param subtotal - The pre-tax amount in cents.
 * @param taxRate  - The tax rate as a decimal (e.g. 0.08 for 8 %).
 * @returns The total amount in cents after applying the tax rate.
 */
export function calculateTotal(subtotal: number, taxRate: number): number {
```

### Enforcement

- When **writing new code**, always add the doc comment before returning the implementation.
- When **editing an existing function**, add or update the doc comment if it is missing or stale.
- When **reviewing code**, flag any public function or API endpoint that lacks a proper doc comment and add one.
- Do **not** add doc comments to private helpers, test utilities, or one-liner lambdas where the name is self-explanatory and there are no parameters to document.
