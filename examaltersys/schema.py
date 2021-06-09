import graphene
from graphene_django.registry import Registry
from graphene.relay import Node
from graphene import ObjectType, Connection, Node, Int
from examaltersys.models import FacultyCount, TakeDutyCount, Exam, User_T, ExamAllocation, Room, AssignDuty, TakeDuty, Course, RoomAllocation, Notification, NotificationCount
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth.models import User
import graphql_jwt
from django_graphene_permissions import permissions_checker
from django_graphene_permissions.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from graphene import Time
import datetime
from django.contrib.auth import get_user_model


class ExtendedConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_edge_count(root, info, **kwargs):
        return len(root.edges)


graphene.relay.Connection = ExtendedConnection


class CourseType(DjangoObjectType):
    class Meta:
        model = Course


class ExamAllocationType(DjangoObjectType):
    class Meta:
        model = ExamAllocation


class ExamType(DjangoObjectType):
    class Meta:
        model = Exam


class UserType(DjangoObjectType):
    class Meta:
        model = User


class UsertType(DjangoObjectType):
    class Meta:
        model = User_T


class FacultyCountType(DjangoObjectType):
    class Meta:
        model = FacultyCount
        fields = ['id']
        filter_fields = {
            'id':  ['exact', 'icontains'],
        }
        interfaces = (graphene.relay.Node, )
        connection_class = ExtendedConnection


class RoomType(DjangoObjectType):
    class Meta:
        model = Room


class RoomCountType(DjangoObjectType):
    class Meta:
        model = Room
        filter_fields = {
            'id':  ['exact', 'icontains'],
        }
        interfaces = (graphene.relay.Node, )
        connection_class = ExtendedConnection


class AssignDutyType(DjangoObjectType):
    class Meta:
        model = AssignDuty


class TakeDutyType(DjangoObjectType):
    class Meta:
        model = TakeDuty


class TakeDutyCountType(DjangoObjectType):
    class Meta:
        model = TakeDutyCount
        filter_fields = {
            'id':  ['exact', 'icontains'],
        }
        interfaces = (graphene.relay.Node, )
        connection_class = ExtendedConnection


class RoomAllocationType(DjangoObjectType):
    class Meta:
        model = RoomAllocation


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification


class NotificationCountType(DjangoObjectType):
    class Meta:
        model = NotificationCount
        filter_fields = {
            'id':  ['exact', 'icontains'],
        }
        interfaces = (graphene.relay.Node, )
        connection_class = ExtendedConnection


class Query(ObjectType):
    me = graphene.Field(UserType)
    usert = graphene.Field(UsertType, id=graphene.Int())
    exam = graphene.Field(ExamType, id=graphene.Int())
    user = graphene.Field(UserType, id=graphene.Int())
    room = graphene.Field(RoomType, id=graphene.Int())
    notification = graphene.Field(NotificationType, id=graphene.Int())
    exam_allocation = graphene.Field(ExamAllocationType, id=graphene.Int())
    assignduty = graphene.Field(AssignDutyType, id=graphene.Int())
    takeduty = graphene.Field(TakeDutyType, id=graphene.Int())
    course = graphene.Field(CourseType, id=graphene.Int())
    room_allocation = graphene.Field(ExamAllocationType, id=graphene.Int())
    exam_allocations = graphene.List(ExamAllocationType)
    room_allocations = graphene.List(RoomAllocationType)
    users = graphene.List(UserType)
    userts = graphene.List(UsertType)
    courses = graphene.List(CourseType)
    notifications = graphene.List(NotificationType)
    facultiescount = DjangoFilterConnectionField(FacultyCountType)
    exams = graphene.List(ExamType)
    rooms = graphene.List(RoomType)
    roomscount = DjangoFilterConnectionField(RoomCountType)
    assignduties = graphene.List(AssignDutyType)
    takeduties = graphene.List(TakeDutyType)
    takerscount = DjangoFilterConnectionField(TakeDutyCountType)
    notfscount = DjangoFilterConnectionField(NotificationCountType)

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        return user

    def resolve_faculties(self, info):
        users = User_T.objects.filter(type='faculty')
        return users

    def resolve_rooms(self, info):
        rooms = Room.objects.all()
        return rooms

    def resolve_exams(self, info):
        exams = Exam.objects.all()
        return exams

    def resolve_duties(self, info, **kwargs):
        take_duty = ExamAllocation.objects.filter(username='faculty')
        return take_duty

    def resolve_exam_allocations(self, info):
        exam_allocations = ExamAllocation.objects.all()
        return exam_allocations

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_userts(self, info):
        userts = User_T.objects.filter()
        return userts

    def resolve_notifications(self, info):
        notifications = Notification.objects.all()
        return notifications


class ExamInput(graphene.InputObjectType):
    exam_name = graphene.String()
    day = graphene.String()
    course_name = graphene.String()
    date = graphene.types.datetime.Date()
    start_time = graphene.types.datetime.Time()
    end_time = graphene.types.datetime.Time()
    duration = Time(required=True, time_input=Time(required=True))
    slot = graphene.String()


class NotificationInput(graphene.InputObjectType):
    notification = graphene.String()
    username = graphene.String()


class TakeDutyInput(graphene.InputObjectType):
    exam_id = graphene.Int()
    faculty_name = graphene.String()

# 1


class AssignDuty(graphene.Mutation):
    ok = graphene.Boolean()
    takeduty = graphene.Field(TakeDutyType)

    @ staticmethod
    @permissions_checker([IsAuthenticated])
    def mutate(root, info, input):
        ok = True
        takeduty_instance = TakeDuty(faculty=graphene.Field(
            UserType, faculty_name=input.faculty_name, id=graphene.Int()), exam=graphene.Field(
            ExamType, faculty_name=input.faculty_name, id=graphene.Int()))
        takeduty_instance.save()
        return AssignDuty(ok=ok, takeduty=takeduty_instance)

# 2


class DeleteDuty(graphene.Mutation):
    ok = graphene.Boolean()
    deleteduty = graphene.Field(TakeDutyType)

    @ staticmethod
    @ permissions_checker([IsAuthenticated])
    def mutate(self, info, id):
        ok = False
        deleteduty = Exam.objects.get(pk=id)
        if deleteduty is not None:
            ok = True
            deleteduty.delete()
        return DeleteDuty(ok=ok, deleteduty=deleteduty)

# 3


class CreateExam(graphene.Mutation):
    class Arguments:
        input = ExamInput(required=True)

    ok = graphene.Boolean()
    exam = graphene.Field(ExamType)

    @ staticmethod
    @permissions_checker([IsAuthenticated])
    def mutate(root, info, input):
        ok = True
        exam_instance = Exam(exam_name=input.exam_name, day=input.day, course_name=input.course_name, date=input.date,
                             start_time=input.start_time,
                             end_time=input.end_time,
                             duration=input.duration,
                             slot=input.slot)
        exam_instance.save()
        return CreateExam(ok=ok, exam=exam_instance)

# 4


class CreateNotification(graphene.Mutation):
    notification = graphene.String()
    ok = graphene.Boolean()
    username = graphene.String()

    class Arguments:
        input = NotificationInput(required=True)

    @ staticmethod
    @permissions_checker([IsAuthenticated])
    def mutate(self, info, input):
        ok = True
        notf_instance = Notification(user=graphene.Field(
            UserType, username=input.username, id=graphene.Int()), notification=input.notification)
        notf_instance.save()
        return CreateNotification(ok=ok, exam=notf_instance)

# 5


class DeleteNotification(graphene.Mutation):
    notification = graphene.Field(NotificationType)
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @ staticmethod
    @ permissions_checker([IsAuthenticated])
    def mutate(self, info, id):
        ok = False
        notification = Exam.objects.get(pk=id)
        if notification is not None:
            ok = True
            notification.delete()
        return DeleteNotification(ok=ok, notification=notification)

# 6


class DeleteExam(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    exam = graphene.Field(ExamType)
    ok = graphene.Boolean()

    @ staticmethod
    @ permissions_checker([IsAuthenticated])
    def mutate(self, info, id):
        ok = False
        exam = Exam.objects.get(pk=id)
        if exam is not None:
            ok = True
            exam.delete()
        return DeleteExam(exam=exam)

# 7


class UpdateExam(graphene.Mutation):
    ok = graphene.Boolean()
    exam = graphene.Field(ExamType)

    class Arguments:
        exam_data = ExamInput(required=True)

    @ staticmethod
    @ permissions_checker([IsAuthenticated])
    def mutate(self, info, exam_data=None, user_data=None):
        exam_instance = Exam.objects.filter(
            exam_name=input.exam_name, date=input.date, start_time=input.start_time, end_time=input.end_time)
        if(exam_instance):
            ok = True
            exam_instance.update(exam_name=input.exam_name, day=input.day, course_name=input.course_name, date=input.date,
                                 start_time=input.start_time,
                                 end_time=input.end_time,
                                 duration=input.duration,
                                 slot=input.slot)
            exam_instance = exam_instance[0]
            exam_instance.save()
            return UpdateExam(ok=ok, exam=exam_instance)

# 8


class UpdateRoom(graphene.Mutation):
    ok = graphene.Boolean()
    room = graphene.Field(ExamType)

    class Arguments:
        room_data = ExamInput(required=True)

    @ staticmethod
    @ permissions_checker([IsAuthenticated])
    def mutate(self, info, room_data=None, user_data=None):
        room_instance = Exam.objects.filter(
            room_name=input.exam_name, date=input.date, start_time=input.start_time, end_time=input.end_time)
        if(room_instance):
            ok = True
            room_instance.update(
                Room_ID=room_data.Room_ID, Block=room_data.Block, Capacity=room_data.Capacity)
            room_instance.save()
            return UpdateExam(ok=ok, exam=room_instance)


class Mutation(graphene.ObjectType):
    create_exam = CreateExam.Field()
    update_exam = UpdateExam.Field()
    update_room = UpdateRoom.Field()
    delete_exam = DeleteExam.Field()
    del_notification = DeleteNotification.Field()
    assign_duty = AssignDuty.Field()
    delete_duty = DeleteDuty.Field()
    create_notification = CreateNotification.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
