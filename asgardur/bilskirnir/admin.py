from django.contrib import admin

from asgardur.bilskirnir.models import Picture, Gallery, Category, GalleryItem
from asgardur.bilskirnir.models import BatchUpload

class PictureAdmin(admin.ModelAdmin):
    model = Picture
    list_display = ('admin_thumbnail', '__unicode__')

class GalleryAdmin(admin.ModelAdmin):
    model = Gallery
    list_display = ('get_thumbnail', '__unicode__', 'category', 'order', 'published',)

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('title', 'order', )

class GalleryItemAdmin(admin.ModelAdmin):
    model = GalleryItem
    list_display = ('admin_thumbnail', 'title', 'picture', 'gallery', 'featured', )
    list_filter = ('gallery',)
    
class BatchUploadAdmin(admin.ModelAdmin):
    model = BatchUpload
    
admin.site.register(Picture, PictureAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(GalleryItem, GalleryItemAdmin)
admin.site.register(BatchUpload, BatchUploadAdmin)