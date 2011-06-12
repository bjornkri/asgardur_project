from django import template

register = template.Library()

class GetThumbnailUrlNode(template.Node):
    def __init__(self, image, width, height):
        self.image = template.Variable(image)
        self.width = width
        self.height = height
        
    def render(self, context):
        actual_image = self.image.resolve(context)
        return actual_image.get_thumb_url(self.width, self.height)

@register.tag(name='get_thumb_url')
def do_get_thumb_url(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, image, width, height = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    return GetThumbnailUrlNode(image, int(width), int(height))
    