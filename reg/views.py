# views.py
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import CourseScheduleSerializer, CourseSerializer, RegisterSerializer,LoginSerializer,StudentSerializer,CourseSerializerTow
from django.contrib.auth.models import User
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from .permissions import IsSuperUser  
from .models import Course, StudentRegistration, Student,CourseSchedule
from django.utils import timezone
from datetime import timedelta

#اضافة مواعيد 
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperUser])
def add_course_schedule(request):
    serializer = CourseScheduleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#اضافة كورسات جديدة
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperUser])
def add_course(request):
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#جلب كل المواعيد
@api_view(['GET'])
def get_all_course_schedules(request):
    schedules = CourseSchedule.objects.all()
    serializer = CourseScheduleSerializer(schedules, many=True)
    return Response(serializer.data)



#جلب كل الكورسات
@api_view(['GET'])
def get_all_courses(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses,many=True)
    return Response(serializer.data)

#جلب كورس معين


@api_view(['GET'])
def get_course_by_id(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    course_serializer = CourseSerializerTow(course)
    
    
    registered_students = StudentRegistration.objects.filter(courseId=course).select_related('studentId__user')
    students = [registration.studentId for registration in registered_students]
    
    student_serializer = StudentSerializer(students, many=True)
    
    response_data = {
        'course': course_serializer.data,
        'registered_students': student_serializer.data,
        'total_registered_students': len(students)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


#تسجيل طالب جديد
class Register(APIView):
    @permission_classes([AllowAny])
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            response_data = {
                'token': token.key,
                'userId': user.id,
                'is_superuser': user.is_superuser
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#تسجيل الدخول سواء طالب او ادمن
class Login(APIView):
    @permission_classes([AllowAny])
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username, 'is_superuser': user.is_superuser, "userId": user.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#البحث عن كورس معين من خلال الكود او اسم المدرب او اسم الكورس
@api_view(['GET'])
def search_courses(request):
    query = request.query_params.get('query', '')
    if query:
        courses = Course.objects.filter(
            Q(code__icontains=query) | 
            Q(name__icontains=query) | 
            Q(instructor__icontains=query)
        )
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    else:
        return Response({"error": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)


#تسجيل خروج

@api_view(['POST'])
def logout(request):
    try:
        token = request.auth
        if token:
            token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No token found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#تسجيل كورس للطالب مع مراعات القيود المفروضة :1-ان يكون طالب--2-ان يكون قد قام بتسجيل الدخول--3-ان يكون انهى المتطلبات--4-ان يكون موعد الكورس لا يتضارب مع موعد كورس اخر--5-ان يكون لم يثم بتسجيل الكورس من قبل
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_course_for_student(request):
    user = request.user
    if user.is_superuser:
        return Response({'error': 'Superuser cannot register for courses.'}, status=status.HTTP_403_FORBIDDEN)

    course_id = request.data.get('course_id')
    student_id = request.data.get('student_id')

    # تحقق من وجود الطالب ومطابقة الاي دي 
    try:
        student = Student.objects.get(user_id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    if student.user_id != user.id:
        return Response({'error': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    # تحقق من وجود الكورس
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

    # تحقق مما إذا كان الكورس مسجل 
    if StudentRegistration.objects.filter(studentId=student, courseId=course).exists():
        return Response({'error': 'Course already registered.'}, status=status.HTTP_409_CONFLICT)

    # تحقق من انهاء المتطلبات السابقة
    prerequisites = course.prerequisites.all()
    completed_courses_ids = StudentRegistration.objects.filter(studentId=student).values_list('courseId_id', flat=True)#كورسات الطالب
    completed_courses = Course.objects.filter(id__in=completed_courses_ids)
    if not all(prerequisite in completed_courses for prerequisite in prerequisites):
        return Response({'error': 'Prerequisites not met.'}, status=status.HTTP_400_BAD_REQUEST)

    # تحقق من تضارب المواعيد
    existing_schedules = CourseSchedule.objects.filter(course__studentregistration__studentId=student)#كل الماعيد الي مسجلها
    new_course_schedule = course.scheduleId
    for schedule in existing_schedules:
        if (new_course_schedule.days == schedule.days and
            not (new_course_schedule.endTime <= schedule.startTime or new_course_schedule.startTime >= schedule.endTime)):
            return Response({'error': 'Schedule conflict.'}, status=status.HTTP_409_CONFLICT)

    # تسجيل الكورس
    StudentRegistration.objects.create(studentId=student, courseId=course)
    return Response({'message': 'Course registered successfully.'}, status=status.HTTP_201_CREATED)

#جلب الكورسات التي سجلها الطالب
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_courses(request):
    user = request.user

    # تحقق مما إذا كان المستخدم طالبا
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    # جلب الكورسات المسجلة
    student_courses = StudentRegistration.objects.filter(studentId=student).select_related('courseId')
    courses = [registration.courseId for registration in student_courses]

    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#جلب فقط الكورسات التي انهى الطالب متطلباتها


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses_with_completed_prerequisites(request):
    user = request.user

    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    registered_course_ids = StudentRegistration.objects.filter(studentId=student).values_list('courseId', flat=True)

    all_courses = Course.objects.exclude(id__in=registered_course_ids)

    eligible_courses = []
    for course in all_courses:
        prerequisites = course.prerequisites.all()
        if all(prerequisite.id in registered_course_ids for prerequisite in prerequisites):
            eligible_courses.append(course)

    serializer = CourseSerializer(eligible_courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
@api_view(['GET'])
def get_recent_courses(request):
    ten_days_ago = timezone.now() - timedelta(days=10)
    recent_courses = Course.objects.filter(created_at__gte=ten_days_ago)
    
    notifications = [
        f"A new course called {course.name} has been launched " for course in recent_courses
    ]
    
    return Response(notifications, status=status.HTTP_200_OK)
