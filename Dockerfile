FROM python:3.11.4-slim-buster


# Fayllarni joylashtirish uchun
WORKDIR /usr/src/app  

# _pycache_ keshlarni saqlamaslik uchun
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update && apt-get install -y netcat


RUN pip install --upgrade




COPY ./requirements.txt .

RUN pip install -r requirements.txt

# entrypoint tanib olishi uchun
COPY ./entrypoint.sh .   
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# appni ichidagi hamma faylni dockerga joylash uchun
COPY . .  

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]