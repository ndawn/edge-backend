from dateutil import parser

from parsers.models import ParseSession, Site, ParsedObject
from parsers.serializers import ParseSessionSerializer, SiteSerializer
from parsers.previews.performers import previewsworld

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


PERFORMER_MODULES = {
    'previewsworld.com': previewsworld,
}


class SiteViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdminUser, )
    serializer_class = SiteSerializer

    queryset = Site.objects.all()


class ParseView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser, )

    def post(self, request):
        host = Site.objects.get(pk=request.data.get('site_id')).address

        parser_module = PERFORMER_MODULES.get(host)

        if parser_module is None:
            return Response({'error': 'Модуль загрузки с выбранного сайта не обнаружен'})

        catalog_date = request.data.get('catalog_date')

        if type(catalog_date) is str:
            catalog_date = parser.parse(catalog_date)

        try:
            return Response(parser_module.Performer.run(
                catalog_date=catalog_date,
                publisher_ids=request.data.get('publisher_ids'),
                category_ids=request.data.get('category_ids'),
            ))
        except LookupError:
            return Response(
                {'error': 'Страница не найдена. Возможно, предзаказов по выбранной дате не существует'},
                status=HTTP_404_NOT_FOUND,
            )


class ParseSessionViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdminUser, )
    serializer_class = ParseSessionSerializer

    queryset = ParseSession.objects.all()

    filterset_fields = ('status',)

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        session = self.get_object()

        if session.ready():
            return Response({'progress': session.item_count})

        return Response({'progress': ParsedObject.objects.filter(session_id=pk).count()})

    # TODO
    # @action(detail=True, methods=['get'])
    # def publishers(self, request, pk=None):
    #     session = self.get_object()
    #
    #     if not session.ready():
    #         return Response(
    #             {'error': 'Сессия еще активна'},
    #             status=HTTP_400_BAD_REQUEST,
    #         )
    #
    #     queryset = ParsedObject.objects.filter(session_id=session.id).select_related('task')
    #
    #     return Response({'publishers': })
    #
    # @action(detail=True, methods=['get'])
    # def categories(self, request, pk=None):
    #     session = self.get_object()
    #
    #     if not session.ready():
    #         return Response({'progress': session.item_count})
    #
    #     return Response({'progress': ParsedObject.objects.filter(session_id=pk).count()})
