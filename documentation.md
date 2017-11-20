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

# Endpoints

## Shares

Base URI: /v1/shares/

### Endpoints

- **list**

    Get a list of shares based on the name and/or ID. Returns all the shares if
    neither of name nor id is provided.

    Method: GET

    Parameters:

    | Name  | Required | Type   | Description                   |
    | ----  | -------- | ------ | ----------------------------- |
    | name  | No       | string | Name of share                 |
    | id    | No       | int    | ID of share                   |

    Responses:

    | Name | Code | Type      | Description                             |
    | ---- | ---- | --------- | --------------------------------------- |
    | OK   | 200  | JSON List | A list of found shares, could be empty. |

    Response Body:

    Response body contains a list of shares. Each share in the list has those
    fields:

    | Name        | Type      | Description                                        |
    | ----------- | --------- | -------------------------------------------------- |
    | id          | int       | ID of the share                                    |
    | name        | string    | name of the share                                  |
    | created_at  | int       | Unix epoch of the creation time of the share       |
    | updated_at  | int       | Unix epoch of the latest updated time of the share |
    | description | string    | Description of the share                           |
    | users       | List[int] | List of user IDs of users in the share             |
    | expenses    | List[int] | List of expense IDs of expenses in the share       |
    | currency    | string    | Currency code used for this share                  |

    Example:

    `GET /v1/shares/list`

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
            "currency": "USD"
        },
        {
            "id": 1,
            "name": "my share 1",
            "created_at": 1511131637,
            "updated_at": 1534232611,
            "description": "Trip to Japan",
            "users": [0, 3, 8],
            "expenses": [2, 3, 5, 8],
            "currency": "JPY"
        },
        ...
    ]
    ```
- **create**

    Create a new share.

    Method: POST

    Request Body (JSON):

    | Name        | Required | Type   | Description                              |
    | ----------- | -------- | ------ | ---------------------------------------- |
    | name        | Yes      | string | Name of the new share                    |
    | description | No       | string | Description of the new share             |
    | currency    | Yes      | string | Currency code used for the share         |
    | users       | No       | list   | List of IDs of users to add to the share |

    Responses:

    | Name        | Code | Type | Description                                                                           |
    | ----------- | ---- | ---- | ------------------------------------------------------------------------------------- |
    | OK          | 200  | JSON | Successfully created a new share                                                      |
    | Bad Request | 400  | JSON | Failed to create a new share because the client did not provide name or currency code |
    | Forbidden   | 403  | JSON | Failed to create a new share due to an error (for example: duplicate names)           |

    Response Body:

    | Name       | Type   | Description                                          |
    | ---------- | ------ | ---------------------------------------------------- |
    | success    | bool   | Boolean indicating success                           |
    | reason     | string | Failure reason                                       |
    | id         | int    | ID of the share created                              |
    | created_at | int    | Unix epoch of the time of creation for the new share |


    Examples:

    `POST /v1/shares/create JSON={"name": "my_share", "currency": "CAD"}`
    ```json
    {"success": true, "reason": null, "id": 0, "created_at": 1511131637}
    ```

    `POST /v1/shares/create JSON={"name": "no currency"}`
    ```json
    {"success": false, "reason": "did not provide a currency code", "id": null, "created_at": null}
    ```

    `POST /v1/shares/create JSON={"name": "my_share", "currency": "USD"}`

    ```json
    {"success": false, "reason": "name already exists", "id": null, "created_at": null}
    ```

- **update**

    Update an existing share.

    Method: Post

    Parameters:

    One of `name` or `id` must be present

    | Name  | Required | Type   | Description                   |
    | ----  | -------- | ------ | ----------------------------- |
    | name  | No       | string | Name of share                 |
    | id    | No       | int    | ID of share                   |

    Request Body (JSON):

    | Name        | Required | Type   | Description                              |
    | ----------- | -------- | ------ | ---------------------------------------- |
    | name        | No       | string | New name of the share                    |
    | description | No       | string | The new description                      |
    | currency    | No       | string | The new currency code                    |
    | users       | No       | list   | New list of IDs of users                 |

    Responses:

    | Name        | Code | Type | Description                                                               |
    | ----------- | ---- | ---- | ------------------------------------------------------------------------- |
    | OK          | 200  | JSON | Successfully created a new share                                          |
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

    `POST /v1/shares/update?name=my_share JSON={"name": "my_new_share"}`
    ```json
    {"success": true, "reason": null, "id": 0, "updated_at": 1511154371}
    ```

    `POST /v1/shares/update JSON={"description": "foo"}`
    ```json
    {"success": false, "reason": "did not provide a name nor an id", "id": null, "updated_at": null}
    ```

    `POST /v1/shares/update?id=0 JSON={"name": ""}`
    ```json
    {"success": false, "reason": "name cannot be empty", "id": null, "updated_at": null}
    ```

    `POST /v1/shares/update?name=does_not_exist JSON={"users": [1, 2, 9]}`
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

    `DELETE /v1/shares/delete?name=my_name`

    ```json
    {"success": true, "reason": null, "id": 0, "expenses": [0, 1, 3, 8]}
    ```

    `DELETE /v1/shares/delete`
    
    ```json
    {"success": false, "reason": "did not provide a name nor an id", "id": null, "expenses": null}
    ```

    `DELETE /v1/shares/delete?id=99`
    
    ```json
    {"success": false, "reason": "id is not found", "id": null, "expenses": null}
    ```

------------------------------------------

## Users

Base URI: /v1/users/

### Endpoints

------------------------------------------

## Expenses
Base URI: /v1/expenses/

### Endpoints