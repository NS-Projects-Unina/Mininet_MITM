# Certificato per il SERVER (h1)
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
    -keyout server.key -out server.crt -subj "/CN=ArcadeServer"

# Certificato falso per l'ATTACCANTE (h3)
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
    -keyout attacker.key -out attacker.crt -subj "/CN=ArcadeServer"

