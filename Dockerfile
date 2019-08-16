FROM surnet/alpine-wkhtmltopdf:3.9-0.12.5-small
RUN apk add --update py-pip
RUN mkdir -p /var/usc-server
COPY ./ /var/usc-server
RUN pip install -r /var/usc-server/requirements.txt

ENTRYPOINT python /var/usc-server/app.py
EXPOSE 80