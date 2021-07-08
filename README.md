# xsplot.com

The source code for a cross section plotting website [xsplot.com](http://xsplot.com)

This repository contains:
- the [Plotly Dash](https://plotly.com/dash/) based GUI
- A dockerfile that provides the hosting enviroment

Pushing to the main branch of this repository triggers an automatic rebuild and
deployment of the new code at the xsplot.com

The website makes use of a few other packages to process the nuclear data:
- [openmc_data_downloader](https://github.com/openmc-data-storage/openmc_data_downloader) to download processed h5 nuclear data files.
- [openmc_data_to_json](https://github.com/openmc-data-storage/openmc_data_to_json) to convert the h5 files (per isotope) into seperate reaction files.
- [nuclear_data_base_docker](https://github.com/openmc-data-storage/nuclear_data_base_docker) to provide a dockerfile containing all the required nuclear data with an index / loop up file containing every reaction available.