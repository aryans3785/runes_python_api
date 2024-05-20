# Rune API

This project provides a RESTful API for managing runes. The following features have been implemented:

1. **Migrated from `pymongo` to `mongoengine`**: 
   - All database operations now use `mongoengine`, an Object-Document Mapper (ODM) for MongoDB, instead of raw `pymongo` queries.

2. **Access Limit to API**:
   - Rate limiting has been implemented using `flask-limiter`.
   - Each user is limited to 5 requests per minute to the `/runes` endpoint.
   - Exceeding this limit will return a 429 status code with a "Too Many Requests" error.

3. **Pagination and Search**:
   - The `/runes` endpoint supports pagination.
   - Clients can specify the `page` and `limit` parameters to paginate results.
   - Clients can also use the `search` parameter to filter results based on the `SpacedRune` field.

4. **API Key Authentication**:
   - API keys are used to authenticate users.
   - Requests to the `/runes` endpoint must include a valid API key.

5. **Redis Implementation**:
   - Redis is used for caching and storing rate limiting data.

6. **Improved Error Handling**:
   - Comprehensive error handling has been implemented to ensure clear and consistent error messages.
   - Errors are returned with appropriate status codes and messages.

7. **Swagger Documentation**:
   - Swagger has been implemented for API documentation.
   - The API documentation can be accessed at `/swagger-ui`.
   - curl "http://localhost:5000/docs" in your browser to access swagger.

## Endpoints

### `/runes` [POST]

#### Description
Get a list of runes with pagination and search capabilities.

#### Parameters

- `page` (int, optional): The page number to retrieve. Default is 1.
- `limit` (int, optional): The number of items per page. Default is 10.
- `search` (string, optional): A search query to filter runes by the `SpacedRune` field.

#### Example Request

```bash
curl -X POST "http://localhost:5000/runes" \
    -H "Content-Type: application/json" \
    -H "x-api-key: YOUR_API_KEY" \
    -d '{
        "page": 1,
        "limit": 10,
        "search": "SCAM"
    }'
