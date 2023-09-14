FROM ubuntu:latest
LABEL authors="garry"

ENTRYPOINT ["top", "-b"]