HWOJ

DEMO: https://test.hw.io.vn/

![Home](Home.png)
![Problems](Problems.png)

# Installing the site

Requirements:
- mariadb
- uv (https://docs.astral.sh/uv/getting-started/installation)
- nodejs (https://nodejs.org/en/download)

## Create database and user

Install mariadb
```sh
$ apt update
$ apt install mariadb-server libmysqlclient-dev
```

Create database and user
```sh
$ sudo mysql
mariadb> CREATE DATABASE hwoj DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
mariadb> GRANT ALL PRIVILEGES ON hwoj.* TO 'hwoj'@'localhost' IDENTIFIED BY '<mariadb user password>';
mariadb> exit
```

[BACKEND](/R-backend.md)

[FRONTEND](/HWOJ-frontend/README.md)

[JUDGE](/R-judge.md)

[Authentication Bot](/CKTOJ_DISCORDBOT/README.md)