FROM harbor.bchen.xyz/library/python-36-centos7:latest
MAINTAINER bo_bo0425@126.com
COPY flask-template.tar ./
RUN tar -zxvf flask-template.tar
RUN rm -f flask-template.tar
RUN pip3 install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
EXPOSE  5000
ENV ENV=DEV
CMD python3 cli.py runserver -w 5
