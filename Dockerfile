FROM rsbyrne/everest
MAINTAINER https://github.com/rsbyrne/

USER root

RUN pip3 install -U --no-cache-dir \
  html5lib \
  lxml \
  adjustText

WORKDIR $MOUNTDIR
USER $MASTERUSER
