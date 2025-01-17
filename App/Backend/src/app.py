from click import command
from flask import Flask, request, jsonify, send_from_directory, Response, send_file
from config import config
from utils import *
from Exceptions import *
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS, cross_origin
import uuid
import coloredlogs
import logging
import json
import ERROR_CODES

# TODO: Implementar API KEY https://geekflare.com/es/securing-flask-api-with-jwt/


def create_app(enviroment):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(enviroment)
    return app


# Logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

# Configuración
enviroment = config['DEVELOPMENT_CONFIG']
app = create_app(enviroment)
# TODO: No funciona session cookie
# TODO: Comprobar CSRF
# app.secret_key = "secret_key"
# csrf = CSRFProtect(app)

# Directorio de subida de archivos
# if not os.path.exists(config['DIRECTORY_UPLOADED_FILE']):
#     os.makedirs(config['DIRECTORY_UPLOADED_FILE'])
# TODO: Y si no existe el directorio?
os.makedirs(getAbsolutePath(config['DIRECTORY_UPLOADED_FILE']), exist_ok=True)
os.makedirs(getAbsolutePath(
    config['DIRECTORY_FILES_PROCESSED']), exist_ok=True)
os.makedirs(getAbsolutePath(
    config['DIRECTORY_FILES_BAKED_TEXTURES']), exist_ok=True)
os.makedirs(getAbsolutePath(
    config['DIRECTORY_MOSAICS_GENERATED']), exist_ok=True)


if(config["REMOVE_DIRECTORIES"]):
    for f in os.listdir(config['DIRECTORY_UPLOADED_FILE']):
        os.remove(getAbsolutePath(config['DIRECTORY_UPLOADED_FILE'], f))
    for f in os.listdir(config['DIRECTORY_FILES_PROCESSED']):
        os.remove(getAbsolutePath(config['DIRECTORY_FILES_PROCESSED'], f))
    for f in os.listdir(config['DIRECTORY_FILES_BAKED_TEXTURES']):
        os.remove(getAbsolutePath(config['DIRECTORY_FILES_BAKED_TEXTURES'], f))
    for f in os.listdir(config['DIRECTORY_MOSAICS_GENERATED']):
        os.remove(getAbsolutePath(config['DIRECTORY_MOSAICS_GENERATED'], f))

# Manejo de errores
# TODO: Cambiar codigo de vuelta


def invalid_api_usage(e):
    response = jsonify(e.to_dict())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 300


# Registro de manejadores
app.register_error_handler(InvalidAPIParameterException, invalid_api_usage)
# app.register_error_handler(InvalidResolutionRangeException, invalid_api_usage)
# app.register_error_handler(InvalidResolutionTypeException, invalid_api_usage)
# app.register_error_handler(NotAllowedFileExtensionException, invalid_api_usage)
# app.register_error_handler(MissingArgumentsException, invalid_api_usage)

# Método de apoyo para enviar respuesta
# def sendResponse(exc):
#     response = jsonify({'message': "OK" })
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response, exc.code


@ app.route('/api/uploadFile', methods=['POST'])
def receive_file():
    # PARÁMETROS DE ENTRADA
    # ==============================================================
    # Resolucion para la voxelización
    try:
        resolution = request.form[config['API_PARAM_RESOLUTION']]
    except KeyError as e:
        resolution = None
    # Usar eliminar elementos inconexos
    try:
        removeDisconnectedElements = request.form[config['API_PARAM_USE_REMOVE_DISCONNECTED']]
    except KeyError as e:
        removeDisconnectedElements = None

    missingArguments = []
    if(not resolution):
        missingArguments.append(config['API_PARAM_RESOLUTION'])
    if(not removeDisconnectedElements):
        missingArguments.append(config['API_PARAM_USE_REMOVE_DISCONNECTED'])
    if(not request.files or not config['API_PARAM_MAIN_FILE'] in request.files):
        missingArguments.append(config['API_PARAM_MAIN_FILE'])

    if(len(missingArguments) > 0):
        raise InvalidAPIParameterException(
            ERROR_CODES.MISSING_PARAMETERS_ERROR_013, missingArguments)

    try:
        resolution = int(resolution)
    except ValueError:
        raise InvalidAPIParameterException(
            ERROR_CODES.INVALID_RESOLUTION_TYPE_ERROR_011)

    if(resolution not in config['RESOLUTION_RANGE_ALLOWED']):
        raise InvalidAPIParameterException(
            ERROR_CODES.INVALID_RESOLUTION_RANGE_ERROR_010)

    if(removeDisconnectedElements not in config['USE_REMOVE_DISCONNECTED_ELEMENTS_ALLOWED']):
        raise InvalidAPIParameterException(
            ERROR_CODES.INVALID_REMOVE_DISCONNECTED_ELEMENTS_TYPE_ERROR_014)

    # Analizar el fichero de entrada
    file = checkFileUploaded(request.files)
    # ==============================================================
    # Guardar archivo y voxelizar figura
    returned_file_name = None
    if file:
        # Nombre y extension del archivo
        ext = file.filename.split('.')[1]
        UUID = str(uuid.uuid1())
        file_name = UUID + '.' + ext

        # Guardar en archivos subidos
        path_save = getAbsolutePath(
            config["DIRECTORY_UPLOADED_FILE"], file_name)
        file.save(path_save)

        # Voxelization with textures Algorithm and Mosaic generation
        uvs_info = Voxelization(UUID, file_name, resolution,
                                removeDisconnectedElements)

        returned_file_name = UUID + "." + \
            config["RETURNED_ALLOW_FILE_EXTENSION"]

        textureBlocks = Mosaic(uvs_info, UUID)

        applyTexture(returned_file_name, UUID)

        comando = createMinecraftCommand(textureBlocks)
        # print(commando.replace("'", '"'))

    # TODO: Send OK, archivo, comando...
    filePath = getAbsolutePath(
        config['DIRECTORY_FILES_PROCESSED'], returned_file_name)
    f = open(filePath, "r")
    s_f = f.read()
    f.close()
    return {"command": comando, "file": s_f}


if __name__ == '__main__':
    app.run(debug=True)
