FROM python:3.10.4-slim

COPY . .
RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

ENTRYPOINT ["python3"]
CMD ["app.py"]
