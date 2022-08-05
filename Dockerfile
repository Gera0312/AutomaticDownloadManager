FROM python:3

WORKDIR /usr/src/manager


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python3", "AutomatedManager.pyw" ]