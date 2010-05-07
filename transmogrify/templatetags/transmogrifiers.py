import os
from transmogrify.hashcompat import sha_constructor
from transmogrify import settings
from django import template
from django.utils.text import smart_split

ACTIONS = {
    'thumbnail':'t', 
    'crop':'c', 
    'forcefit': 's', 
    'resize': 'r', 
    'letterbox': 'l', 
    'filter': 'f', 
    'border': 'b',
}
FILTERS = ["blur", "contour", "edge_enhance", "edge_enhance_more", "emboss",
           "find_edges", "smooth", "smooth_more", "sharpen"]

def resolve(var, context):
    """
    Resolve the variable, or return the value passed to it in the first place
    """
    try:
        return var.resolve(context)
    except template.VariableDoesNotExist:
        return var.var

def transmogrify(parser, token):
    """
    """    
    bits = smart_split(token.contents)
    tagname = bits.next()
    try:
        imageurl = bits.next()
    except StopIteration:
        raise template.TemplateSyntaxError("%r tag requires at least the image url" % tagname)
    
    # Parse the actions into a list of (action, arg) tuples.
    # The "border" and "letterbox" actions are a special case: they take two arguments.
    actions = []
    for action in bits:
        if action not in ACTIONS:
            raise template.TemplateSyntaxError("Unknown action in %r tag: %r" % (tagname, action))
        if action in ["border", "letterbox"]:
            param1 = bits.next()
            color = bits.next()
            color = color.lstrip("#")
            actions.append((action, param1, color))
        else:
            actions.append((action, bits.next()))
    
    # No actions is an error
    if not actions:
        raise template.TemplateSyntaxError("%r tag requires at least one action" % (tagname))
    
    return MogrifyNode(imageurl, actions)


def one_param_shortcut(parser, token):
    """
    Shortcut to transmogrify thumbnail
    """
    bits = smart_split(token.contents)
    tagname = bits.next()
    try:
        imageurl = bits.next()
        param1 = bits.next()
    except StopIteration:
        raise template.TemplateSyntaxError("%r tag requires at least the image url" % tagname)
    
    return MogrifyNode(imageurl, [(tagname, param1),])


def two_param_shortcut(parser, token):
    """
    Shortcut to transmogrify thumbnail
    """
    bits = smart_split(token.contents)
    tagname = bits.next()
    try:
        imageurl = bits.next()
        param1 = bits.next()
        param2 = bits.next()
        param2 = param2.lstrip("#")
    except StopIteration:
        raise template.TemplateSyntaxError("%r tag requires at least the image url" % tagname)
    
    return MogrifyNode(imageurl, [(tagname, param1, param2),])



class MogrifyNode(template.Node):
        
    def __init__(self, imageurl, actions):
        self.imageurl, self.actions = template.Variable(imageurl), actions
        
    def render(self, context):
        imageurl = resolve(self.imageurl, context)
        
        if not imageurl:
            imageurl = settings.NO_IMAGE_URL
            
        action_list = []
        
        for action in self.actions:
            action_code = ACTIONS[action[0]]
            arg_list = [str(resolve(template.Variable(arg), context)) for arg in action[1:]]
            args = "-".join(arg_list)
            if settings.PROCESSORS[action_code].param_pattern().match(args):
                action_list.append("_%s%s" % (action_code, args))
            else:
                raise template.TemplateSyntaxError("The action '%s' doesn't accept the arguments: %s" % (action[0], ",".join(action[1:])))
        
        # Make sure we've actually got some actions.
        if not action_list:
            return imageurl
        
        # Construct the action into a string, and calculate the security hash
        action_string = "".join(action_list)
        security_hash = sha_constructor(action_string + settings.SECRET_KEY).hexdigest()
        
        # Apply the converted actions to the image url
        prefix, ext = os.path.splitext(imageurl)
        return "%s%s%s?%s" % (prefix, action_string, ext, security_hash)

register = template.Library()
register.tag(transmogrify)
register.tag('thumbnail', one_param_shortcut)
register.tag('crop', one_param_shortcut)
register.tag('forcefit', one_param_shortcut)
register.tag('resize', one_param_shortcut)
register.tag('filter', one_param_shortcut)
register.tag('border', two_param_shortcut)
register.tag('letterbox', two_param_shortcut)
