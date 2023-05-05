from cdg_service.service.common.base_service import Service
from cdglib.models_client import Organisation
from pathlib import Path
from os.path import split
from pprint import pprint
from random import choice, randint


class FileService(Service):
    """ Service for managing files """

    def create(self, filename):
        """ Create a file """
        session = self.session
        organisation = session.query(Organisation).first()
        upload_path = organisation.get_upload_path()


    def read(self, extensions=[]):
        """ List all files """
        session = self.session
        organisation = session.query(Organisation).first()
        upload_path = organisation.get_upload_path()
        return self._get_files_in_path(upload_path, extensions)

    def update(self, filename, new_file):
        """ Update a file """
        session = self.session

    def delete(self, filename):
        """ Delete a file with filename """
        session = self.session


    def analyse(selfself, filename):
        """ Analyse a file for time series properties """
        return {
            "filename": filename,
            "interval": "%sT"%randint(1,60),
            "regular_data": choice([True, False]),
            "synchronized_data": choice([True, False]),
            "repeat_data": choice([True, False]),
            "apply_delta": choice([True, False]),
            "messages": ["Analysis based on 1867 timestamps", "Interval 15M found in 89% cases", "Interval is regular (>80%)","Data is continuously increasing with 2 resets"]            
        }

    def _get_files_in_path(self, upload_path, extensions=[]):
        """ Loop over extensions and fetch the files matching """
        matched_files = []
        if extensions:
            for ext in extensions:
                files = [split(f)[1] for f in Path(upload_path).rglob("*.%s"%ext)]
                matched_files.extend(files)
        else:
            files = [split(f)[1] for f in Path(upload_path).rglob("*")]
            matched_files.extend(files)
        return matched_files

