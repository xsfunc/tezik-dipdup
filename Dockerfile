FROM dipdup/dipdup:4.2.6

# COPY pyproject.toml poetry.lock ./
# RUN inject_pyproject

COPY quipuswap /home/dipdup/quipuswap
COPY dipdup.yml /home/dipdup/dipdup.yml
COPY dipdup.prod.yml /home/dipdup/dipdup.prod.yml

CMD ["-c", "dipdup.yml", "-c", "dipdup.prod.yml", "run"]