
from django.contrib.auth.models import User, Group
from .models import User_T, Room, RoomAllocation, Exam, Notification, TakeDuty, AssignDuty, Course, ExamAllocation
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, AdminPasswordChangeForm
from django.contrib import admin

admin.site.site_header = 'FacAssist'
admin.site.site_title = 'FacAssist'
admin.site.index_title = "ADMIN ACCOUNT"


class UserInline(admin.StackedInline):
    model = User_T
    extra = 1


class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_superuser')
    inlines = (UserInline, )

    def save_model(self, request, obj, form, change):

        obj.user = request.user
        super().save_model(request, obj, form, change)
        try:
            a = User_T.objects.filter(user=obj)
            Notification(
                user=a[0], Notification="Your details have been updated.").save()
        except:
            pass


class CourseInline(admin.StackedInline):
    model = Course
    extra = 0


class RoomInline(admin.StackedInline):
    model = Room
    extra = 0


class ExamInline(admin.StackedInline):
    model = Exam
    extra = 0


class RoomAdmin(admin.ModelAdmin):
    model = Room
    extra = 0


class ExamAllocationInline(admin.TabularInline):
    model = ExamAllocation
    extra = 0


class ExamAdmin(admin.ModelAdmin):
    model = Exam
    extra = 0


class RoomAllocationInline(admin.StackedInline):
    model = RoomAllocation
    extra = 0


class AssignDutyInline(admin.TabularInline):
    model = AssignDuty
    extra = 0


class TakeDutyInline(admin.TabularInline):
    model = TakeDuty
    extra = 0


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Room)
admin.site.register(Exam)
admin.site.register(RoomAllocation)
admin.site.register(TakeDuty)
admin.site.register(AssignDuty)
admin.site.register(ExamAllocation)
admin.site.register(Course)
admin.site.register(Notification)
