# V1 API Documentation

# Authentication

All API requests are authenticated via token authentication.

For clients to authenticate, the token key should be included in the
Authorization HTTP header. The key should be prefixed by the string literal
"Token", with whitespace separating the two strings. For example:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```
Unauthenticated responses that are denied permission will result in an HTTP
401 Unauthorized response with an appropriate WWW-Authenticate header.
For example:
```
WWW-Authenticate: Token
```
# Request and Response Body

Request and response bodies are all in JSON format unless specified.

# Endpoints

## Shares

Base URI: /api/v1/shares/

### Endpoints

- **list**

    Get a list of shares based on the provided names/IDs. Returns all shares if
    neither names nor IDs are provided.


    Method: GET

    The response is evaluated at an OR basis, so if both name and id are
    provided, any share with name in the list OR id in the list are 
    returned.

    Request Body:

    | Name | Required | Type         | Description             |
    | ---- | -------- | ------------ | ----------------------- |
    | name | No       | List[string] | List of names of shares |
    | id   | No       | List[int]    | List of ids of shares   |

    Responses:

    | Name        | Code | Type      | Description                             |
    | ----------- | ---- | --------- | --------------------------------------- |
    | OK          | 200  | JSON List | A list of found shares, could be empty. |
    | Bad Request | 400  | None      | There's an error with the request body  |

    Response Body:

    Response body contains a list of shares. Each share in the list has the
    following fields:

    | Name        | Type      | Description                                        |
    | ----------- | --------- | -------------------------------------------------- |
    | id          | int       | ID of the share                                    |
    | name        | string    | name of the share                                  |
    | created_at  | int       | Unix epoch of the creation time of the share       |
    | updated_at  | int       | Unix epoch of the latest updated time of the share |
    | description | string    | Description of the share                           |
    | users       | List[int] | List of user IDs of users in the share             |
    | expenses    | List[int] | List of expense IDs of expenses in the share       |
    | total       | float     | The total expense amount in this share             |

    Examples:

    `GET /api/v1/shares/list`

    ```json
    [
        {
            "id": 0,
            "name": "my share 0",
            "created_at": 1511136659,
            "updated_at": 1511233617,
            "description": "Sharing food",
            "users": [1, 22, 5787],
            "expenses": [0, 1, 3, 4],
            "total": 109.9
        },
        {
            "id": 1,
            "name": "my share 1",
            "created_at": 1511131637,
            "updated_at": 1534232611,
            "description": "Trip to Japan",
            "users": [0, 3, 8],
            "expenses": [2, 3, 5, 8],
            "total": 30000.0
        },
        ...
    ]
    ```

- **update**

    Update an existing share.

    Method: POST

    Parameters:

    One of `name` or `id` must be present

    | Name  | Required | Type   | Description                   |
    | ----  | -------- | ------ | ----------------------------- |
    | name  | No       | string | Name of share                 |
    | id    | No       | int    | ID of share                   |

    Request Body:

    | Name        | Required | Type      | Description              |
    | ----------- | -------- | --------- | ------------------------ |
    | name        | No       | string    | New name of the share    |
    | description | No       | string    | The new description      |
    | users       | No       | List[int] | New list of IDs of users |

    Responses:

    | Name        | Code | Type | Description                                                               |
    | ----------- | ---- | ---- | ------------------------------------------------------------------------- |
    | OK          | 200  | JSON | Successfully updated a share                                              |
    | Bad Request | 400  | JSON | Failed to update a share because the client did not provide an id or name |
    | Forbidden   | 403  | JSON | Failed to update share due to an error (for example: user not found)      |
    | Not Found   | 404  | JSON | Failed to update a share because the server could not find the id/name    |

    Response Body:

    | Name       | Type   | Description                                             |
    | ---------- | ------ | ------------------------------------------------------- |
    | success    | bool   | Boolean indicating success                              |
    | reason     | string | Failure reason                                          |
    | id         | int    | ID of the share updated                                 |
    | updated_at | int    | Unix epoch of the time of the last update for the share |

    Examples:

    `POST /api/v1/shares/update?name=my_share JSON={"name": "my_new_share"}`
    ```json
    {"success": true, "reason": null, "id": 0, "updated_at": 1511154371}
    ```

    `POST /api/v1/shares/update JSON={"description": "foo"}`
    ```json
    {"success": false, "reason": "did not provide a name nor an id", "id": null, "updated_at": null}
    ```

    `POST /api/v1/shares/update?id=0 JSON={"name": ""}`
    ```json
    {"success": false, "reason": "name cannot be empty", "id": null, "updated_at": null}
    ```

    `POST /api/v1/shares/update?name=foo JSON={"users": []}`
    ```json
    {"success": false, "reason": "cannot remove users from share when there are expenses related to the user", "id": null, "updated_at": null}
    ```

    `POST /api/v1/shares/update?name=does_not_exist JSON={"users": [1, 2, 9]}`
    ```json
    {"success": false, "reason": "name is not found", "id": null, "updated_at": null}
    ```

- **delete**

    Delete an existing share, this also deletes ALL expenses in that share.

    Method: DELETE

    Parameters:
    One of `name` or `id` must be present.

    | Name  | Required | Type   | Description                   |
    | ----  | -------- | ------ | ----------------------------- |
    | name  | No       | string | Name of share                 |
    | id    | No       | int    | ID of share                   |

    Responses:

    | Name        | Code | Type | Description                                                               |
    | ----------- | ---- | ---- | ------------------------------------------------------------------------- |
    | OK          | 200  | JSON | Successfully deleted a share                                              |
    | Bad Request | 400  | JSON | Failed to delete a share because the client did not provide an id or name |
    | Not Found   | 404  | JSON | Failed to delete a share because the server could not find the id/name    |

    Response Body:

    | Name       | Type      | Description                                             |
    | ---------- | --------- | ------------------------------------------------------- |
    | success    | bool      | Boolean indicating success                              |
    | reason     | string    | Failure reason                                          |
    | id         | int       | ID of the share updated                                 |
    | expenses   | List[int] | List of IDs of expenses that also got deleted           |

    Examples:

    `DELETE /api/v1/shares/delete?name=my_name`

    ```json
    {"success": true, "reason": null, "id": 0, "expenses": [0, 1, 3, 8]}
    ```

    `DELETE /api/v1/shares/delete`
    
    ```json
    {"success": false, "reason": "did not provide a name nor an id", "id": null, "expenses": null}
    ```

    `DELETE /api/v1/shares/delete?id=99`
    
    ```json
    {"success": false, "reason": "id is not found", "id": null, "expenses": null}
    ```

------------------------------------------

## Users

Base URI: /api/v1/users/

### Endpoints

- **list**

    Get a list of users based on given request body. If no request body is
    given, this returns all users.

    Method: Get

    The response is evaluated at an OR basis, so if multiple fields are
    provided in the request body, any user matching any of the fields area
    returned.

    Request Body:

    | Name    | Required | Type         | Description                             |
    | ------- | -------- | ------------ | --------------------------------------- |
    | name    | No       | List[string] | List of user names                      |
    | id      | No       | List[int]    | List of user IDs                        |
    | share   | No       | List[int]    | List of share IDs that the user is in   |
    | expense | No       | List[int]    | List of expense IDs that the user is in |

    Responses:

    | Name        | Code | Type      | Description                             |
    | ----------- | ---- | --------- | --------------------------------------- |
    | OK          | 200  | JSON List | A list of found users, could be empty   |
    | Bad Request | 400  | None      | There's an error with the request body  |

    Response Body:

    Response body contains a list of users. Each user in the list has the
    following fields:

    | Name        | Type               | Description                                       |
    | ----------- | ------------------ | ------------------------------------------------- |
    | id          | int                | ID of the user                                    |
    | name        | string             | name of the user                                  |
    | created_at  | int                | Unix epoch of the creation time of the user       |
    | updated_at  | int                | Unix epoch of the latest updated time of the user |
    | shares      | List[int]          | List of share IDs of the shares the user is in    |
    | expenses    | List[int]          | List of expense IDs of expenses the user is in    |
    | balance     | map[string: float] | A mapping of user ID and balance amount.          |
    
    Note about the balance field:

    Because JSON does not allow int keys, the user ID is a string. 

    A positive balance means the mapped user owns the current user money.

    A negative balance means the current user owns the mapped user money.


    Example:

    `GET /api/v1/users/list JSON={"share": [0], "name": ["Charlie"]}`
    ```json
    [
        {
            "id": 1,
            "name": "Alice",
            "created_at": 1511136613,
            "updated_at": 1511136613,
            "shares": [0, 1],
            "expenses": [0, 1, 3, 4, 8],
            "balance": {"22": 3.0, "5787": -8.7}
        },
        {
            "id": 22,
            "name": "Bob",
            "created_at": 1511136621,
            "updated_at": 1511930393,
            "shares": [0],
            "expenses": [0, 1, 3],
            "balance": {"1": -3.0}
        },
        {
            "id": 5787,
            "name": "Robert'); DROP TABLE users;",
            "created_at": 1511136601,
            "updated_at": 1511136601,
            "shares": [0, 1, 8],
            "expenses": [1, 3, 4, 12, 16],
            "balance": {"1": 8.7, "8": -120.2}
        },
        {
            "id": 8,
            "name": "Charlie",
            "created_at": 1511226621,
            "updated_at": 1511226621,
            "shares": [1, 2],
            "expenses": [4],
            "balance": {"5787": 120.2}
        }
    ]
    ```

- **update**

    Update an existing user.

    Method: POST

    Parameters:

    One of `name` or `id` must be present

    | Name  | Required | Type   | Description                   |
    | ----  | -------- | ------ | ----------------------------- |
    | name  | No       | string | Name of user                  |
    | id    | No       | int    | ID of user                    |

    Request Body:

    | Name  | Required | Type      | Description                   |
    | ----- | -------- | --------- | ----------------------------- |
    | name  | No       | string    | New name of the user          |
    | share | No       | List[int] | List of shares the user is in |

    Responses:

    | Name        | Code | Type | Description                                                               |
    | ----------- | ---- | ---- | ------------------------------------------------------------------------- |
    | OK          | 200  | JSON | Successfully updated a user                                               |
    | Bad Request | 400  | JSON | Failed to update a user because the client did not provide an id or name  |
    | Forbidden   | 403  | JSON | Failed to update a user due to an error (for example: empty name)         |
    | Not Found   | 404  | JSON | Failed to update a user because the server could not find the id/name     |

    Response Body:

    | Name       | Type   | Description                                             |
    | ---------- | ------ | ------------------------------------------------------- |
    | success    | bool   | Boolean indicating success                              |
    | reason     | string | Failure reason                                          |
    | id         | int    | ID of the user updated                                  |

    Examples:

    `POST /api/v1/users/update?id=0 JSON={"name": "Cat"}`
    ```json
    {"success": true, "reason": null, "id": 0}
    ```

    `POST /api/v1/users/update JSON={"name": "400"}`
    ```json
    {"success": false, "reason": "did not provide a name or ID", "id": null}
    ```

    `POST /api/v1/users/update?id=0 JSON={"name": ""}`
    ```json
    {"success": false, "reason": "name cannot be empty", "id": null}
    ```

    `POST /api/v1/users/update?name=404 JSON={"name": "foo"}`
    ```json
    {"success": false, "reason": "cannot find user with name 404", "id": null}
    ```
------------------------------------------

## Expenses
Base URI: /api/v1/expenses/

### Endpoint

- **list**

    Get a list of expenses based on given request body. If no request body is
    provided, this returns all expenses.

    Method: GET

    The response is evaluated at an OR basis, so if multiple fields are
    provided in the request body, any expense matching any of the fields area
    returned.

    Request Body:

    | Name     | Required | Type          | Description                              |
    | -------- | -------- | ------------- | ---------------------------------------- |
    | id       | No       | List[int]     | List of expense IDs                      |
    | share    | No       | List[int]     | List of share IDs that any expense is in |
    | user     | No       | List[int]     | List of user IDs that any expense has    |
    | resolved | No       | bool          | Wether the expense is resolved or not    |
    | time     | No       | List[int]     | A list of 2 integers specifying the time range. The first integer is the start of the time range and the second integer is the end of the time range. Time are represented in Unix epoch. |

    Responses:

    | Name        | Code | Type      | Description                               |
    | ----------- | ---- | --------- | ----------------------------------------- |
    | OK          | 200  | JSON List | A list of found expenses, could be empty. |
    | Bad Request | 400  | None      | There's an error with the request body    |

    Response Body:

    Response body contains a list of expenses. Each expense in the list has the
    following fields:

    | Name        | Type                | Description                                          |
    | ----------- | ------------------- | ---------------------------------------------------- |
    | id          | int                 | ID of the expense                                    |
    | created_at  | int                 | Unix epoch of the creation time of the expense       |
    | updated_at  | int                 | Unix epoch of the latest updated time of the expense |
    | description | string              | Description of the expense                           |
    | share       | int                 | The share the expense is in                          |
    | total       | float               | The total cost of this expense                       |
    | paid_by     | int                 | The user ID of who paid for this expense             |
    | paid_for    | map[string: string] | A mapping of user IDs and paid ratios                |
    | resolved    | bool                | Wether the expense is resolved or not                |

    Note about the paid_for field:

    Because JSON does not allow int keys, the user ID is a string.

    The ratio of the user that paid the expense can be included in the mapping.

    The ratios in the mapping are expressed in a fraction of form
    `numerator/denominator` to ensure that they sum up to 1.

    Examples:

    `GET /api/v1/expenses/list JSON={"time": [1400000000, 1500000000]}`
    ```json
    [
        {
            "id": 0,
            "created_at": 1408417253,
            "updated_at": 1408417253,
            "description": "Pizza",
            "share": 0,
            "total": 12.95,
            "paid_by": 1,
            "paid_for": {"1": "1/3", "5": "1/3", "7": "1/3"},
            "resolved": true
        },
        {
            "id": 7,
            "created_at": 1423145281,
            "updated_at": 1423145281,
            "description": "Plane tickets",
            "share": 1,
            "total": 3000,
            "paid_by": 8,
            "paid_for": {"8": "1/2", "21": "1/2"},
            "resolved": false
        },
        ...
    ]
    ```

- **create**

    Create a new expense.

    Method: POST

    Request Body:

    | Name        | Required | Type                | Description                                          |
    | ----------- | -------- | ------------------- | ---------------------------------------------------- |
    | description | No       | string              | Description of the expense                           |
    | share       | Yes      | int                 | The share the expense is in                          |
    | total       | Yes      | float               | The total cost of this expense                       |
    | paid_by     | Yes      | int                 | The user ID of who paid for this expense             |
    | paid_for    | Yes      | map[string: string] | A mapping of user IDs and paid ratios                |
    | resolved    | No       | bool                | Wether this expense is resolved or not, if not provided, defaults to false |

    Note about the paid_for field:

    The ratios in the mapping are expressed in a fraction of form
    `numerator/denominator` to ensure that they sum up to 1.

    Responses:

    | Name        | Code | Type | Description                                      |
    | ----------- | ---- | ---- | ------------------------------------------------ |
    | OK          | 200  | JSON | Successfully created a new expense               |
    | Bad Request | 400  | JSON | Failed to create a new share because of an error |

    Response Body:

    | Name       | Type   | Description                                    |
    | ---------- | ------ | ---------------------------------------------- |
    | success    | bool   | Boolean indicating success                     |
    | reason     | string | Failure reason                                 |
    | id         | int    | ID of expense created                          |
    | created_at | int    | Unix epoch of the creation time of the expense |

    Examples:

    `POST /api/v1/expenses/create JSON={"share": 1, "total": 10, "paid_by": 3, "paid_for": {"7": "1/1"}}`
    ```json
    {"success": true, "reason": null, id: 198, "created_at": 1511391924}
    ```

    `POST /api/v1/expenses/create JSON={"share": 28, "total": 178, "paid_by": 6, "paid_for": {"6": "1/2"}}`
    ```json
    {"success": false, "reason": "paid_for ratio does not sum up to 1", id: null, "created_at": null}
    ```

- **update**

    Update an existing expense.

    Method: POST

    Parameters:

    | Name | Required | Type   | Description       |
    | ---- | -------- | ------ | ----------------- |
    | id   | Yes      | int    | ID of the expense |

    Request Body:

    | Name        | Required | Type                | Description                              |
    | ----------- | -------- | ------------------- | ---------------------------------------- |
    | description | No       | string              | Description of the expense               |
    | share       | No       | int                 | The ID of share the expense is in        |
    | total       | No       | float               | The total cost of this expense           |
    | paid_by     | No       | int                 | The user ID of who paid for this expense |
    | paid_for    | No       | map[string: string] | A mapping of user IDs and paid ratios    |
    | resolved    | No       | bool                | Wether the expense is resolved or not    |


    Responses:

    | Name        | Code | Type | Description                                                                     |
    | ----------- | ---- | ---- | ------------------------------------------------------------------------------- |
    | OK          | 200  | JSON | Successfully updated an expense                                                 |
    | Bad Request | 400  | JSON | Failed to update an expense because the client did not provide an id            |
    | Forbidden   | 403  | JSON | Failed to update an expense due to an error (for example: share does not exist) |
    | Not Found   | 404  | JSON | Failed to update an expense because the server could not find the id            |

    Response Body:

    | Name       | Type   | Description                                       |
    | ---------- | ------ | ------------------------------------------------- |
    | success    | bool   | Boolean indicating success                        |
    | reason     | string | Failure reason                                    |
    | updated_at | int    | Unix epoch of the last update time of the expense |

    Examples:

    `POST /api/v1/expenses/update?id=0 JSON={"total": 300.0}`
    ```json
    {"success": true, "reason": null, "updated_at": 1511409056}
    ```

    `POST /api/v1/expenses/update JSON={"description": "baka"}`
    ```json
    {"success": false, "reason": "did not provide an ID", "updated_at": null}
    ```

    `POST /api/v1/expenses/update?id=3 JSON={"share": 7}`
    ```json
    {"success": false, "reason": "user with ID 3 is not in share with ID 7", "updated_at": null}
    ```

    `POST /api/v1/expenses/update?id=99 JSON={"paid_for": {"1": "1/2", "3": "1/2"}}`
    ```json
    {"success": false, "reason": "cannot find expense with ID 99", "updated_at": null}
    ```

- **resolve**

    Mark a list of expenses as resolved.

    If one of the expenses failed to be resolved, none of the expenses will be
    resolved.

    Method: POST

    Parameters:

    | Name | Required | Type      | Description                           |
    | ---- | -------- | --------- | ------------------------------------- |
    | id   | Yes      | List[int] | A comma separated list of expense IDs |

    Response:

    | Name        | Code | Type | Description                                                                     |
    | ----------- | ---- | ---- | ---------------------------------- |
    | OK          | 200  | None | Successfully resolved the expenses |
    | Bad Request | 400  | None | Failed to resolve the expenses     |

    Examples:

    `POST /api/v1/expenses/resolve?id=1,2,100,12`

    `200`

    `POST /api/v1/expenses/resolve?id=0`

    `200`

- **delete**

    Delete a list of expenses

    If one of the expenses failed to be deleted, none of the expenses will be
    deleted.

    Method: DELETE

    Parameters:

    | Name | Required | Type      | Description                           |
    | ---- | -------- | --------- | ------------------------------------- |
    | id   | Yes      | List[int] | A comma separated list of expense IDs |

    Response:

    | Name        | Code | Type | Description                                                                     |
    | ----------- | ---- | ---- | --------------------------------- |
    | OK          | 200  | None | Successfully deleted the expenses |
    | Bad Request | 400  | None | Failed to delete the expenses     |

    Examples:

    `DELETE /api/v1/expenses/delete?id=1,2,100,12`

    `200`

    `DELETE /api/v1/expenses/delete?id=12`

    `400`