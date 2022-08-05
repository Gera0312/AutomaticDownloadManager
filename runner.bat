CALL docker build -t manager_image .
CALL docker run --name manager_image --volume /Progetti:/usr/directory/Python