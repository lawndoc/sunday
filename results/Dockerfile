FROM python:3.9

# DEFAULT ARGS that can be changed
ARG SECRET_KEY="insanely_secret_default_key"
ARG DB_URI="mongodb://localhost/testStats"

# set environment variables
ENV SECRET_KEY=$SECRET_KEY
ENV DB_URI=$DB_URI

# copy code and install dependencies
COPY . /opt/results
RUN pip install -r /opt/results/requirements.txt

# mostly for documentation purposes --> should still specify at runtime
EXPOSE 5000

# start app
WORKDIR "/opt/results"
ENTRYPOINT ["python", "/opt/results/results.py"]