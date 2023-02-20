# article/serializers.py

from rest_framework import serializers

from comment.serializers import CommentSerializer
from user_info.serializers import UserDescSerializer
from .models import Article, Category, Tag, Avatar

class AvatarSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='avatar-detail')

    class Meta:
        model = Avatar
        fields = '__all__'

"""关于分类的序列化器"""
class CategorySerializer(serializers.ModelSerializer):
    """分类的序列化器"""
    url = serializers.HyperlinkedIdentityField(view_name='category-detail')

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['created']


"""上面的分类接口中，希望分类的列表页面不显示其链接的文章以保持数据清爽，但是详情页面则展示出链接的所有文章，方便接口的使用。
因此就需要同一个视图集用到两个不同的序列化器了，即前面章节讲的覆写 get_serializer_class() """
class ArticleCategoryDetailSerializer(serializers.ModelSerializer):
    """给分类详情用的嵌套序列化器"""
    url = serializers.HyperlinkedIdentityField(view_name='article-detail')

    class Meta:
        model = Article
        fields = [
            'url',
            'title',
        ]

class CategoryDetailSerializer(serializers.ModelSerializer):
    """分类详情"""
    articles = ArticleCategoryDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'title',
            'created',
            'articles',
        ]


"""关于文章标签的序列化器"""
class TagSerializer(serializers.ModelSerializer):
    """因为标签仅有 text 字段是有用的，两个 id 不同但是 text 相同的标签没有任何意义。更重要的是，SlugRelatedField
    是不允许有重复的 slug_field 。因此还需要覆写 TagSerializer 的 create()/update() 方法："""

    def check_tag_obj_exists(self, validated_data):
        text = validated_data.get('text')
        if Tag.objects.filter(text=text).exists():
            raise serializers.ValidationError('Tag with text {} exists.'.format(text))

    def create(self, validated_data):
        self.check_tag_obj_exists(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.check_tag_obj_exists(validated_data)
        return super().update(instance, validated_data)

    class Meta:
        model = Tag
        fields = '__all__'




"""第一次写文章列表的序列化器"""
class ArticleListSerializer(serializers.ModelSerializer):
    # read_only 参数设置为只读
    author = UserDescSerializer(read_only=True)
    # category 的嵌套序列化字段
    category = CategorySerializer(read_only=True)
    # category 的 id 字段，用于创建/更新 category 外键
    category_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
        slug_field='text'  # 直接显示其 text 字段的内容就足够了
    )
    #  json 数据中直接提供超链接到每篇文章的 url，前端用起来就方便
    #  view_name 是路由的名称，也就是在 path(... name='xxx') 里的那个 name
    #  url = serializers.HyperlinkedIdentityField(view_name="article:detail")

    class Meta:
        model = Article
        fields = ['id', 'url', 'title', 'created', 'author', 'tags', 'category']

        #防止用户手动传入一个错误的 author，将其加入到只读字段中,在接收 POST 请求时，序列化器就不再理会请求中附带的 author 数据了
        # 嵌套序列化器已经设置了只读，所以这个就不要了
        # read_only_fields = ['author']




"""第二次写一个 提供给视图集的新序列化器 """
class ArticleBaseSerializer(serializers.HyperlinkedModelSerializer):
    """# 将已有的 ArticleSerializer 里的东西全部挪到这个 ArticleBaseSerializer 里来除了 Meta 类保留"""
    id = serializers.IntegerField(read_only=True)
    author = UserDescSerializer(read_only=True)
    # category 的嵌套序列化字段
    category = CategorySerializer(read_only=True)
    # category 的 id 字段，用于创建/更新 category 外键
    category_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    # tag 字段
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
        slug_field='text'   # 直接显示其 text 字段的内容就足够了
    )

    # 图片字段
    avatar = AvatarSerializer(read_only=True)
    avatar_id = serializers.IntegerField(
        write_only=True,
        allow_null=True,
        required=False
    )
    # 自定义错误信息
    default_error_messages = {
        'incorrect_avatar_id': 'Avatar with id {value} not exists.',
        'incorrect_category_id': 'Category with id {value} not exists.',
        'default': 'No more message here..'
    }

    def check_obj_exists_or_fail(self, model, value, message='default'):
        if not self.default_error_messages.get(message, None):
            message = 'default'

        if not model.objects.filter(id=value).exists() and value is not None:
            self.fail(message, value=value)

    def validate_avatar_id(self, value):
        self.check_obj_exists_or_fail(
            model=Avatar,
            value=value,
            message='incorrect_avatar_id'
        )

        return value

    def validate_category_id(self, value):
        self.check_obj_exists_or_fail(
            model=Category,
            value=value,
            message='incorrect_category_id'
        )

        return value
    #
    # # category_id 字段的验证器
    # def validate_category_id(self, value):
    #     if not Category.objects.filter(id=value).exists() and value is not None:
    #         raise serializers.ValidationError("Category with id {} not exists.".format(value))
    #     return value
    #
    # # DRF 对图片的处理进行了封装，通常不需要你关心实现的细节，只需要像其他 Json 接口一样写序列化器就可以了。
    # # 图片上传完成后，会将其 id、url 等信息返回到前端，前端将图片的信息以嵌套结构表示到文章接口中，并在适当的时候将其链接到文章数据中
    # def validate_avatar_values(self, value):
    #     if not Avatar.objects.filter(id=value).exists() and value is not None:
    #         raise serializers.ValidationError("Avatar with id {} not exists.".format(value))
    #
    #     return value

    # 覆写方法，如果输入的标签不存在则创建它
    def to_internal_value(self, data):
        tags_data = data.get('tags')

        if isinstance(tags_data, list):
            for text in tags_data:
                if not Tag.objects.filter(text=text).exists():
                    Tag.objects.create(text=text)

        return super().to_internal_value(data)

    class Meta:
        model = Article
        fields = '__all__'




# 序列化器继承的 HyperlinkedModelSerializer 基本上与之前用的 ModelSerializer 差不多，
# 区别是它自动提供了外键字段的超链接，并且默认不包含模型对象的 id 字段。
class ArticleSerializer(ArticleBaseSerializer):
    """# 保留 Meta 类 将父类改为 ArticleBaseSerializer"""
    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {'body': {'write_only': True}}



"""继承的父类是 ArticleBaseSerializer"""
class ArticleDetailSerializer(ArticleBaseSerializer):
    # 渲染后的正文
    body_html = serializers.SerializerMethodField()
    # 渲染后的目录
    toc_html = serializers.SerializerMethodField()
    # 让评论通过文章接口显示出来
    id = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    def get_body_html(self, obj):
        return obj.get_md()[0]

    def get_toc_html(self, obj):
        return obj.get_md()[1]

    class Meta:
        model = Article
        fields = '__all__'


