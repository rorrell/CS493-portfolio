# CS493-portfolio

This is a school project that has a web page at the root level ('/') that allows you to authenticate via Google OAuth and then creates a user in Google Datastore whose ID is the sub property of the decoded JWT.  The JWT is shown to you after you authenticate, and then you use that as a bearer token for the API.

# API
All requests and responses must be in JSON.  All endpoints require the bearer token described above except for the /users endpoint.
## POST /aquariums
### Request JSON Attributes
| Name | Description | Required? |
| :--- | :--- | :--- |
| name | Name of the aquarium, to differentiate it from similar aquariums. | Yes |
| waterType | E.g., "salt", "fresh", "brackish" | Yes |
| size | Aquarium size in gallons | Yes |
| material | E.g., "glass", "acrylic" | Yes |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :---| :--- |
| Success | 201 Created | The created aquarium will be owned by you |
| Failure | 400 Bad request | If the request is missing any of the required attributes, the aquarium is not created, and a 400 status code is returned. |
| Failure | 401 Unauthorized | If you are not authorized, the aquarium can't be assigned to you. |
| Failure | 403 Forbidden | If an aquarium with the privded name already exists, the aquarium is not created, and a 403 status code is returned. |
| Failure | 406 Not Acceptable | If the content type is not JSON, the aquarium is not created, and a 406 status code is returned. |
### Success Response Example
```
{
     "id": 123,
     "name": "Tank A",
     "waterType": "fresh",
     "size": 25,
     "material": "glass",
     "owner": {
          "id": "123948273433298",
          "name": "John Doe"
     },
     "fish": [],
     "self: "http://localhost:8080/aquariums/123"
}
```
## GET /aquariums/:aquarium_id
### Path Parameters
| Name | Description |
| :--- | :--- |
| aquarium_id | ID of the aquarium |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :---| :--- |
| Success | 200 OK | |
| Failure | 401 Unathorized | This aquarium is not owned by you |
| Failure | 404 Not Found | No aquarium with this aquarium_id exists |
### Success Response Example
```
{
     "id": 123,
     "name": "Tank A",
     "waterType": "fresh",
     "size": 25,
     "material": "glass",
     "owner": {
          "id": "123948273433298",
          "name": "John Doe"
     },
     "fish": [
          {
               "id": 345,
               "name": "Sparky",
               "species": "goldfish",
               "self": "http://localhost:8080/fish/345"
          }
     ],
     "self: "http://localhost:8080/aquariums/123"
}
```
## GET /aquariums
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :---| :--- |
| Success | 200 OK | Results are paginated (5 per page) with a link to the next page and property showing the total number of results.  Only those aquariums that are owned by you will be shown. |
### Success Response Example
```
{
     "aquariums": [
          {
               "id": 123,
               "name": "Tank A",
               "waterType": "fresh",
               "size": 25,
               "material": "glass",
               "owner": {
                    "id": "123948273433298",
                    "name": "John Doe"
               },
               "fish": [
                    {
                         "id": 345,
                         "name": "Sparky",
                         "species": "goldfish",
                         "self": "http://localhost:8080/fish/345"
                    }
               ],
               "self: "http://localhost:8080/aquariums/123"
          },
          {
               "id": 124,
               "name": "Tank B",
               "waterType": "fresh",
               "size": 5,
               "material": "acrylic",
               "owner": {
                    "id": "123948273433298",
                    "name": "John Doe"
               },
               "fish": [],
               "self: "http://localhost:8080/aquariums/124"    
          },
          {
               "id": 124,
               "name": "Tank C",
               "waterType": "brackish",
               "size": 40,
               "material": "acrylic",
               "owner": {
                    "id": "123948273433298",
                    "name": "John Doe"
               },
               "fish": [],
               "self: "http://localhost:8080/aquariums/124"    
          },
          {
               "id": 125,
               "name": "Tank C",
               "waterType": "salt",
               "size": 50,
               "material": "glass",
               "owner": {
                    "id": "123948273433298",
                    "name": "John Doe"
               },
               "fish": [],
               "self: "http://localhost:8080/aquariums/125"    
          },
          {
               "id": 126,
               "name": "Tank D",
               "waterType": "fresh",
               "size": 10,
               "material": "glass",
               "owner": {
                    "id": "123948273433298",
                    "name": "John Doe"
               },
               "fish": [],
               "self: "http://localhost:8080/aquariums/126"    
          },
          {
               "id": 127,
               "name": "Tank E",
               "waterType": "salt",
               "size": 20,
               "material": "acrylic",
               "owner": {
                    "id": "123948273433298",
                    "name": "John Doe"
               },
               "fish": [],
               "self: "http://localhost:8080/aquariums/127"    
          },
     ],
     "next": "http://localhost:8080/aquariums?cursor= CikSI2oNc35odzQtb3JyZWxscnISCxIFQm9hdHMYgICA2NqZhAoMGAAgAA==",
     "totalItems": 6
}
```
## PATCH /aquariums/:aquarium_id
### Path Parameters
| Name | Description |
| :--- | :--- |
| aquarium_id | ID of the aquarium |
### Request JSON Attributes
| Name | Description | Required? |
| :--- | :---| :--- |
| name | Name of the aquarium, to differentiate it from similar aquariums. | No |
| waterType | E.g., "salt", "fresh", "brackish" | No |
| size | Aquarium size in gallons | No |
| material | E.g., "glass", "acrylic" | No |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :---| :--- |
| Success | 200 OK | |
| Failure | 400 Unauthorized | If the aquarium is not owned by you, the change is not made, and 401 status code is returned. |
| Failure | 403 Forbidden | If the name is being changed and there is already an aquarium with the new name, the change is not made, and a 403 status code is returned. |
| Failure | 404 Not Found | If no aquarium with this ID exists, a 404 status code is returned. |
| Failure | 406 Not Acceptable | If the content type is not JSON, the change is not made, and a 406 status code is returned.
## Success Response Example
```
{
     "id": 123,
     "name": "Tank A",
     "waterType": "fresh",
     "size": 25,
     "material": "glass",
     "owner": {
          "id": "123948273433298",
          "name": "John Doe"
     },
     "fish": [
          {
               "id": 345,
               "name": "Sparky",
               "species": "goldfish",
               "self": "http://localhost:8080/fish/345"
          }
     ],
     "self: "http://localhost:8080/aquariums/123"
}
```
## PUT aquariums/:aquarium_id
### Path Parameters
| Name | Description |
| :--- | :---|
| aquarium_id | ID of the aquarium |
### Request JSON Attributes
| Name | Description | Required? |
| :--- | :---| :--- |
| name | Name of the aquarium, to differentiate it from similar aquariums. | Yes |
| waterType | E.g., "salt", "fresh", "brackish" | Yes |
| size | Aquarium size in gallons | Yes |
| material | E.g., "glass", "acrylic" | Yes |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 200 OK | |
| Failure | 400 Bad Request | If the aquarium is missing any of its attributes, the change is not made, and a 400 status code is returned. |
| Failure | 401 Unauthorized | If the aquarium is not owned by you, the change is not made, and 401 status code is returned |
| Failure | 403 Forbidden | If the name is being changed and there is already an aquarium with the new name, the change is not made, and 403 status code is returned. |
| Failure | 406 Not Acceptabled | If the content type is not JSON, the change is not made, and a 406 status code is returned. |
## Success Response Example
```
{
     "id": 123,
     "name": "Tank A",
     "waterType": "fresh",
     "size": 25,
     "material": "glass",
     "owner": {
          "id": "123948273433298",
          "name": "John Doe"
     },
     "fish": [
          {
               "id": 345,
               "name": "Sparky",
               "species": "goldfish",
               "self": "http://localhost:8080/fish/345"
          }
     ],
     "self: "http://localhost:8080/aquariums/123"
}
```
## DELETE /aquariums/:aquarium_id
### Path Parameters
| Name | Description |
| :--- | :--- |
| aquarium_id | ID of the aquarium |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 204 No Content | |
| Failure | 401 Unauthorized | If the aquarium is not owned by you, it is not deleted, and a 401 status code is returned. |
| Failure | 404 Not Found | No aquarium with this aquarium_id exists. |
## PUT /aquariums/:aquarium_id/fish/:fish_id
Adds a fish to an aquarium
### Path Parameters
| Name | Description |
| :--- | :--- |
| aquarium_id | ID of the aquarium |
| fish_id | ID of the fish |
**Note: Set Content-Length to 0 in your request when calling out to this endpoint**
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 204 No Content | | 
| Failure | 401 Unauthorized | Either the specified fish or the specified aquarium is not owned by you. |
| Failure | 403 Forbidden | The specified fish is already in another aquarium. |
| Failure | 404 Not Found | The specified aquarium and/or fish does not exist. |
## DELETE /aquariums/:aquarium_id/fish/:fish_id
Removes a fish from an aquarium
### Path Parameters
| Name | Description |
| :--- | :--- |
| aquarium_id | ID of the aquarium |
**Note: Set Content-Length to 0 in your request when calling out to this endpoint**
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 204 No Content | |
| Failure | 401 Unauthorized | Either the specified fish or the specified aquarium is not owned by you. |
| Failure | 404 Not Found | No fish with this fish_id is in an aquarium with this aquarium_id.  This could be because no aquarium with this aquarium_id exists, or because no fish with this fish_id exists, or if both do exist, the fish with this fish_id is not in the aquarium with this aquarium_id. |
## POST /fish
### Request JSON Attributes
| Name | Description | Required? |
| :--- | :--- | :--- |
| name | Name of the fish, to differentiate if from similar fish | Yes |
| species | E.g., "goldfish", "guppy", etc. | Yes |
| gender | E.g., "male", "female" | Yes |
| color | The color or colors of the fish | Yes |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 201 Created | The created fish is owned by you. |
| Failure | 400 Bad Request | If the request is missing any of the required attributes, the fish is not created, and a 400 status code is returned. |
| Failure | 401 Unauthorized | If you are not authorized, the fish can't be assigned to you. |
| Failure | 403 Forbidden | If a fish with the provided name already exists, the fish is not created, and a 403 status code is returned. |
| Failure | 406 Not Acceptable | If the content type is not JSON, the fish is not created, and a 406 status code is returned. |
### Success Response Example
```
{
     "id": 123,
     "name": "Ginny",
     "species: "guppy",
     "gender": "female",
     "color": "white and gray",
     "owner": {
          "id": "1293847234",
          "name": "John Doe"
     },
     "self": http://localhost:8080/fish/123"
}
```
## GET /fish/:fish_id
### Path Parameters
| Name | Description |
| :--- | :--- |
| fish_id | ID of the fish |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 200 OK | |
| Failure | 401 Unauthorized | The specified fish is not owned by you. |
| Failure | 404 Not Found | No fish with this fish_id exists. |
### Success Response Example
```
{
     "id": 123,
     "name": "Ginny",
     "species: "guppy",
     "gender": "female",
     "color": "white and gray",
     "aquarium" : {
          "id": 124,
          "name": "Tank B",
          "self": "http://localhost:8080/aquariums/124"
     }
     "owner": {
          "id": "1293847234",
          "name": "John Doe"
     },
     "self": "http://localhost:8080/fish/123"
}
```
## GET /fish
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 200 OK | Results are paginated (5 per page) with a link to the next page and property showing the total number of results.  Only those fish that are owned by you will be shown. |
### Success Response Example
```
{
     "fish": [
          {
               "id": 123,
               "name": "Ginny",
               "species": "guppy",
               "gender": "female",
               "color": "white and gray",
               "aquarium": {
                    "id": 124,
                    "name": "Tank B",
                    "self": "http://localhost:8080/aquariums/124"
               },
               "owner": {
                    "id": "1293847234",
                    "name": "John Doe"
               },
               "self": "http://localhost:8080/fish/123"
          },
          {
               "id": 124,
               "name": "Geoff",
               "species": "guppy",
               "gender": "male",
               "color": "red and yellow",
               "owner": {
                    "id": "1293847234",
                    "name": "John Doe"
               },
               "self": "http://localhost:8080/fish/124"
          },
          {
               "id": 125,
               "name": "Genny",
               "species": "guppy",
               "gender": "female",
               "color": "white and gray",
               "owner": {
                    "id": "1293847234",
                    "name": "John Doe"
               },
               "self": "http://localhost:8080/fish/125"
          },
          {
               "id": 126,
               "name": "George",
               "species": "guppy",
               "gender": "male",
               "color": "green and blue",
               "owner": {
                    "id": "1293847234",
                    "name": "John Doe"
               },
               "self": "http://localhost:8080/fish/126"
          },
          {
               "id": 127,
               "name": "Greg",
               "species": "guppy",
               "gender": "male",
               "color": "blue and white",
               "owner": {
                    "id": "1293847234",
                    "name": "John Doe"
               },
               "self": "http://localhost:8080/fish/127"
          }
     ],
     "next": "http://localhost:8080/fish?cursor= CikSI2oNc35odzQtb3JyZWxscnISCxIFQm9hdHMYgICA2NqZhAoMGAAgAA==",
     "totalItems": 6
}
```
## PATCH /fish/:fish_id
### Path Parameters
| Name | Description |
| :--- | :--- |
| fish_id | ID of the fish |
### Request JSON Attributes
| Name | Description | Required? |
| :--- | :--- | :--- |
| name | Name of the fish, to differentiate if from similar fish. | No |
| species | E.g., "goldfish", "guppy" | No |
| gender | E.g., "male", "female" | No |
| color | The color or colors of the fish. | No |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 200 OK | | 
| Failure | 401 Unauthorized | If the fish is not owned by you, the change is not made, and 401 status code is returned. |
| Failure | 403 Forbidden | If the name is being changed and there is already a fish with the new name, the change is not made, and a 403 status code is returned. |
| Failure | 404 Not Found | If no fish with this ID exists, a 404 status code is returned. |
| Failure | 406 NOt Acceptable | If the content type is not JSON, the change is not made, and a 406 status code is returned. |
### Success Response Example
```
{
     "id": 123,
     "name": "Ginny",
     "species: "guppy",
     "gender": "female",
     "color": "white and gray",
     "aquarium" : {
          "id": 124,
          "name": "Tank B",
          "self": "http://localhost:8080/aquariums/124"
     }
     "owner": {
          "id": "1293847234",
          "name": "John Doe"
     },
     "self": "http://localhost:8080/fish/123"
}
```
## PUT fish/:fish_id
### Path Parameters
| Name | Description |
| :--- | :--- |
| fish_id | ID of the fish |
### Request JSON Attributes
| Name | Description | Required? |
| :--- | :--- | :--- |
| name | Name of the fish, to differentiate if from similar fish. | Yes |
| species | E.g., "goldfish", "guppy" | Yes |
| gender | E.g., "male", "female" | Yes |
| color | The color or colors of the fish. | Yes |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 200 OK | | 
| Failure | 400 Bad Request | If the fish is missing any of its required attributes, the change is not made, and 400 status code is returned. |
| Failure | 401 Unauthorized | If the fish is not owned by you, the change is not made, and 401 status code is returned. |
| Failure | 403 Forbidden | If the name is being changed and there is already a fish with the new name, the change is not made, and a 403 status code is returned. |
| Failure | 404 Not Found | If no fish with this ID exists, a 404 status code is returned. |
| Failure | 406 NOt Acceptable | If the content type is not JSON, the change is not made, and a 406 status code is returned. |
### Success Response Example
```
{
     "id": 123,
     "name": "Ginny",
     "species: "guppy",
     "gender": "female",
     "color": "white and gray",
     "aquarium" : {
          "id": 124,
          "name": "Tank B",
          "self": "http://localhost:8080/aquariums/124"
     }
     "owner": {
          "id": "1293847234",
          "name": "John Doe"
     },
     "self": "http://localhost:8080/fish/123"
}
```
## DELETE /fish/:fish_id
### Path Parameters
| Name | Description |
| :--- | :--- |
| fish_id | ID of the fish |
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 204 No Content | |
| Failure | 401 Unauthorized | If the fish is not owned by you, it is not deleted, and a 401 status code is returned. |
| Failure | 404 Not Found | No fish with this fish_id exists. |
## GET /users
### Response Statuses
| Outcome | Status Code | Notes |
| :--- | :--- | :--- |
| Success | 200 OK | |
### Success Response Example
```
[
     {
          "id": "23982342897324",
          "name": "John Doe"
     },
     {
          "id": "12398423489723",
          "name": "Jane Doe"
     }
]
```
