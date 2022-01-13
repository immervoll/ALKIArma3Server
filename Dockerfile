FROM debian:buster-slim

LABEL maintainer="ALKI Immervoll - https://github.com/immervoll"

RUN apt-get update \
    && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        python3 \
        lib32stdc++6 \
        lib32gcc1 \
        rename \
        wget \
        ca-certificates \
    && \
    apt-get remove --purge -y \
    && \
    apt-get clean autoclean \
    && \
    apt-get autoremove -y \
    && \
    rm /var/lib/apt/lists/* -r \
    && \
    mkdir -p /steamcmd \
        && cd /steamcmd \
        && wget -qO- 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz' | tar zxf -
RUN pip install beautifulsoup4

ENV ARMA_BINARY=./arma3server
ENV ARMA_CONFIG=main.cfg
ENV ARMA_PROFILE=main
ENV ARMA_WORLD=empty
ENV ARMA_LIMITFPS=1000
ENV HEADLESS_CLIENTS=0
ENV PORT=2302
ENV STEAM_BRANCH=public
ENV STEAM_BRANCH_PASSWORD=
ENV ARMA_DLC = ""
ENV STEAM_USER =""
ENV STEAM__PASSWORD = ""

EXPOSE 2302/udp
EXPOSE 2303/udp
EXPOSE 2304/udp
EXPOSE 2305/udp
EXPOSE 2306/udp

ADD launch.py /launch.py
COPY modlistToSteam /modlistToSteam

WORKDIR /arma3

VOLUME /steamcmd

STOPSIGNAL SIGINT

CMD ["python3","/launch.py"]
