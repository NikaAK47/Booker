FROM python:3.9
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py app.py
COPY models.py models.py
COPY templates/ templates/
EXPOSE 5000
CMD ["python", "app.py"]