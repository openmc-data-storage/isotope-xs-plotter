
# build with
# sudo docker build -t xsplot .

# run with
# sudo docker run --network host -t xsplot

# maintained at https://github.com/openmc-data-storage/xsplot.com/


FROM continuumio/miniconda3:4.9.2 as dependencies

RUN conda install -c conda-forge openmc

RUN pip install dash

RUN pip install openmc_data_downloader

RUN pip install openmc_data_to_json

RUN pip install gunicorn==20.0.4

COPY download_and_convert.py .

RUN python download_and_convert.py


COPY app.py .

ENV PORT 8080

EXPOSE 8080

# CMD [ "python" , "./app.py"]
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:server"]

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# https://cloud.google.com/run/docs/quickstarts/build-and-deploy/python
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:server
