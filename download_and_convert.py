
import openmc_data_downloader as odd
import pathlib
import openmc_data_to_json as odj

odd.just_in_time_library_generator(
    libraries='TENDL-2019',
    elements=['Li', 'Be', 'Na'],
    # elements='all',
    destination='TENDL-2019'
)

odj.cross_section_h5_files_to_json_files(
    filenames = list(pathlib.Path('TENDL-2019').glob('*.h5')),
    output_dir = 'TENDL-2019_json',
    library='TENDL-2019',
    index_filename='TENDL-2019_index.json'
)