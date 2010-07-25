import Image, os, random, zipfile
from cStringIO import StringIO

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile

UPLOAD_TO = "bsk"

class Picture(models.Model):
    image = models.ImageField(upload_to=UPLOAD_TO)
        
    title = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.title or self.image.name.split('/')[-1]
    
    def get_thumb_path(self, width, height):
        # TODO: Make more generic
        path = "%s/%s/%d.%d" % (settings.MEDIA_ROOT, UPLOAD_TO, width, height)
        filename = self.image.name.split('/')[-1]
        full = os.path.join(path, filename)
        # Step one: Check if file exists
        if not os.path.exists(full):
            # Step one b: Check if directory exists
            if not os.path.exists(path):
                # Then create directory
                os.mkdir(path)
            # Step two: Create the file
            self.create_thumb(width, height)
        return path + filename

    def create_thumb(self, width, height):
        img = Image.open(self.image.path)
        if width > 0 and height > 0:
            h = height
            if h == 0 and width < self.image.width:
                h = int(self.image.height * (float(width) / self.image.width))
            img.thumbnail((width, h), Image.ANTIALIAS)
        img.save("%s/%s/%d.%d/%s" % (
            settings.MEDIA_ROOT, UPLOAD_TO, width, height, 
            self.image.name.split('/')[-1])
        )

    def get_thumb_url(self, height=156, width=156):
        # TODO: Make more generic
        # Check for file existence in the process
        self.get_thumb_path(width, height) 
        return "%s%s/%d.%d/%s" % (
            settings.MEDIA_URL, UPLOAD_TO, width, height,
            self.image.name.split('/')[-1]
        )
        
    def delete(self, *args, **kwargs):
        top = "%s/%s" % (settings.MEDIA_ROOT, UPLOAD_TO)
        for root, dirs, files in os.walk(top):
            for name in files:
                    if name == self.image.name.split('/')[-1]:
                        os.remove(os.path.join(root, name))
        super(Picture, self).delete(*args, **kwargs)
        
    def admin_thumbnail(self):
        return u'<img src="%s">' % self.get_thumb_url(56, 56)
    admin_thumbnail.short_description = 'Thumb'
    admin_thumbnail.allow_tags = True

class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('order', 'title', )
    
    def __unicode__(self):
        return self.title

class Gallery(models.Model):
    title = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, blank=True, null=True)

    order = models.PositiveIntegerField(blank=True, null=True)
    published = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'galleries'
        ordering = ('category__order', 'category__title', 'order', 'title',)
    
    def __unicode__(self):
        return self.title or "gallery_%d" % self.pk
        
    def get_thumbnail(self, height=156, width=156):
        # TODO: Get a random thumb, and check if there are no 'featured' ones
        thumbs = self.galleryitem_set.filter(
            featured=True
        ) or self.galleryitem_set.all()
        if thumbs:
            thumb = random.sample(thumbs, 1)[0]
            return u'<img src="%s" alt="%s">' % (
                thumb.picture.get_thumb_url(
                    height, width
                ), thumb.title
            )
        else:
            return u"No thumbnail"
    get_thumbnail.short_description = 'Thumb'
    get_thumbnail.allow_tags = True
    
class GalleryItem(models.Model):
    picture = models.ForeignKey(Picture)
    gallery = models.ForeignKey(Gallery)
    
    title = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True)

    featured = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "%s in %s" % (self.picture, self.gallery)
        
    def url(self):
        return self.picture.image.url
        
    def admin_thumbnail(self):
        return self.picture.admin_thumbnail()
    admin_thumbnail.short_description = 'Thumb'
    admin_thumbnail.allow_tags = True
    
class BatchUpload(models.Model):
    zipfile = models.FileField(upload_to="zipfile")
    
    def save(self, *args, **kwargs):
        super(BatchUpload, self).save(*args, **kwargs)
        z = zipfile.ZipFile(self.zipfile.path)
        g = Gallery.objects.create(
            published=False
        )
        for filename in sorted(z.namelist()):
            data = z.read(filename)
            if len(data):
                try:
                    trial_image = Image.open(StringIO(data))
                    trial_image.load()
                    trial_image = Image.open(StringIO(data))
                    trial_image.verify()
                except Exception:
                    continue
                p = Picture()
                p.image.save(filename, ContentFile(data))
                GalleryItem.objects.create(
                    picture=p,
                    gallery=g
                )
        z.close()
        self.delete()