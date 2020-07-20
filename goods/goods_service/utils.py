import os


class DiskWorker:
    """Class performs saving of the image to /static/ directory"""

    def __init__(self):
        self.path = os.getcwd() + "/static/"

    def save_to_disk(self, file_data, file_name):
        """Function receives image data and name to save file in /static/ directory.
        Returns full path to created file"""

        file_name = str(file_name) + ".jpeg"

        fullpath_to_file = self.path + file_name

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        with open(fullpath_to_file, "wb") as file:
            file.write(file_data)

        return fullpath_to_file
