FROM python:3.13-slim

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app --home /app app

ENV HOME=/app
ENV TMPDIR=/tmp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# RUN python manage.py collectstatic --noinput

RUN chown -R app:app /app
USER app

CMD ["gunicorn", "my_project.wsgi:application", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/tmp"]