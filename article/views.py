# article/views.py

from django.http import JsonResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, generics, viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from article.models import Article, Category, Tag, Avatar
from article.permissions import IsAdminUserOrReadOnly
# 这个 ArticleListSerializer 暂时还没有
from article.serializers import ArticleListSerializer, ArticleDetailSerializer, CategorySerializer, \
    CategoryDetailSerializer, TagSerializer, AvatarSerializer
from article.serializers import ArticleSerializer

"""第一次写文章列表接口函数"""
# def article_list(request):
#     articles = Article.objects.all()
#     serializer = ArticleListSerializer(articles, many=True)
#     return JsonResponse(serializer.data, safe=False)

"""第二次写文章列表接口函数"""
# @api_view(['GET', 'POST'])
# def article_list(request):
#     if request.method == 'GET':
#         articles = Article.objects.all()
#         serializer = ArticleListSerializer(articles, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         serializer = ArticleListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""第三次写文章列表接口函数"""
# class ArticleList(generics.ListCreateAPIView):
#     queryset = Article.objects.all()
#     serializer_class = ArticleListSerializer
#     # 自定义权限控制类, 只准许管理员可以发布文章，其他人可以get操作
#     # permission_classes = [IsAdminUser]
#     permission_classes = [ IsAdminUserOrReadOnly ]
#
#     def perform_create(self, serializer):
#         # 从 Request 中提取用户信息，并把额外的用户信息注入到已有的数据中
#         serializer.save(author=self.request.user)


"""第一个文章详情视图函数"""
# class ArticleDetail(APIView):
#     """文章详情视图"""
#
#     def get_object(self, pk):
#         """获取单个文章对象"""
#         try:
#             # pk 即主键，默认状态下就是 id
#             return Article.objects.get(pk=pk)
#         except:
#             raise Http404
#
#     def get(self, request, pk):
#         article = self.get_object(pk)
#         serializer = ArticleDetailSerializer(article)
#         # 返回 Json 数据
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         article = self.get_object(pk)
#         serializer = ArticleDetailSerializer(article, data=request.data)
#         # 验证提交的数据是否合法
#         # 不合法则返回400
#         if serializer.is_valid():
#             # 序列化器将持有的数据反序列化后，
#             # 保存到数据库中
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         article = self.get_object(pk)
#         article.delete()
#         # 删除成功后返回204
#         return Response(status=status.HTTP_204_NO_CONTENT)

"""第二个文章详情视图"""
# class ArticleDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,generics.GenericAPIView):
#     """文章详情视图"""
#     queryset = Article.objects.all()
#     serializer_class = ArticleDetailSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)

"""第三个文章详情视图"""
# class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Article.objects.all()
#     serializer_class = ArticleDetailSerializer
#
#     # 自定义权限控制类, 只准许管理员可以发布文章
#     # permission_classes = [IsAdminUser]
#     permission_classes = [IsAdminUserOrReadOnly]

"""最后用视图集来写文章列表和文章详情的接口集成在一起，并提供了默认的增删改查"""
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    # django-filter 吗，这就是用于过滤的轮子,可以将其单独配置在特定的视图中,,实现单纯的完全匹配
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['author__username', 'title']

    # 如果要实现更常用的模糊匹配，就可以使用 SearchFilter 做搜索后端：
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # 虽然视图集默认只提供一个序列化器，但是通过覆写 get_serializer_class() 方法可以根据条件而访问不同的序列化器：
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleSerializer
        else:
            return ArticleDetailSerializer

    # 有些时候用户需要某个特定范围的文章（比如搜索功能），这时候后端需要把返回的数据进行过滤。
    def get_queryset(self):
        queryset = self.queryset
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(author__username=username)

        return queryset




"""分类视图集"""
class CategoryViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    # 由于博客文章的分类、标签通常不会太多，因此对这两个接口，为了方便起见我并不想翻页而是希望一次请求直接返回所有的数据。
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return CategorySerializer
        else:
            return CategoryDetailSerializer


class TagViewSet(viewsets.ModelViewSet):
    """标签视图集"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    # 由于博客文章的分类、标签通常不会太多，因此对这两个接口，为了方便起见我并不想翻页而是希望一次请求直接返回所有的数据。
    pagination_class = None

class AvatarViewSet(viewsets.ModelViewSet):
    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = [IsAdminUserOrReadOnly]