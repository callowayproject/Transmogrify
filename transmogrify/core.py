import os
from hashlib import sha1
from PIL import Image
import images2gif
import optimize


class Transmogrify(object):
    def __init__(self, path_and_query, server="", **kwargs):
        from .utils import process_url

        url_parts = process_url(path_and_query, server)
        original_file = url_parts['original_file']
        output_path, _ = os.path.split(url_parts['requested_file'])

        if original_file.startswith('s3://'):
            import s3
            self.im = Image.open(s3.get_file(original_file))
        elif not os.path.exists(original_file) or not os.path.isfile(original_file):
            self.im = None
        else:
            self.im = Image.open(original_file)
        if self.im and 'duration' in self.im.info and self.im.format == 'GIF':
            self.duration = int(self.im.info['duration']) / 1000.0
            self.frames = images2gif.read_gif(original_file, True)
        else:
            self.duration = None
            self.frames = []
        self.output_path = output_path
        self.original_file = original_file
        self.actions = url_parts['actions']
        self.quality = kwargs.get('quality', 80)
        self.filename = self.get_processed_filename()

        _, fmt = os.path.splitext(self.filename)
        fmt = fmt.lower().replace('.', '')
        if fmt == 'jpg':
            fmt = 'jpeg'
        self.format = fmt

    def save(self):
        """
        Apply a series of actions from a set of (action, arg) tuples, probably
        as parsed from a URL. Each action is a code into PROCESSORS.

        Then save the mogrified image.
        """
        from settings import PROCESSORS
        from .filesystem import makedirs

        if self.im is None:
            return
        makedirs(self.output_path)
        for action, arg in self.actions:
            action = PROCESSORS[action]
            if self.frames:
                new_frames = []
                for frame in self.frames:
                    new_frames.append(action.process(frame, arg))
                self.frames = new_frames
            else:
                self.im = action.process(self.im, arg)

        self.im = optimize.optimize(self.im, fmt=self.format, quality=self.quality)

        if self.filename.startswith('s3://'):
            import cStringIO
            import s3
            output = cStringIO.StringIO()
            if self.frames:
                images2gif.write_gif(output, self.frames)
            else:
                self.im.save(output, format=self.format, quality=self.quality)
            output.reset()
            s3.put_file(output, self.filename)
        else:
            if self.frames:
                images2gif.write_gif(self.filename, self.frames)
            else:
                self.im.save(self.filename, quality=self.quality)

    def apply_action_tuples(self, actions):
        """
        Add more actions to the stack of actions. Nothing is done until the
        image is saved.
        """
        self.actions.extend(actions)

    def get_processed_filename(self):
        parent_dir, filename = os.path.split(self.original_file)
        base_filename, ext = os.path.splitext(filename)
        cropname = getattr(self, 'cropname', None)
        if cropname is not None:
            action_string = "-%s" % self.cropname
        else:
            action_string = self.get_action_string()
        parent_dir = self.output_path or parent_dir
        return os.path.join(parent_dir, "%s%s%s" % (base_filename, action_string, ext))

    def get_action_string(self):
        code = ["_%s%s" % (action, param) for action, param in self.actions]
        return "".join(code)

    def get_security_hash(self):
        from settings import SECRET_KEY

        action_string = self.get_action_string()
        return sha1(action_string + SECRET_KEY).hexdigest()
