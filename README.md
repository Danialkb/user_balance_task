## !!! You should first deploy Quiz Task
## Deploy instructions (LOCAL). Execute from root directory of project (user_balance_task)
> docker compose -f deploy/docker-compose.yml up --build -d


Swagger UI doc can be accessed on 
> 0.0.0.0:8001/docs


Run tests
> docker exec -it quiz_backend uv run pytest -vvv 

# Endpoint description
Headers required:
X-User-ID - UUID

## /api/v1/user_balance
Get balance for specific user provided with X-User-ID header. Raises 404 if balance not found


## /api/v1/user_balance/add
Adds balance for specific user account, if account doesn't exists it will be automatically created.
Update transaction will be written in user_balance_transactions table.
