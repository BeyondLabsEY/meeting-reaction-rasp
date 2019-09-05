import kivy
kivy.require('1.0.5')
 
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import StringProperty, BooleanProperty

import meeting_word_cloud as meeting
import threading

class Controller(FloatLayout):

    start_meeting_button_text = StringProperty()
    stop_meeting_button_text = StringProperty()
    
    status_text = StringProperty()
    header_text = StringProperty()
    camera_text = StringProperty()

    start_button = BooleanProperty()
    stop_button = BooleanProperty()
    
    def audio_toggle(self):
        meeting.audio_active = self.ids.audio_checkbox.active
        print("Audio Status: " + str(meeting.audio_active))
    
    def video_toggle(self):
        meeting.camera_active = self.ids.video_checkbox.active
        print("Video Status: " + str(meeting.camera_active))
              
    def record_meeting(self):
        self.start_button = True

        self.start_meeting_text = 'Recording...'
        meeting.recording_stop = False
        
        self.meeting_code = meeting.get_meeting_code()
         
        self.header_text = "Meeting Reaction\n" + meeting.FRONT_END_APP + "\nMeeting Code: " + self.meeting_code
        
        #if self.ids.video_checkbox.active:
        threading.Thread(target=meeting.video_recorder, args=(self.meeting_code, self)).start()
        #    meeting.camera_active = True
        #else:
        #    meeting.camera_active = False
        
        #if self.ids.audio_checkbox.active:
        threading.Thread(target=meeting.audio_recorder, args=(self.meeting_code, self)).start()
        #    meeting.audio_active = True
        #else:
        #    meeting.audio_active = False
        
        threading.Thread(target=meeting.enviar_arquivos, args=(self.meeting_code, self)).start()
        threading.Thread(target=meeting.buscar_codigo_sincronizado, args=(self.meeting_code, self)).start()
       
        self.status_text = "Meeting code: " + self.meeting_code + " sync pending..."
        self.stop_button = False
 
    def stop_meeting(self):
        self.stop_button = True
        self.start_meeting_text = "Stopped"
        self.stop_meeting_text = "Stopping"
        self.status_text = "Recording has stopped"
        meeting.recording_stop=True
        meeting.enviar_aquivos_imagem_blob(self)
        meeting.enviar_aquivos_audio_blob(self)
        self.status_text = "Recordings synced with cloud."
        self.start_meeting_text = "Start"
        self.stop_meeting_text = "Stop"
        self.start_button = False
 
class ControllerApp(App):
    
    def build(self):
        
        self.title = "Reaction"
        
        if meeting.is_connected():
            status_text = "Internet OK, ready for recording"
            meeting.enviar_aquivos_audio_blob(self)
            meeting.enviar_aquivos_imagem_blob(self)
        else:
            status_text = "Check you internet connection"
            
        return Controller(stop_meeting_button_text="Stop",
                          start_meeting_button_text="Start",
                          status_text=status_text,
                          header_text="Meeting Reaction\n" + meeting.FRONT_END_APP,
                          start_button = False,
                          camera_text = "Camera off")
 
 
if __name__ == '__main__':
    ControllerApp().run()