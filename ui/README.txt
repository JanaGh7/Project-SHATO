
docker build -t project-shato-ui ./ui

docker run --rm -p 7860:7860 project-shato-ui

curl http://localhost:7860

http://localhost:7860
