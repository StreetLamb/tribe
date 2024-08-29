# Running Tribe on Your Local Machine

This guide will help you set up and run Tribe on your local machine as quickly as possible.

## Requirements

- [Docker](https://docs.docker.com/desktop/) installed on your machine. Check that docker is installed by running:

  ```bash
  docker --version
  docker-compose --version
  ```

## Step-by-Step Setup

### 1. Clone the Repository

Clone the Tribe repository to your local machine and navigate to the project directory:
```bash
git clone https://github.com/StreetLamb/tribe.git tribe
cd tribe
```

### 2. Set Up Environment Variables

Copy the example environment variables file into a new `.env` file:
```bash
cp .env.example .env
```

Update the `.env` file with your custom configurations. At a minimum, you should change the following values:
- `USERNAME`
- `HASHED_PASSWORD` (Continue reading to learn how to generate it)
- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`
- `OPENAI_API_KEY` (Choose your preferred model provider)
- `FLOWER_BASIC_AUTH`

For variables with a default value of `changethis`, generate secure values using the following command:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Creating Traefik Environment Variables

Create the username for HTTP Basic Auth, e.g.:
```bash
export USERNAME=admin

echo $USERNAME
```

To generate `HASHED_PASSWORD`, create an environment variable with the password for HTTP Basic Auth, e.g.:
```bash
export PASSWORD=changethis
```

Next, use openssl to generate the "hashed" version of the password for HTTP Basic Auth and store it in an environment variable:
```bash
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)

echo $HASHED_PASSWORD
```

Copy the printed value into the `.env` file.

### 4. Build and Run the Docker Containers

Use Docker Compose to build the images and start the containers:
```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up
```

## Accessing the Services

Once the containers are running, you can access various services through the following URLs:

- **Frontend**: [http://localhost/](http://localhost/)
- **Backend API Documentation**: [http://localhost/docs/](http://localhost/docs/)
- **Backend API Base URL**: [http://localhost/api/](http://localhost/api/)
- **Qdrant Dashboard**: [http://qdrant.localhost/dashboard](http://qdrant.localhost/dashboard)
- **Adminer**: [http://adminer.localhost/](http://adminer.localhost/)
- **Traefik UI**: [http://traefik.localhost/](http://traefik.localhost/)
- **Flower**: [http://flower.localhost/](http://flower.localhost/)

## Troubleshooting
- **Out of Memory**: If you are getting the `Worker (pid:14) was sent SIGKILL! Perhaps out of memory?` error, this is due to the number of processes started for the backend container consuming more memory than what is available. You can fix this by decreasing `MAX_WORKERS` in your `.env` file.
- **Unable to login to Traefik Dashboard**: Ensure that username and password is correct. If you are using zsh, `USERNAME` environment variable corresponds to the real user ID of the shell process, so you should use your user ID as the username.
- **Cannot login to Adminer**: Set 'System' to `PostgreSQL` and set the 'server' field should be `db`. The other fields should follow the values in your `.env` file.

## Known issues
- **Password does not match for user "postgres-tribe"**: https://github.com/StreetLamb/tribe/issues/84#issuecomment-2250219701
