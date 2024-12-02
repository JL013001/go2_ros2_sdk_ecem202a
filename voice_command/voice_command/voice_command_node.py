import rclpy
from rclpy.node import Node
import speech_recognition as sr
import json
import re
import pyttsx3
import pyaudio
from vosk import Model, KaldiRecognizer


class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__('voice_command_node')
        self.model_path = "./vosk-model-small-en-us-0.15/"
        self.model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio = pyaudio.PyAudio()
        self.engine = pyttsx3.init()

        self.search_verbs = ["find", "search", "look for", "get"]
        self.verbs_pattern = "|".join([re.escape(verb) for verb in self.search_verbs])

        self.awake = False  # Initial wake state

        # Start listening
        self.say("Listening for wake word 'hi ben'.")
        self.stream = self.audio.open(
            format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000
        )
        self.stream.start_stream()

        self.timer = self.create_timer(0.1, self.listen)  # Call listen function periodically

    def say(self, text):
        self.get_logger().info(f"Saying: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def extract_item(self, command_text):
        pattern = rf"\b(?:i want to )?(?:{self.verbs_pattern})\s+(.+)"
        match = re.search(pattern, command_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def listen(self):
        data = self.stream.read(4000, exception_on_overflow=False)

        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            text = result.get('text', '').lower()
            self.get_logger().info(f"Recognized Text: {text}")

            if not self.awake:
                if "hi ben" in text:
                    self.say("Hello. I am listening.")
                    self.awake = True
            else:
                item = self.extract_item(text)
                if item:
                    self.say(f"Do you want me to find: {item}? Yes or no.")
                    self.handle_confirmation(item)

    def handle_confirmation(self, item):
        while True:
            confirmation_data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(confirmation_data):
                confirmation_result = json.loads(self.recognizer.Result())
                confirmation_text = confirmation_result.get('text', '').lower()
                self.get_logger().info(f"Confirmation Text: {confirmation_text}")

                if "yes" in confirmation_text:
                    self.say(f"Heading to find the {item} now.")
                    self.say("Is this what you are looking for? Yes or no.")
                    self.awake = False  # Return to standby mode
                    break
                elif "no" in confirmation_text:
                    self.say("Alright, returning to standby mode.")
                    self.awake = False  # Return to standby mode
                    break
                else:
                    self.say("Sorry, I didn't understand. Please say yes or no.")


def main(args=None):
    rclpy.init(args=args)
    node = VoiceCommandNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.say("Stopping the voice command node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
