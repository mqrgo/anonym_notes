import datetime
from fastapi import Form, BackgroundTasks
from cryptography.fernet import Fernet
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import db_settings
from models import Note
from schemas import NoteData
from celery import Celery
import smtplib
from email.mime.text import MIMEText


celery = Celery('tasks', broker='redis://localhost:6379') #connect with celery

engine = create_engine(url=db_settings.db_url)
Session = sessionmaker(bind=engine)

#SECTION OF ENCODING END DECODING NOTES
def encode_note(note: str) -> tuple:
    '''
    input - note
    encoding note using fernet
    return - encoded note and key (for decoding) as tuple
    '''
    key = Fernet.generate_key()
    f = Fernet(key)
    encoded_note = f.encrypt(note.encode())
    return encoded_note.decode(), key.decode()


def decode_note(note: str, key: str) -> str:
    '''
    input - encoded note (as str) and key (as str)
    return decoded note
    '''
    f = Fernet(key.encode())
    decoded_note = f.decrypt(note.encode())
    return decoded_note.decode()


#CELERY SECTION FOR SENGING MAILS AND LOGER
@celery.task
def send_mail(message: str, email: str) -> bool | dict:
    '''
    input - message that will be send and email
    using sender and SMTP pass (created using gmail) connecting to google service using smtplib
    forming a message using unput data and trying to send it
    return - True for succes an exception args
    '''
    sender = #sender from config
    password = #password from config
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    try:
        server.login(sender, password)
        msg = MIMEText(message)
        msg['Subject'] = 'Hello, you have got anonym message!'
        server.sendmail(from_addr=sender, to_addrs=email, msg=msg.as_string())
        return True
    except Exception as exc:
        return exc.args


@celery.task
def loger(note_id: str, err):
    '''
    input - note_id that was sended from HTTP body, and an error
    the time and date of the error and the error itself are recorded in a file
    '''
    created_log = f'Time - {datetime.datetime.now(datetime.UTC)}, note_id {note_id}: {err}\n'
    with open('logs/err_logs.txt', 'a') as f:
        f.write(created_log)


#CORE LOGIC OF APP
def add_note_into_db(note: str = Form(), email: str = Form()):
    '''
    The entry accepts a note and an email to which information about the note will be sent. 
    The information received as input is validated. The note itself is encrypted and sent to the database.
    A message about a new note is sent to the specified email
    '''
    try:
        note_data = NoteData(note=note, email=email)       
        encoded_note, key = encode_note(note=note_data.note)
        r = Note(note=encoded_note)

        with Session() as session:
            session.add(r)
            session.commit()
            id = session.query(Note.id).filter(Note.note == encoded_note).all()[0][0]

        send_mail.delay(message=f'message: {id} message key: {key}', email=email)
        return True
    except Exception as exc:
        loger.delay(id, exc.args)
        return False


def delete_note_from_db(id: str):
    'looks for a note with the required ID and deletes it from the database'
    try:
        with Session() as session:
            res = session.query(Note).filter(Note.id == int(id)).one()
            session.delete(res)
            session.commit()
        return True
    except Exception as exc:
        loger.delay(id, exc.args)
        return False
    

def get_note_from_db(note_id: str = Form(), key: str = Form()):
    '''
    Retrieves a note from the database using the specified ID. 
    If the note exists, then the note is decrypted using the key. 
    If the key is suitable, then the decrypted record is issued, and the note itself is deleted from the database.
    '''
    note_id = note_id.strip()
    key = key.strip()

    try:
        with Session() as session:
            res = session.query(Note.note).filter(Note.id == int(note_id)).all()[0][0]
        if not res:
            raise Exception('note doens not exist')
        if (decoded_note := decode_note(res, key)) is False:
            raise Exception('wrong key')
        delete_note_from_db(id=note_id)
        return decoded_note
    except Exception as exc:
        loger.delay(note_id, exc.args)
        return False
    




    


