from django.contrib import admin
from .models import CommunityPost, PostLike, PostComment


class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    readonly_fields = ('user', 'created_at')


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    inlines = [PostCommentInline]


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
