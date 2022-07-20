FROM rsbyrne/everest
MAINTAINER https://github.com/rsbyrne/

USER root

WORKDIR $MOUNTDIR
USER $MASTERUSER
