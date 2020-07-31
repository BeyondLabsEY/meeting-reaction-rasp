import requests
import json
import pyaudio
import wave
from array import array
from util import Utility as util
from azure.storage.blob.blockblobservice import BlockBlobService
from azure.storage.queue import QueueService, QueueMessageFormat
from azure.storage.table import TableService
from datetime import datetime
import glob
import socket
import traceback
import os
import time
import cv2
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+"/config.ini")

REMOTE_SERVER = config["DEFAULT"]["REMOTE_SERVER"]
ACCOUNT_NAME = config["DEFAULT"]["ACCOUNT_NAME"]
ACCOUNT_KEY = config["DEFAULT"]["ACCOUNT_KEY"]
CONTAINER_NAME = config["DEFAULT"]["CONTAINER_NAME"]
QUEUE_NAME_AUDIO = config["DEFAULT"]["QUEUE_NAME_AUDIO"]
QUEUE_NAME_IMAGE = config["DEFAULT"]["QUEUE_NAME_IMAGE"]
FRONT_END_APP = config["DEFAULT"]["FRONT_END_APP"]
TABLE_TRACKING = config["DEFAULT"]["TABLE_TRACKING"]

camera_active = False
audio_active = False
recording_stop = False


def get_faces_num(imagem):
    classificador_face = cv2.CascadeClassifier(
        "classifier/haarcascade_frontalface_default.xml")

    imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    faces = classificador_face.detectMultiScale(imagem_gray, 1.3, 5)

    if faces is None:
        return 0
    else:
        return len(faces)


def buscar_meeting_code_processado(meeting_code):
    table_service = TableService(
        account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
    records = table_service.query_entities(
        TABLE_TRACKING, filter="PartitionKey eq 'audio-analysis' and RowKey eq '" + meeting_code + "'")
    return len(records.items) > 0


def get_meeting_code():
    code = util.get_random_string()
    return code


def buscar_codigo_sincronizado(meeting_code, main_app):
    while True:
        retorno = buscar_meeting_code_processado(meeting_code)
        if retorno:
            main_app.status_text = "Meeting code: " + meeting_code + " synced with cloud"
            print("Meeting Code persistido")
            break


def enviar_arquivos(meeting_code, main_app):
    while True:
        enviar_aquivos_audio_blob(main_app)
        enviar_aquivos_imagem_blob(main_app)
        time.sleep(10)


def enviar_aquivos_audio_blob(main_app, dir="audio_files/"):
    for file in glob.glob(dir + "*.wav"):
        try:
            print("Processando arquivo "+file + "...")
            meeting_code = file.split("_")[1].split("/")[1]
            blob = meeting_code + "/" + file
            print("Meeting code " + str(meeting_code))
            blob_service = BlockBlobService(
                account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
            blob_service.create_blob_from_path(CONTAINER_NAME, blob, file)

            if os.path.exists(file):
                os.remove(file)

            queue_service = QueueService(
                account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
            queue_service.encode_function = QueueMessageFormat.text_base64encode
            payload = {"meeting-code": meeting_code, "blob": blob,
                       "file-name": util.get_file_with_extension(file)}

            payload = json.dumps(payload, ensure_ascii=False)

            queue_service.put_message(QUEUE_NAME_AUDIO, payload)
            print("Arquivo " + file + " processado com sucesso.")

            main_app.mensagem["text"] = "File " + file + " synced successfully"

        except:
            traceback.format_exc()


def enviar_aquivos_imagem_blob(main_app, dir="image_files/"):
    for file in glob.glob(dir + "*.jpg"):
        try:
            print("Processando arquivo "+file + "...")
            meeting_code = file.split("_")[1].split("/")[1]
            blob = meeting_code + "/" + file
            print("Meeting code " + str(meeting_code))
            blob_service = BlockBlobService(
                account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
            blob_service.create_blob_from_path(CONTAINER_NAME, blob, file)

            if os.path.exists(file):
                os.remove(file)

            queue_service = QueueService(
                account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
            queue_service.encode_function = QueueMessageFormat.text_base64encode

            date_time = datetime.now()
            date_time_formatted = date_time.strftime("%d/%m/%Y %H:%M")

            payload = {"meeting-code": meeting_code, "blob": blob, "date-time": date_time_formatted,
                       "file-name": util.get_file_with_extension(file)}

            payload = json.dumps(payload, ensure_ascii=False)

            queue_service.put_message(QUEUE_NAME_IMAGE, payload)
            print("Arquivo " + file + " processado com sucesso.")

            #main_app.mensagem["text"] = "File " + file + " synced successfully"

        except:
            traceback.format_exc()


def obter_sample_rate():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i))


def video_recorder(meeting_code, main_app):
    cam = None

    while recording_stop is not True:
        try:
            time.sleep(30)

            if camera_active:
                if cam is None:
                    cam = cv2.VideoCapture(0)

                cap, frame = cam.read()

                if cap:
                    frame = cv2.resize(frame, None, fx=3,
                                       fy=3, interpolation=cv2.INTER_LANCZOS4)
                    num_faces = get_faces_num(frame)
                    main_app.camera_text = "Faces around " + \
                        str(num_faces) + "."

                    print("Faces around " + str(num_faces) + ".")

                    if num_faces >= 0:
                        random_file_name = util.get_random_string(4) + ".jpg"
                        file_path = "image_files/" + \
                            str(meeting_code) + "_" + random_file_name
                        cv2.imwrite(file_path, frame)

                cam.release()
                cam = None
            else:
                main_app.camera_text = "Camera off"
        except:
            traceback.format_exc()
            pass


def audio_recorder(meeting_code, main_app):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 256
    RECORD_SECONDS = 8

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    t1 = datetime.now()
    zero_vol = 0

    print("Audio Status: " + str(audio_active))

    while True:
        try:
            if not audio_active:
                #print("Audio Status: " + str(audio_active))
                time.sleep(1)
                continue

            #print("Audio Status: " + str(audio_active))

            if not stream.is_active():
                print("Stream is not active")
                audio.terminate()
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
                frames = []
                t1 = datetime.now()

            data = stream.read(CHUNK, exception_on_overflow=False)
            data_chunk = array('h', data)
            vol = max(data_chunk)

            if vol == 0:
                zero_vol += 1

                main_app.start_meeting_text = "Mic is muted!"

                if zero_vol > 10:
                    cmd = "amixer -c 1 sset Mic toggle"
                    os.system(cmd)
                    zero_vol = 0
            else:
                main_app.start_meeting_text = "Recording..."
                zero_vol = 0

            frames.append(data)

            t2 = datetime.now()
            result = t2 - t1

            if result.seconds >= RECORD_SECONDS:
                print("Tempo terminado")
                stream.stop_stream()

                random_file_name = util.get_random_string(4) + ".wav"

                wavfile = wave.open(
                    "audio_files/" + str(meeting_code) + "_" + random_file_name, 'wb')
                wavfile.setnchannels(CHANNELS)
                wavfile.setsampwidth(audio.get_sample_size(FORMAT))
                wavfile.setframerate(RATE)
                wavfile.writeframes(b''.join(frames))
                wavfile.close()

            if recording_stop is True:
                print("Recording is over")
                stream.stop_stream()

                random_file_name = util.get_random_string(4) + ".wav"

                wavfile = wave.open(
                    "audio_files/" + str(meeting_code) + "_" + random_file_name, 'wb')
                wavfile.setnchannels(CHANNELS)
                wavfile.setsampwidth(audio.get_sample_size(FORMAT))
                wavfile.setframerate(RATE)
                wavfile.writeframes(b''.join(frames))
                wavfile.close()

                main_app.start_meeting_text = "Start"

                break

        except:
            traceback.format_exc()
            pass

    try:
        stream.close()
        audio.terminate()
    except:
        traceback.format_exc()
        pass


def is_connected(hostname=REMOTE_SERVER):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80), timeout=2)
        return True
    except:
        pass
    return False
