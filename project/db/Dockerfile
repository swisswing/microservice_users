# base image
FROM postgres:11.2-alpine

# run create.sql on init
# Here, we extend the official Postgres image (again, an Alpine-based image) 
# by adding a SQL file to the "docker-entrypoint-initdb.d" directory in the container, 
# which will execute on init.
ADD create.sql /docker-entrypoint-initdb.d