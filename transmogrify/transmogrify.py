import os
from hashlib import sha1
from PIL import Image
import images2gif
from settings import PROCESSORS, SECRET_KEY


class Transmogrify(object):
    def __init__(self, original_file, action_tuples=[], quality=80, output_path=None, **kwargs):
        self.im = Image.open(original_file)
        if 'duration' in self.im.info and self.im.format == 'GIF':
            self.duration = int(self.im.info['duration']) / 1000.0
            self.frames = images2gif.readGif(original_file, False)
        else:
            self.duration = None
            self.frames = []
        self.output_path = output_path
        self.original_file = original_file
        self.actions = action_tuples
        self.cropname = None
        self.quality = quality

    def save(self):
        """
        Apply a series of actions from a set of (action, arg) tuples, probably
        as parsed from a URL. Each action is a code into PROCESSORS.

        Then save the mogrified image.
        """
        filename = self.get_processed_filename()
        for action, arg in self.actions:
            action = PROCESSORS[action]
            if self.frames:
                new_frames = []
                for frame in self.frames:
                    new_frames.append(action.process(frame, arg))
                images2gif.writeGif(filename, new_frames)
            else:
                self.im = action.process(self.im, arg)
                self.im.save(filename, quality=self.quality)

    def apply_action_tuples(self, actions):
        """
        Add more actions to the stack of actions. Nothing is done until the
        image is saved.
        """
        self.actions.extend(actions)

    def get_processed_filename(self):
        parent_dir, filename = os.path.split(self.original_file)
        base_filename, ext = os.path.splitext(filename)
        action_string = self.get_action_string()
        cropname = self.cropname
        parent_dir = self.output_path or parent_dir
        if cropname:
            return os.path.join(parent_dir, "%s-%s%s" % (base_filename, cropname, ext))
        else:
            return os.path.join(parent_dir, "%s%s%s" % (base_filename, action_string, ext))

    def get_action_string(self):
        code = ["_%s%s" % (action, param) for action, param in self.actions]
        return "".join(code)

    def get_security_hash(self):
        action_string = self.get_action_string()
        return sha1(action_string + SECRET_KEY).hexdigest()
