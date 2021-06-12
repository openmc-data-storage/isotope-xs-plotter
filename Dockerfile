
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

COPY download_and_convert.py .

RUN python download_and_convert.py

COPY dash_gui.py .

ENV PORT 8050

EXPOSE 8050

CMD [ "python" , "./dash_gui.py"]
