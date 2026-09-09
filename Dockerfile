FROM python:3.11-slim

WORKDIR /workspace
COPY src ./src
COPY config.json instruction.md eval.py solve.sh ./
RUN chmod +x solve.sh

CMD ["python3", "eval.py"]
