import os
from hashcompat import sha_constructor
from PIL import Image
from settings import PROCESSORS, SECRET_KEY

class Transmogrify(object):
    def __init__(self, original_file, action_tuples = [], **kwargs):
        self.im = Image.open(original_file)
        self.actions = action_tuples
        self.original_file = original_file
    
    def save(self):
        """
        Apply a series of actions from a set of (action, arg) tuples, probably
        as parsed from a URL. Each action is a code into PROCESSORS.
        
        Then save the mogrified image.
        """
        for action, arg in self.actions:
            action = PROCESSORS[action]
            self.im = action.process(self.im, arg)
        
        filename = self.get_processed_filename()
        self.im.save(filename, quality=85)
    
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
        
        return os.path.join(parent_dir, "%s%s%s" % (base_filename, action_string, ext))
    
    def get_action_string(self):
        code = ["_%s%s" % (action, param) for action, param in self.actions]
        return "".join(code)
    
    def get_security_hash(self):
        action_string = self.get_action_string()
        return sha_constructor(action_string + SECRET_KEY).hexdigest()
