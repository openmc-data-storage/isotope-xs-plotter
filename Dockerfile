
# docker build -t xsplot .

FROM continuumio/miniconda3:4.9.2 as dependencies

RUN conda install -c conda-forge openmc

RUN pip install openmc_data_downloader

RUN pip install openmc_data_to_json

RUN pip install dash



# make index file for example cross sections

# mount json files

# build second stage docker image and del the first

# make streamlit / dash gui that loads the json files and makes 


