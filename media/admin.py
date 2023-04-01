from django.contrib import admin

from media.models import Video, OperationGroup, Operation

@admin.register(Video)
class MediaAdmin(admin.ModelAdmin):
    class OperationGroupInline(admin.TabularInline):
        model = OperationGroup
        extra = 0
    
    inlines = [OperationGroupInline]

@admin.register(OperationGroup)
class MediaOperationGroupAdmin(admin.ModelAdmin):
    class OperationInline(admin.TabularInline):
        model = Operation
        extra = 0
    inlines = [OperationInline]

