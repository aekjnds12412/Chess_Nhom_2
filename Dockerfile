FROM python:3.12-slim
WORKDIR /app
COPY vendor /app/vendor
COPY chessnet /app/chessnet
COPY app.py /app/app.py
EXPOSE 8765/tcp 9999/udp
VOLUME ["/app/data"]
CMD ["python", "app.py", "--server"]
