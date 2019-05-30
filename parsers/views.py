from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from parsers.models import ParseSession
from parsers.serializers import ParseSessionSerializer
from parsers.previews import performers


class ParseView(APIView):
    permission_classes = (IsAdminUser, )

    def post(self, mode):
        parser_module = getattr(performers, mode)

        return Response(parser_module.run.delay())


class ParseSessionViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = ParseSessionSerializer

    queryset = ParseSession.objects.all()
