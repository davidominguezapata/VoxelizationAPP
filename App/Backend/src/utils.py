import logging
import os
from statistics import mean
# from mosaic_generation import *

import ERROR_CODES
from Exceptions import *
from config import config
from re import *

from PIL import Image
from scipy import spatial
import numpy as np
import glob

import time

# Constantes
BLENDER_COMMAND = 'blender --background --factory-startup --python ./scripts/voxelization.py -- {} {} {} {} {} {} {}'

# TimeStamp
DEBUG_TIME = False
start = None
end = None


# Logger
logger = logging.getLogger(__name__)


def list_to_string(list):
    return ''.join(list)


def allowed_file_extension(filename, extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in extensions


def checkFileUploaded(files):
    # Get main file
    mainFile = files[config['API_PARAM_MAIN_FILE']]
    logger.debug(mainFile)

    if not allowed_file_extension(mainFile.filename, config['ALLOWED_EXTENSIONS_MODEL_FILE']):
        raise InvalidAPIParameterException(
            ERROR_CODES.NOT_ALLOWED_FILE_EXTENSION_ERROR_012, list_to_string(config['ALLOWED_EXTENSIONS_MODEL_FILE']))

    return mainFile


# METODOS DE VOXELIZACION
def Voxelization(UUID, file_name, resolution, removeDisconnectedElements):
    formatted_command = BLENDER_COMMAND.format(
        config['DIRECTORY_UPLOADED_FILE'] + '/' + file_name, config['DIRECTORY_FILES_PROCESSED'] + '/' + file_name, resolution, removeDisconnectedElements, UUID, config['DIRECTORY_FILES_BAKED_TEXTURES'], config['BAKED_FILES_EXTENSION'])
    output = os.popen(formatted_command)
    print(output.read())
    errors = findall("ERR_CODE: \d", output.read())
    logger.error(errors)
    for e in errors:
        if('1' in e):
            raise InvalidAPIParameterException(
                ERROR_CODES.NO_SINGLE_ELEMENT_IN_FILE_ERROR_030)
    return None


def Mosaic():
    # start = time.time()
    # Configuracion
    main_file = "..\\TEXTURAS_Y_MODELOS\\UV_DE_REFERENCIA.png"
    main_photo = Image.open(main_file)

    colors = []
    for tile_path in os.listdir(config['DIRECTORY_MINECRAFT_TEXTURES']):
        tile_img = Image.open(
            config['DIRECTORY_MINECRAFT_TEXTURES'] + '\\'+tile_path)
        mean_color = np.array(tile_img).mean(axis=0).mean(axis=0)
        if(mean_color.shape and mean_color.shape[0] == 4):
            colors.append(mean_color)

    tree = spatial.KDTree(colors)
    # end = time.time()
    # print("TIME: " + str(end-start))

    pass
