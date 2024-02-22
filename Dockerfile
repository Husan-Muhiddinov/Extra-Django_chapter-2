FROM python:3.11.4-slim-buster


# Fayllarni joylashtirish uchun
WORKDIR /usr/src/app  

# _pycache_ keshlarni saqlamaslik uchun
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt

# appni ichidagi hamma faylni dockerga joylash uchun
COPY . .  