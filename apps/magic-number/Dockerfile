FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target /deps -r requirements.txt

FROM gcr.io/distroless/python3-debian13:nonroot
WORKDIR /app
ENV PYTHONPATH=/deps \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
COPY --from=build /deps /deps
COPY app.py .
COPY static/ static/
EXPOSE 5000
ENTRYPOINT ["/usr/bin/python"]
CMD ["app.py"]