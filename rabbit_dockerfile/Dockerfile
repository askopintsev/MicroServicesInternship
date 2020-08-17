# Base Image
FROM rabbitmq:3.6.6-management
ADD /rabbit_dockerfile/rabbitmq.config /etc/rabbitmq/
ADD /rabbit_dockerfile/definitions.json /etc/rabbitmq/
RUN chown rabbitmq:rabbitmq /etc/rabbitmq/rabbitmq.config /etc/rabbitmq/definitions.json
CMD ["rabbitmq-server"]